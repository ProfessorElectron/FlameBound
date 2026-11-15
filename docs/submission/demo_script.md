# FlameBound local demonstration

Use this guide to run the current local prototype. It demonstrates deterministic atmospheric calculations and explicit scientific limits; it does not demonstrate NASA evidence retrieval or validated fire-behavior prediction.

## Prerequisites

- Python 3.10 or newer and `uv` (recommended for the locked dependency set); `pip` can be used with the unlocked `requirements.txt` alternative.
- Node.js 20.19+ or 22.12+ and npm (the version ranges are from `frontend/package.json`).
- Ollama with `qwen3:4b` available only for general AI background answers. Calculations, clarifications, unsupported-request handling, and evidence abstention work without Ollama.
- No credentials or `.env` file are required. Defaults are `http://127.0.0.1:8000` for FastAPI, `http://localhost:11434` for Ollama, and `qwen3:4b` for generation. The Vite proxy target can be overridden with `FLAMEBOUND_API_PROXY_TARGET`; an externally hosted API base can be set with `VITE_API_BASE_URL` (CORS is not configured for deployment).

## Start the services

Run these from the repository root in separate PowerShell terminals. Install the locked Python dependencies once if needed:

```powershell
python -m pip install uv
uv sync --locked
```

**Terminal 1 — backend:**

```powershell
uv run --locked python -m uvicorn backend.app.main:app --reload
```

**Terminal 2 — Ollama, optional for general background responses:** If Ollama is not already running, start it with `ollama serve`. In another terminal, fetch the model once if it is not installed:

```powershell
ollama pull qwen3:4b
```

**Terminal 3 — frontend:**

```powershell
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite (normally `http://localhost:5173`). The browser calls `/api` through Vite's proxy to the backend. `/docs` on the backend exposes its OpenAPI page.

To change the assistant provider defaults in the backend terminal before startup:

```powershell
$env:FLAMEBOUND_OLLAMA_BASE_URL = "http://localhost:11434"
$env:FLAMEBOUND_OLLAMA_GENERATION_MODEL = "qwen3:4b"
```

## Walkthrough

| Step | Action and exact input | Expected observation |
|---|---|---|
| 1 | Open **Overview**. | The dashboard is a UI demo. Its counts and cards are explicitly labeled illustrative fixtures, not NASA statistics. |
| 2 | Open **Scenario Analysis**. Enter oxygen mole fraction `0.21` and total pressure `101.325 kPa absolute`; select **Calculate scenario**. | Backend calculation envelope reports `p(O₂) = 21.27825 kPa`. It is a deterministic partial-pressure calculation, not a fire-behavior result. |
| 3 | Change the inputs to oxygen fraction `0.18` and pressure `95 kPa absolute`; calculate again. | The second deterministic result is `17.1 kPa`. The page does not calculate a paired comparison or evidence distance. |
| 4 | Open **AI Assistant** and submit: `Compare an atmosphere containing 21% oxygen at 101.325 kPa absolute with one containing 18% oxygen at 95 kPa absolute.` | The assistant uses the deterministic comparison path. Expect scenario/reference partial pressures `21.27825 kPa` and `17.1 kPa`, difference `4.17825 kPa`, relative difference about `24.4342%` (relative to the reference). Inspect **Calculation details** for the authoritative envelope. |
| 5 | Ask: `Calculate oxygen partial pressure for 30% oxygen at 10.2 psi absolute.` | Deterministic unit conversion and calculation; the result is about `21.0979573 kPa` oxygen partial pressure. |
| 6 | Ask: `Explain Dalton's law for ideal gas mixtures in general terms.` | With Ollama and `qwen3:4b` available, the assistant returns a general-background answer. This is model-generated background, not reviewed project evidence. |
| 7 | Ask: `Calculate oxygen partial pressure for 21% oxygen at 101.325 kPa.` | Clarification requests an explicit absolute-pressure basis; no calculation is made. |
| 8 | Ask: `Predict flame spread rate on the lunar surface.` | The assistant declines to produce a number because no validated predictive model is available. |
| 9 | Ask: `What experimental evidence exists for flame spread in reduced gravity?` | The assistant states project evidence retrieval is unavailable. No project citations are fabricated. |
| 10 | Open **Methodology** and **Evidence Explorer**. | Methodology reports unavailable pipeline stages. Evidence Explorer records and chart points are labeled demo fixtures, not experimental observations. |

### If Ollama is unavailable

Continue with steps 1–5 and 7–10. The deterministic calculation, clarification, prediction refusal, and evidence abstention paths do not need Ollama. Skip the general-background response in step 6 and state that this response requires the local Ollama service and configured model; do not substitute a scripted or fabricated answer.

## Demo boundaries

- Scenario Analysis accepts one atmosphere at a time and uses kPa absolute. Paired comparison is available through the assistant's deterministic endpoint path.
- Dashboard charts and visible records are illustrative fixtures. The harmonised test-point table is not populated with reviewed records.
- Project PDF ingestion and retrieval are not operational: there are no approved ingestion records, no configured/calibrated embedding retrieval, and the optional PDF dependency may not be installed.
- No validated lunar flame-spread, ignition, or safety prediction is available.
- The local workflow has no authentication or production CORS configuration. Do not present it as a deployed service.
