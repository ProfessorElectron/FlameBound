"""Stateless assistant API contract with bounded untrusted conversation context."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.version import API_SCHEMA_VERSION


class AssistantRequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ConversationMessage(AssistantRequestModel):
    role: Literal["user", "assistant"]
    content: Annotated[str, Field(min_length=1, max_length=2000)]


class AssistantChatRequest(AssistantRequestModel):
    question: Annotated[str, Field(min_length=1, max_length=2000)]
    history: Annotated[list[ConversationMessage], Field(max_length=8)] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_context_budget(self) -> "AssistantChatRequest":
        if sum(len(message.content) for message in self.history) > 8000:
            raise ValueError("Conversation history exceeds the total character limit")
        if not self.question.strip():
            raise ValueError("Question must not be blank")
        return self


class AssistantCitation(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    citation_id: str
    source_id: str
    title: str
    source_uri: str
    page: int
    location_label: str | None = None
    content_hash: str
    review_status: Literal["unreviewed", "reviewed"]
    publication_date: str
    document_type: str


class AssistantChatResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    status: Literal["answered", "insufficient_evidence", "clarification", "unsupported"]
    api_schema_version: Literal[API_SCHEMA_VERSION] = API_SCHEMA_VERSION
    explanation: str
    bases: list[Literal[
        "general_background", "retrieved_unreviewed", "reviewed_evidence",
        "deterministic_calculation", "unsupported",
    ]]
    citations: list[AssistantCitation] = Field(default_factory=list)
    calculation: dict[str, object] | None = None
