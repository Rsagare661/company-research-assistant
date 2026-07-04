import base64
import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.schemas import ResearchRequest, ResearchResponse, CompanyReport
from app.services import serper, crawler, ai as ai_service, pdf_report, discord_bot
from app.cache import research_cache
from app.config import settings

logger = logging.getLogger("research")
router = APIRouter(prefix="/api", tags=["research"])


@router.post("/research", response_model=ResearchResponse)
async def research_company(req: ResearchRequest):
    query = req.query.strip()
    if not query:
        return JSONResponse(status_code=400, content={"status": "error", "error": "Query cannot be empty."})

    cache_key = research_cache.make_key("research", query.lower(), req.ai_model)
    cached = research_cache.get(cache_key)
    if cached:
        logger.info(f"Cache hit for '{query}'")
        report_dict = cached
    else:
        try:
            report_dict = await _run_research_pipeline(req)
        except (serper.SerperError, crawler.CrawlError, ai_service.AIError) as e:
            return JSONResponse(status_code=422, content={"status": "error", "error": str(e)})
        except Exception as e:  # noqa: BLE001
            logger.exception("Unexpected research pipeline failure")
            return JSONResponse(status_code=500, content={"status": "error", "error": f"Unexpected error: {e}"})

        research_cache.set(cache_key, report_dict)

    pdf_bytes = pdf_report.build_report_pdf(report_dict)
    pdf_b64 = base64.b64encode(pdf_bytes).decode()

    discord_sent = False
    if req.discord_bot_token and req.discord_channel_id:
        try:
            await discord_bot.send_report_to_discord(
                bot_token=req.discord_bot_token,
                channel_id=req.discord_channel_id,
                applicant_name=req.applicant_name or "Unknown",
                applicant_email=req.applicant_email or "unknown@example.com",
                company_name=report_dict.get("company_name", query),
                company_website=report_dict.get("website"),
                pdf_bytes=pdf_bytes,
            )
            discord_sent = True
        except discord_bot.DiscordError as e:
            logger.warning(f"Discord send failed: {e}")

    return ResearchResponse(
        status="success",
        report=CompanyReport(**report_dict),
        pdf_base64=pdf_b64,
        discord_sent=discord_sent,
    )


async def _run_research_pipeline(req: ResearchRequest) -> dict:
    query = req.query.strip()

    # Step 1: resolve to a website
    sources = []
    if serper.is_probable_url(query):
        website = serper.normalize_url(query)
        company_name_guess = _domain_to_name(website)
        search_results = []
    else:
        website, search_results = await serper.find_official_website(query, req.serper_api_key)
        company_name_guess = query
        for r in search_results[:5]:
            sources.append({"url": r.get("link", ""), "title": r.get("title"), "type": "search_result"})

    # Step 2: crawl the site
    pages = await crawler.crawl_website(website)
    for p in pages:
        sources.append({"url": p["url"], "title": p["title"], "type": "crawled_page"})

    # Step 3: enrichment + competitor search (best-effort; don't fail the whole run)
    enrichment, competitor_snippets = [], []
    try:
        enrichment = await serper.enrich_company_search(company_name_guess, req.serper_api_key)
    except serper.SerperError:
        pass
    try:
        competitor_snippets = await serper.find_competitors(company_name_guess, "", req.serper_api_key)
    except serper.SerperError:
        pass

    # Step 4: AI synthesis
    ai_json = await ai_service.generate_company_report(
        company_name=company_name_guess,
        website=website,
        crawled_pages=pages,
        search_snippets=enrichment,
        competitor_snippets=competitor_snippets,
        api_key=req.openrouter_api_key,
        model=req.ai_model,
    )

    report = {
        "company_name": ai_json.get("company_name") or company_name_guess,
        "website": website,
        "phone": ai_json.get("phone"),
        "address": ai_json.get("address"),
        "industry": ai_json.get("industry"),
        "summary": ai_json.get("summary", ""),
        "products_services": ai_json.get("products_services", []),
        "pain_points": ai_json.get("pain_points", []),
        "additional_insights": ai_json.get("additional_insights", []),
        "competitors": ai_json.get("competitors", []),
        "sources": sources,
        "pages_crawled": len(pages),
        "ai_model_used": req.ai_model,
    }
    return report


def _domain_to_name(url: str) -> str:
    from urllib.parse import urlparse
    netloc = urlparse(url).netloc.lower().replace("www.", "")
    return netloc.split(".")[0].capitalize()
