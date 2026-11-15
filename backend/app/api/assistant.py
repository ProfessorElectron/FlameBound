"""Stateless AI assistant API; deterministic calculation results remain separate."""

from fastapi import APIRouter, HTTPException

from ai.config import ProviderError
from backend.app.schemas.assistant import AssistantChatRequest, AssistantChatResponse
from backend.app.services.assistant_service import AssistantOrchestrator

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/chat", response_model=AssistantChatResponse)
def assistant_chat(request: AssistantChatRequest) -> AssistantChatResponse:
    try:
        return AssistantOrchestrator().respond(request)
    except ProviderError as exc:
        status = 502 if exc.code in {"invalid_provider_response", "invalid_assistant_response", "unexpected_tool_call"} else 503
        raise HTTPException(status_code=status, detail={
            "code": exc.code, "field": None, "message": str(exc),
        }) from None
