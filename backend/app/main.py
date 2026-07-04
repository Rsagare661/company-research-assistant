from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import research, config as config_router

app = FastAPI(
    title="Company Research Assistant API",
    description="AI-powered company research: website crawling, Serper.dev search, "
                 "OpenRouter synthesis, competitor analysis, and PDF report generation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router)
app.include_router(config_router.router)


@app.get("/")
async def root():
    return {"name": "Company Research Assistant API", "status": "live", "docs": "/docs"}
