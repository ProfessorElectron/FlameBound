# Phase 5 document index

The Phase 5 files are implementation and audit snapshots from separate stages. Some conclusions and scope statements in them describe an earlier backend-only state and are not the current architecture. Preserve them as historical artifacts; do not use their old “frontend not integrated” or “AI not implemented” statements as current status.

For current user-facing setup and behavior, use the root [README](../../README.md), [AI setup](ai_setup.md), [assistant API contract](assistant_api.md), and [submission demo script](../submission/demo_script.md). The current branch includes a React assistant and FastAPI assistant route. Deterministic calculations stay server-side; Ollama is required only for general background responses. Project evidence retrieval remains unavailable.
