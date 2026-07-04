from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["config"])

# A curated shortlist shown in the UI dropdown. Users on OpenRouter can access
# many more models; this list covers strong, commonly available options.
AVAILABLE_MODELS = [
    {"id": "anthropic/claude-sonnet-4.5", "label": "Claude Sonnet 4.5"},
    {"id": "anthropic/claude-haiku-4.5", "label": "Claude Haiku 4.5"},
    {"id": "openai/gpt-4o", "label": "GPT-4o"},
    {"id": "openai/gpt-4o-mini", "label": "GPT-4o Mini"},
    {"id": "google/gemini-2.0-flash-001", "label": "Gemini 2.0 Flash"},
    {"id": "meta-llama/llama-3.3-70b-instruct", "label": "Llama 3.3 70B"},
    {"id": "deepseek/deepseek-chat", "label": "DeepSeek Chat"},
]


@router.get("/models")
async def list_models():
    return {"models": AVAILABLE_MODELS}


@router.get("/health")
async def health():
    return {"status": "ok"}
