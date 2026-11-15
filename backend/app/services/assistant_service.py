"""Stateless assistant orchestration, evidence boundary, and one-tool policy."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from ai.config import AISettings, ProviderError
from ai.index import SQLiteDocumentIndex
from ai.local_corpus import local_psi_corpus
from ai.llm.ollama_client import OllamaClient
from ai.rag.pipeline import FINAL_RESPONSE_SCHEMA, SYSTEM_PROMPT, evidence_payload
from ai.retrieval.service import RetrievalService, load_calibrated_threshold, validate_citations
from ai.tools import AtmosphericToolRegistry, MissingToolInputs, ToolRejected
from backend.app.schemas.assistant import AssistantChatRequest, AssistantChatResponse
from backend.app.services.atmospheric_service import CalculationOutOfRangeError


_UNSUPPORTED_PATTERNS = re.compile(
    r"\b(safe|safety|certif(y|ication)|operational guidance|hazard assessment|"
    r"will (it|this) (burn|ignite|spread)|can (it|this) (ignite|spread)|"
    r"predict(ion)? .{0,60}(fire|flame|spread|burn|ignit)|"
    r"forecast.{0,30}(fire|flame|burn|spread)|"
    r"guarantee.*(safe|fire)|evacuat)\b", re.IGNORECASE,
)
_PROJECT_PATTERNS = re.compile(
    r"\b(nasa|psi[- ]?\d+|saffire|bass[- ]?\w*|experiment(al)?|test matrix|"
    r"measured|measurement|dataset|documented result|reported result)\b", re.IGNORECASE,
)
_CALCULATION_PATTERNS = re.compile(
    r"\b(p\s*o\s*2|partial pressure|compare.{0,40}(atmosphere|condition)|"
    r"atmosphere.{0,30}compare)\b", re.IGNORECASE,
)
_CONCEPTUAL_QUESTION_PATTERNS = re.compile(
    r"\b(?:what\s+does\b.{0,120}\bmean\b|what\s+is\b.{0,100}\b(?:oxygen\s+)?partial\s+pressure\b|"
    r"(?:explain|define)\b)", re.IGNORECASE,
)
_GREETING_PATTERN = re.compile(r"^(?:hi|hello|hey|good\s+(?:morning|afternoon|evening))[!.?,\s]*$", re.IGNORECASE)
_CAPABILITY_PATTERN = re.compile(
    r"\b(?:what|which)\b.{0,35}\b(?:ask|questions?|help|do)\b|\bwhat\s+else\s+can\s+i\s+ask\b",
    re.IGNORECASE,
)
_INTERNAL_NARRATION_PATTERN = re.compile(
    r"^\s*(?:the user's message|the user asked|the user just|to provide helpful information|"
    r"i need to know what|i will provide|i should|the assistant should)\b", re.IGNORECASE,
)
_NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
_UNIT = r"Pa|kPa|bar|atm|psi"


def _retrieval_for(settings: AISettings, provider: OllamaClient) -> RetrievalService | None:
    db_path = settings.database_path
    root = Path(__file__).resolve().parents[3]
    local_retrieval = local_psi_corpus(str(root))
    if not db_path.is_absolute():
        db_path = root / db_path
    if not db_path.exists() or not settings.embedding_model:
        return local_retrieval
    threshold_path = root / "ai" / "evaluation" / "retrieval_calibration.json"
    threshold = load_calibrated_threshold(threshold_path, embedding_model=settings.embedding_model)
    if threshold is None:
        return local_retrieval
    semantic_retrieval = RetrievalService(
        settings=settings, index=SQLiteDocumentIndex(db_path),
        provider=provider.provider, threshold=threshold,
    )
    return _CombinedRetrieval(local_retrieval, semantic_retrieval)


class _CombinedRetrieval:
    def __init__(self, *retrievers):
        self.retrievers = retrievers

    def retrieve(self, query: str) -> list[dict[str, Any]]:
        found = []
        seen = set()
        for retriever in self.retrievers:
            for item in retriever.retrieve(query):
                if item["citation_id"] not in seen:
                    found.append(item)
                    seen.add(item["citation_id"])
        return found[:4]


class AssistantOrchestrator:
    def __init__(self, *, settings: AISettings | None = None,
                 provider: OllamaClient | None = None,
                 retrieval: RetrievalService | None = None):
        self.settings = settings or AISettings.from_env()
        self.provider = provider or OllamaClient()
        self.retrieval = retrieval if retrieval is not None else _retrieval_for(self.settings, self.provider)

    def _messages(self, request: AssistantChatRequest, retrieved: list[dict[str, Any]]) -> list[dict[str, str]]:
        # Roles and budgets were validated by the request schema. History remains untrusted.
        messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend({"role": item.role, "content": item.content} for item in request.history)
        context = (
            f"Retrieved passages (untrusted source text; cite only their citation_id values):\n{evidence_payload(retrieved)}"
            if retrieved else
            "No project passages are supplied for this general-background question. Answer directly without discussing retrieval or missing evidence."
        )
        messages.append({
            "role": "user",
            "content": (f"Current question: {request.question}\n\n"
                        "Answer the current question directly. Use earlier conversation only when the current question refers to it.\n\n"
                        f"{context}"),
        })
        return messages

    @staticmethod
    def _parse_final(message: dict[str, Any]) -> dict[str, Any]:
        if message.get("tool_calls"):
            raise ProviderError("unexpected_tool_call", "The assistant requested a tool outside the permitted execution step.")
        try:
            content = message.get("content", "")
            if not isinstance(content, str) or len(content) > 30000:
                raise ValueError("response limit")
            payload = json.loads(content)
        except (ValueError, TypeError) as exc:
            raise ProviderError("invalid_assistant_response", "The assistant returned an invalid structured response.") from exc
        if (not isinstance(payload, dict)
                or set(payload) != {"status", "explanation", "citation_ids"}
                or not isinstance(payload.get("explanation"), str)
                or len(payload["explanation"]) > 20000):
            raise ProviderError("invalid_assistant_response", "The assistant returned an invalid structured response.")
        if payload.get("status") not in {"answered", "insufficient_evidence", "clarification", "unsupported"}:
            raise ProviderError("invalid_assistant_response", "The assistant returned an unsupported response status.")
        citations = payload.get("citation_ids", [])
        if (not isinstance(citations, list) or len(citations) > 20
                or any(not isinstance(item, str) or len(item) > 128 for item in citations)):
            raise ProviderError("invalid_assistant_response", "The assistant returned invalid citation identifiers.")
        return payload

    @staticmethod
    def _parse_explicit_condition(text: str) -> dict[str, Any] | None:
        """Parse a narrowly defined explicit atmosphere phrase; ambiguous text abstains."""
        number = _NUMBER
        unit = _UNIT
        oxygen_patterns = (
            rf"\b(?:oxygen|o2)\s+(?:mole\s+)?fraction\s*(?:of|is|=|:)\s*({number})\s*(%)?",
            rf"\b(?:oxygen|o2)\s+(?:mole\s+)?fraction\s+({number})\s*(%)?",
            rf"\boxygen\s+({number})\s*(%)?",
            rf"\b({number})\s*(%)?\s+(?:oxygen|o2)(?:\s+mole)?\s+fraction\b",
            rf"\b({number})\s*%\s+(?:oxygen|o2)\b",
        )
        oxygen_values: list[float] = []
        for pattern in oxygen_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = float(match.group(1))
                if "%" in match.group(0):
                    value /= 100.0
                oxygen_values.append(value)
        # Overlapping grammar matches are okay only if they state the same value.
        unique_oxygen = list(dict.fromkeys(oxygen_values))
        if len(unique_oxygen) != 1:
            return None

        pressure_matches = list(re.finditer(
            rf"(?:\b(?:total\s+)?pressure\s*(?:(?:of|is)\s*|[=:]\s*)?|\bat\s+)({number})\s*({unit})\b(?:\s+(absolute|gauge))?",
            text, re.IGNORECASE,
        ))
        all_number_unit_pairs = list(re.finditer(rf"({number})\s*({unit})\b", text, re.IGNORECASE))
        if len(pressure_matches) != 1 or len(all_number_unit_pairs) != 1:
            return None
        pressure_match = pressure_matches[0]
        pressure = float(pressure_match.group(1))
        pressure_unit = pressure_match.group(2)
        basis = pressure_match.group(3)
        local_start = max(0, pressure_match.start() - 24)
        local_text = text[local_start:pressure_match.end() + 24].casefold()
        if basis is None and not re.search(r"\babsolute\s+(?:total\s+)?pressure\b", local_text):
            return None
        if basis == "gauge" or re.search(r"\bgauge\b|\b(?:not|non|without)\s+(?:an?\s+)?absolute\b|\bnon[- ]absolute\b", local_text):
            return None
        # Ensure the pressure phrase is not negated or contradicted locally.
        before_pressure = text[max(0, pressure_match.start() - 32):pressure_match.start()].casefold()
        if re.search(r"\b(?:not|isn't|isnt|wasn't|wasnt)\s+(?:an?\s+)?(?:absolute\s+)?(?:total\s+)?pressure\b", before_pressure):
            return None
        return {
            "oxygen_mole_fraction": unique_oxygen[0],
            "total_pressure": pressure,
            "pressure_unit": pressure_unit,
            "pressure_basis": "absolute",
        }

    @classmethod
    def _parse_explicit_calculation(cls, tool_name: str, question: str) -> dict[str, Any] | None:
        """Bind values to explicit fields in the current user message, never chat history."""
        if tool_name == "calculate_oxygen_partial_pressure":
            return cls._parse_explicit_condition(question)
        if tool_name != "compare_atmospheres":
            return None
        match = re.search(r"\bscenario\b(?P<scenario>.*?)\breference\b(?P<reference>.*)", question, re.IGNORECASE | re.DOTALL)
        if match:
            scenario_text, reference_text = match.group("scenario"), match.group("reference")
        else:
            ordered = re.search(
                r"\bcompare\s+(?P<scenario>(?:an?\s+)?atmosphere\b.*?)\s+with\s+(?P<reference>(?:one|an?\s+atmosphere)\b.*)",
                question, re.IGNORECASE | re.DOTALL,
            )
            if not ordered:
                return None
            scenario_text, reference_text = ordered.group("scenario"), ordered.group("reference")
        scenario = cls._parse_explicit_condition(scenario_text)
        reference = cls._parse_explicit_condition(reference_text)
        if scenario is None or reference is None:
            return None
        return {"scenario": scenario, "reference": reference}

    @staticmethod
    def _calculation_explanation(calculation: dict[str, Any]) -> str:
        """Render numeric claims exclusively from the deterministic calculation envelope."""
        outputs = calculation.get("outputs", {})
        units = calculation.get("units", {})
        if calculation.get("calculation") == "oxygen_partial_pressure":
            value = outputs.get("oxygen_partial_pressure_kpa")
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return (f"The deterministic calculation gives oxygen partial pressure as {value!r} kPa. "
                        "The supplied inputs are user-provided and unverified; see the calculation envelope for assumptions, provenance, and limitations.")
        if calculation.get("calculation") == "compare_atmospheric_conditions":
            difference = outputs.get("differences_scenario_minus_reference", {}).get("oxygen_partial_pressure_kpa")
            scenario = outputs.get("scenario", {}).get("oxygen_partial_pressure_kpa")
            reference = outputs.get("reference", {}).get("oxygen_partial_pressure_kpa")
            if all(isinstance(value, (int, float)) and not isinstance(value, bool)
                   for value in (difference, scenario, reference)):
                comparison = "higher than" if difference > 0 else "lower than" if difference < 0 else "equal to"
                return (f"The deterministic comparison gives scenario oxygen partial pressure {scenario!r} kPa and "
                        f"reference {reference!r} kPa; scenario minus reference is {difference!r} kPa, so the scenario is {comparison} the reference. "
                        "Inputs are user-provided and unverified; consult the calculation envelope for full provenance and limitations.")
        return "The deterministic calculation completed. See the authoritative calculation envelope for its outputs, units, provenance, assumptions, and limitations."

    def respond(self, request: AssistantChatRequest) -> AssistantChatResponse:
        question = request.question.strip()
        if len(question) > self.settings.max_question_chars or len(request.history) > self.settings.max_history_messages:
            raise HTTPException(status_code=422, detail={"code": "request_limit_exceeded", "field": None,
                                                         "message": "Question or conversation history exceeds configured limits."})
        if any(len(message.content) > self.settings.max_message_chars for message in request.history):
            raise HTTPException(status_code=422, detail={"code": "request_limit_exceeded", "field": "history",
                                                         "message": "A conversation message exceeds the configured limit."})
        if sum(len(message.content) for message in request.history) > self.settings.max_history_chars:
            raise HTTPException(status_code=422, detail={"code": "request_limit_exceeded", "field": "history",
                                                         "message": "Conversation history exceeds the configured total size."})
        if _GREETING_PATTERN.fullmatch(question):
            return AssistantChatResponse(
                status="answered",
                explanation="Hi! I’m FlameBound’s scientific assistant. Ask me about atmospheric science, oxygen partial pressure, or a supported calculation.",
                bases=["general_background"],
            )
        if _CAPABILITY_PATTERN.search(question):
            return AssistantChatResponse(
                status="answered",
                explanation=(
                    "You can ask me to explain atmospheric and combustion concepts; calculate oxygen partial pressure "
                    "or compare two atmospheres (include oxygen fractions, pressure units, and confirm absolute pressure); "
                    "or look up information in the local NASA PSI files. Retrieved PSI material is marked unreviewed and cited. "
                    "I cannot predict flame spread or make fire-safety decisions."
                ),
                bases=["general_background"],
            )
        if (self._is_conceptual_question(question)
                and re.search(r"\b(?:oxygen\s+)?partial\s+pressure\b|\bp\s*o\s*2\b", question, re.IGNORECASE)):
            return AssistantChatResponse(
                status="answered",
                explanation=(
                    "Oxygen partial pressure is the part of a gas mixture’s total pressure contributed by oxygen. "
                    "It depends on both the oxygen fraction and the total absolute pressure (pO₂ = oxygen mole fraction × total pressure). "
                    "It describes the oxygen present in the gas; by itself, it does not predict ignition or flame spread."
                ),
                bases=["general_background"],
            )
        if _UNSUPPORTED_PATTERNS.search(question):
            return AssistantChatResponse(
                status="unsupported", explanation="I cannot assess fire safety, certify conditions, or predict ignition or spread. FlameBound does not provide operational safety decisions.",
                bases=["unsupported"],
            )
        if re.search(r"\bmass fraction\b", question, re.IGNORECASE):
            return AssistantChatResponse(
                status="unsupported",
                explanation="Oxygen mass-fraction calculation is unavailable until a reviewed diluent record is present in the server registry.",
                bases=["unsupported"],
            )

        conceptual_question = self._is_conceptual_question(question)
        calculation_tool = None if conceptual_question else self._calculation_tool_for_question(question)
        if calculation_tool is not None:
            expected_arguments = self._parse_explicit_calculation(calculation_tool, question)
            if expected_arguments is None:
                return AssistantChatResponse(
                    status="clarification",
                    explanation="Please state each oxygen fraction and pressure with its unit, label scenario and reference values separately, and explicitly confirm absolute pressure. I cannot safely map the current wording to calculation inputs.",
                    bases=["general_background"],
                )
            registry = AtmosphericToolRegistry()
            try:
                registry.validate(calculation_tool, expected_arguments)
                calculation = registry.execute(calculation_tool, expected_arguments)
            except MissingToolInputs as exc:
                return AssistantChatResponse(
                    status="clarification", explanation=f"Please provide the missing calculation inputs: {', '.join(exc.fields)}.",
                    bases=["general_background"],
                )
            except ToolRejected as exc:
                return AssistantChatResponse(
                    status="clarification",
                    explanation="The stated calculation inputs are outside the supported scientific request schema. Please check that oxygen mole fractions are between 0 and 1 and pressures are positive absolute values in supported units.",
                    bases=["general_background"],
                )
            except CalculationOutOfRangeError as exc:
                raise HTTPException(status_code=422, detail={"code": "calculation_out_of_range", "field": None,
                                                             "message": str(exc)}) from None
            return AssistantChatResponse(
                status="answered", explanation=self._calculation_explanation(calculation),
                bases=["deterministic_calculation"], calculation=calculation,
            )

        retrieved = self.retrieval.retrieve(question) if self.retrieval else []
        if _CALCULATION_PATTERNS.search(question) and not conceptual_question:
            return AssistantChatResponse(
                status="clarification", explanation="Please provide explicit numeric values, units, scenario labels, and absolute pressure basis for the requested calculation.",
                bases=["general_background"],
            )
        if _PROJECT_PATTERNS.search(question) and not retrieved:
            return AssistantChatResponse(
                status="insufficient_evidence",
                explanation=(
                    "Project evidence retrieval is not enabled or available for this request. "
                    "I cannot present general model knowledge as retrieved FlameBound or NASA evidence, "
                    "and I do not have reviewed project citations to provide."
                ),
                bases=["unsupported"],
            )
        messages = self._messages(request, retrieved)
        final_message = self.provider.chat(messages, response_format=FINAL_RESPONSE_SCHEMA)
        answer = self._parse_final(final_message)
        if _INTERNAL_NARRATION_PATTERN.search(answer["explanation"]):
            return AssistantChatResponse(
                status="clarification",
                explanation="I couldn’t produce a clear direct answer. Please rephrase your question, and I’ll try again.",
                bases=["general_background"],
            )
        if answer["status"] == "unsupported":
            return AssistantChatResponse(status="unsupported", explanation=answer["explanation"], bases=["unsupported"])
        if answer["status"] == "clarification":
            return AssistantChatResponse(status="clarification", explanation=answer["explanation"], bases=["general_background"])
        if answer["status"] == "insufficient_evidence" or (_PROJECT_PATTERNS.search(question) and not retrieved):
            return AssistantChatResponse(
                status="insufficient_evidence",
                explanation=answer["explanation"] or "I do not have reviewed or indexed evidence for this project-specific question.",
                bases=["unsupported"],
            )
        try:
            citation_ids = answer.get("citation_ids", [])
            if not citation_ids and retrieved and _PROJECT_PATTERNS.search(question):
                citation_ids = [item["citation_id"] for item in retrieved]
            citations = validate_citations(citation_ids, retrieved)
        except ValueError:
            return AssistantChatResponse(
                status="insufficient_evidence",
                explanation="The generated response referenced evidence that was not present in this request’s retrieval results, so I cannot present it as a supported citation.",
                bases=["unsupported"],
            )
        bases: list[str] = ["general_background"]
        if citations:
            if any(item["review_status"] == "reviewed" for item in citations):
                bases.append("reviewed_evidence")
            if any(item["review_status"] == "unreviewed" for item in citations):
                bases.append("retrieved_unreviewed")
        return AssistantChatResponse(
            status="answered", explanation=answer["explanation"], bases=bases,
            citations=citations,
        )

    @staticmethod
    def _is_conceptual_question(question: str) -> bool:
        """Keep explanations and definitions out of the deterministic calculation path."""
        if not _CONCEPTUAL_QUESTION_PATTERNS.search(question):
            return False
        # An explicit calculation command still takes precedence when a user asks
        # for both a result and an explanation in one message.
        return not re.search(r"\b(?:calculate|compute|work\s+out)\b", question, re.IGNORECASE)

    @staticmethod
    def _calculation_tool_for_question(question: str) -> str | None:
        if re.search(r"\b(compare|comparison)\b", question, re.IGNORECASE) and re.search(
            r"\b(scenario|reference|atmospheres?|conditions?)\b", question, re.IGNORECASE
        ):
            return "compare_atmospheres"
        if re.search(r"\b(p\s*o\s*2|partial pressure)\b", question, re.IGNORECASE):
            return "calculate_oxygen_partial_pressure"
        return None
