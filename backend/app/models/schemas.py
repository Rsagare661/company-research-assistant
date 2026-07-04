from pydantic import BaseModel, Field
from typing import Optional


class ResearchRequest(BaseModel):
    query: str = Field(..., description="Company name or website URL")
    openrouter_api_key: str = Field(..., description="User-provided OpenRouter API key")
    serper_api_key: str = Field(..., description="User-provided Serper.dev API key")
    ai_model: str = Field(default="anthropic/claude-sonnet-4.5")

    # Optional Discord auto-send
    discord_bot_token: Optional[str] = None
    discord_channel_id: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_email: Optional[str] = None


class Competitor(BaseModel):
    name: str
    website: Optional[str] = None
    reason: Optional[str] = None


class SourceRef(BaseModel):
    url: str
    title: Optional[str] = None
    type: str = "crawled_page"  # crawled_page | search_result


class CompanyReport(BaseModel):
    company_name: str
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    summary: str
    products_services: list[str] = []
    pain_points: list[str] = []
    additional_insights: list[str] = []
    competitors: list[Competitor] = []
    sources: list[SourceRef] = []
    pages_crawled: int = 0
    ai_model_used: str = ""


class ResearchResponse(BaseModel):
    status: str  # "success" | "error"
    report: Optional[CompanyReport] = None
    pdf_base64: Optional[str] = None
    discord_sent: bool = False
    error: Optional[str] = None


class DiscordSendRequest(BaseModel):
    bot_token: str
    channel_id: str
    applicant_name: str
    applicant_email: str
    company_name: str
    company_website: Optional[str] = None
    pdf_base64: str
