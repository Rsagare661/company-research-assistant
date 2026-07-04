"""
Intelligent, lightweight website crawler.

Strategy:
1. Fetch the homepage, parse all internal links.
2. Score links by relevance to a fixed set of target sections
   (home/about/products/services/solutions/contact/pricing).
3. Fetch the top-scoring unique pages (deduped by normalized URL + content hash),
   skipping login/auth/irrelevant pages.
4. Strip nav/footer/script noise and return clean text per page.

This avoids a full-site crawl (slow, wasteful) while still covering the
pages that actually contain the information the AI step needs.
"""
import hashlib
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from app.config import settings

USER_AGENT = "Mozilla/5.0 (compatible; CompanyResearchBot/1.0; +https://example.com/bot)"

TARGET_KEYWORDS = {
    "home": ["home", "index"],
    "about": ["about", "about-us", "who-we-are", "company", "our-story", "team"],
    "products": ["product", "products", "platform", "features"],
    "services": ["service", "services", "solutions", "what-we-do"],
    "contact": ["contact", "contact-us", "get-in-touch", "support"],
    "pricing": ["pricing", "plans", "price"],
}

SKIP_PATTERNS = [
    "login", "signin", "sign-in", "signup", "sign-up", "register",
    "cart", "checkout", "privacy", "terms", "cookie", "logout",
    ".pdf", ".jpg", ".png", ".zip", ".svg", ".css", ".js",
    "javascript:", "mailto:", "tel:", "#",
]


class CrawlError(Exception):
    pass


def _normalize(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def _should_skip(url: str) -> bool:
    low = url.lower()
    return any(p in low for p in SKIP_PATTERNS)


def _score_link(url: str) -> tuple[str, int]:
    """Return (section_label, score). Higher score = more relevant."""
    low = url.lower()
    for section, keywords in TARGET_KEYWORDS.items():
        for kw in keywords:
            if f"/{kw}" in low or low.endswith(kw):
                return section, 10
    return "other", 0


def _clean_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "nav", "footer", "noscript", "svg", "iframe"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())


async def _fetch(client: httpx.AsyncClient, url: str) -> httpx.Response | None:
    try:
        resp = await client.get(url, timeout=settings.CRAWL_TIMEOUT_SECONDS, follow_redirects=True)
        if resp.status_code >= 400:
            return None
        content_type = resp.headers.get("content-type", "")
        if "text/html" not in content_type:
            return None
        return resp
    except (httpx.RequestError, httpx.TimeoutException):
        return None


async def crawl_website(base_url: str) -> list[dict]:
    """
    Returns a list of {url, section, title, content} dicts for the most
    relevant, deduplicated pages on the site.
    """
    headers = {"User-Agent": USER_AGENT}
    pages: list[dict] = []
    seen_urls: set[str] = set()
    seen_hashes: set[str] = set()

    async with httpx.AsyncClient(headers=headers) as client:
        home_resp = await _fetch(client, base_url)
        if home_resp is None:
            raise CrawlError(f"Could not reach {base_url}.")

        home_soup = BeautifulSoup(home_resp.text, "html.parser")
        parsed_base = urlparse(str(home_resp.url))
        origin = f"{parsed_base.scheme}://{parsed_base.netloc}"

        # Record homepage
        home_url_norm = _normalize(str(home_resp.url))
        home_text = _clean_text(home_soup)
        home_hash = hashlib.md5(home_text[:500].encode()).hexdigest()
        seen_urls.add(home_url_norm)
        seen_hashes.add(home_hash)
        pages.append({
            "url": home_url_norm,
            "section": "home",
            "title": (home_soup.title.string.strip() if home_soup.title and home_soup.title.string else "Home"),
            "content": home_text[: settings.MAX_CONTENT_CHARS_PER_PAGE],
        })

        # Discover candidate internal links
        candidates: list[tuple[int, str]] = []
        for a in home_soup.find_all("a", href=True):
            href = a["href"]
            if _should_skip(href):
                continue
            full_url = urljoin(origin, href)
            if urlparse(full_url).netloc != parsed_base.netloc:
                continue  # external link, not part of this site
            norm = _normalize(full_url)
            if norm in seen_urls:
                continue
            section, score = _score_link(norm)
            if score > 0:
                candidates.append((score, norm))

        # Dedupe candidates, keep highest scoring per URL, sort best-first
        unique_candidates = sorted(set(candidates), key=lambda x: -x[0])

        for score, url in unique_candidates:
            if len(pages) >= settings.MAX_PAGES_TO_CRAWL:
                break
            if url in seen_urls:
                continue
            resp = await _fetch(client, url)
            seen_urls.add(url)
            if resp is None:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            text = _clean_text(soup)
            if len(text) < 50:
                continue  # near-empty page, skip
            content_hash = hashlib.md5(text[:500].encode()).hexdigest()
            if content_hash in seen_hashes:
                continue  # duplicate content (e.g. template page with no real content)
            seen_hashes.add(content_hash)
            section, _ = _score_link(url)
            title = soup.title.string.strip() if soup.title and soup.title.string else section.title()
            pages.append({
                "url": url,
                "section": section,
                "title": title,
                "content": text[: settings.MAX_CONTENT_CHARS_PER_PAGE],
            })

    return pages
