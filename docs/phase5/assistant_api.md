# FlameBound Assistant API (initial backend contract)

The assistant endpoint is `POST /api/assistant/chat` and uses API schema version `1.0`. Backend requests are stateless; clients may include at most eight recent `user`/`assistant` messages. Each message and question is capped at 2,000 characters and total history at 8,000 characters. All supplied history is untrusted context.

## Request

```json
{
  "question": "Calculate oxygen partial pressure for 21% oxygen at 101.325 kPa absolute.",
  "history": []
}
```

For pO₂ and comparison requests, the server identifies the calculation intent and parses the current question using a narrow deterministic grammar. It binds every fraction/pressure/unit to its labeled field (and to scenario/reference), requires an uncontradicted absolute-pressure declaration, validates through the strict tool request schema, and calls the shared atmospheric service directly. The model is not asked to choose or supply calculation arguments, and history is never used as proof of calculation inputs. Ambiguous or unsupported phrasings clarify. At most one calculation is executed per request. The mass-fraction operation, fire-behavior prediction, and safety/certification advice are unavailable. Ollama generation is used for non-calculation answers only.

## Response

```json
{
  "status": "answered",
  "api_schema_version": "1.0",
  "explanation": "At the supplied oxygen fraction and absolute pressure, the deterministic engine reports the value below.",
  "bases": ["general_background", "deterministic_calculation"],
  "citations": [],
  "calculation": {
    "status": "success",
    "calculation": "oxygen_partial_pressure",
    "outputs": {"oxygen_partial_pressure_kpa": 21.27825},
    "units": {"oxygen_partial_pressure_kpa": "kPa"},
    "verification": {"result": "DERIVED"},
    "api_schema_version": "1.0"
  }
}
```

`calculation` is the authoritative atmospheric-engine envelope. On calculation success, the server builds the short numeric explanation directly from that envelope and does not ask the model to restate the result. The shown envelope is abbreviated; actual responses also include inputs, formula, assumptions, limitations, warnings, conversion methods, and full provenance from `modelling.atmospheric.CalculationResult.to_dict()`. `bases` can include any combination of `general_background`, `retrieved_unreviewed`, `reviewed_evidence`, and `deterministic_calculation`; `unsupported` is used for requests outside scope. Citations are assembled server-side only from retrieved chunk IDs and trusted SQLite metadata. Local paths are not returned.

The React frontend sends assistant requests to FastAPI and keeps up to eight recent user/assistant turns as untrusted client-side context. In local development, Vite proxies `/api` to `http://127.0.0.1:8000`; `VITE_API_BASE_URL` can set an API origin for another environment, but the API currently has no authentication or CORS policy. A separately hosted frontend therefore needs a deliberately configured allowed origin before browser requests will work. Display the `calculation` object as the authoritative numeric result; do not connect the browser directly to Ollama.

Statuses are `answered`, `insufficient_evidence`, `clarification`, and `unsupported`. Errors retain the API-wide envelope:

```json
{"status":"error","api_schema_version":"1.0","error":{"code":"provider_unavailable","field":null,"message":"The model provider is unavailable."}}
```

## Current evidence/model state

The source registry has no review-state or AI-ingestion approval fields. `ai/ingestion_approvals.csv` is intentionally empty; therefore no PDFs are approved for ingestion. Retrieval has no calibrated threshold, and `ai/evaluation/retrieval_calibration.json` remains pending, so retrieval abstains. A threshold may be published only after scores from the selected embedding model are evaluated against all labeled cases in `ai/evaluation/retrieval_cases.json`.

The current calculation request path does not use Ollama tool calling: the server parses explicit values from the current question, validates them, and calls the deterministic atmospheric service. Prior local tool-call probes are limited compatibility observations and do not establish reliable tool selection. Ollama generation is used only for non-calculation questions and requires the configured local service/model; it is not needed for calculations, unsupported-request handling, or evidence abstention. Embeddings remain unconfigured. No project documents are approved or indexed, so evidence retrieval is unavailable.
