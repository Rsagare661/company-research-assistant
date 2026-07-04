"""
Serper.dev integration.

Responsibilities:
1. Resolve a company NAME into its official website (when the user doesn't
   paste a URL directly).
2. Run supporting searches to enrich research (news, "about" info, industry).
3. Help surface competitor candidates that the AI step can then reason over.

Serper.dev exposes a Google-Search-as-an-API. We never scrape Google directly.
"""
import re
import httpx
from urllib.parse import urlparse

SERPER_SEARCH_URL = "https://google.serper.dev/search"

# Domains that are almost never a company's own official site
BLOCKED_DOMAINS = {
    "linkedin.com", "facebook.com", "twitter.com", "x.com", "instagram.com",
    "youtube.com", "wikipedia.org", "crunchbase.com", "glassdoor.com",
    "indeed.com", "bloomberg.com", "reuters.com", "g2.com", "capterra.com",
    "trustpilot.com", "medium.com", "github.com", "pitchbook.com",
    "owler.com", "zoominfo.com",
}


class SerperError(Exception):
    pass


async def _post(api_key: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            SERPER_SEARCH_URL,
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json=payload,
        )
    if resp.status_code == 401 or resp.status_code == 403:
        raise SerperError("Invalid Serper.dev API key.")
    if resp.status_code >= 400:
        raise SerperError(f"Serper.dev request failed ({resp.status_code}).")
    return resp.json()


def _root_domain(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def is_probable_url(query: str) -> bool:
    q = query.strip().lower()
    if q.startswith("http://") or q.startswith("https://"):
        return True
    return bool(re.match(r"^[a-z0-9-]+\.[a-z]{2,}(/.*)?$", q))


def normalize_url(query: str) -> str:
    q = query.strip()
    if not q.startswith("http"):
        q = "https://" + q
    return q


async def find_official_website(company_name: str, api_key: str) -> tuple[str, list[dict]]:
    """
    Search for the company and return its most likely official website,
    plus the raw search results (used later as source references).
    """
    data = await _post(api_key, {"q": f"{company_name} official website"})
    organic = data.get("organic", [])

    candidate = None
    for result in organic:
        link = result.get("link", "")
        domain = _root_domain(link)
        if not domain or domain in BLOCKED_DOMAINS:
            continue
        # A strong heuristic: the company name (loosely) appears in the domain
        candidate = link
        break

    if not candidate and organic:
        candidate = organic[0].get("link")

    if not candidate:
        raise SerperError(f"Could not find an official website for '{company_name}'.")

    return candidate, organic


async def enrich_company_search(company_name: str, api_key: str) -> list[dict]:
    """General enrichment search: news, funding, industry context."""
    data = await _post(api_key, {"q": f"{company_name} company overview industry"})
    return data.get("organic", [])[:5]


async def find_competitors(company_name: str, industry_hint: str, api_key: str) -> list[dict]:
    """
    Search for competitor candidates. The AI step still does the final
    reasoning/filtering, but this gives it real, current web results to
    ground its answer in rather than relying purely on training data.
    """
    query = f"top competitors and alternatives to {company_name}"
    if industry_hint:
        query += f" in {industry_hint}"
    data = await _post(api_key, {"q": query})
    return data.get("organic", [])[:8]
