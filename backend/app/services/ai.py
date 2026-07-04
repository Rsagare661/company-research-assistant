"""
OpenRouter integration.

Sends crawled page content + supporting search results to an AI model and
asks for a strict JSON structure back, which we validate against
CompanyReport before returning it to the client.
"""
import json
import re
import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """You are a meticulous B2B company research analyst working for a consultancy.
You are given raw text scraped from a company's own website, plus web search snippets.
Your job is to produce an accurate, well-organized research report as STRICT JSON ONLY.

Rules:
- Base every factual claim ONLY on the provided content. Do not invent phone numbers, addresses, or client names.
- If a field is not found in the provided content, use null (for strings) or an empty list.
- "pain_points" should be realistic business/strategic challenges this company likely faces, inferred from its
  market position, product, and competitive landscape described in the content — label them clearly as analysis,
  not confirmed facts.
- "competitors" must be real, named companies in the same industry/space. Include a website if you are confident
  of it, otherwise null. Prefer competitors mentioned or implied by the source content and search results.
- Keep "summary" to 3-5 sentences.
- "products_services" is a short list of concrete product/service names or offering categories.
- "additional_insights" can include things like target market, notable positioning, recent news mentioned in
  sources, or funding/scale signals — 2-5 bullet points.
- Output MUST be valid JSON matching this exact schema, with no markdown fences, no commentary:

{
  "company_name": string,
  "industry": string | null,
  "phone": string | null,
  "address": string | null,
  "summary": string,
  "products_services": string[],
  "pain_points": string[],
  "additional_insights": string[],
  "competitors": [{"name": string, "website": string | null, "reason": string}]
}
"""


class AIError(Exception):
    pass


def _build_user_prompt(company_name: str, website: str, crawled_pages: list[dict], search_snippets: list[dict], competitor_snippets: list[dict]) -> str:
    parts = [f"COMPANY NAME (as provided): {company_name}", f"WEBSITE: {website}", ""]

    parts.append("=== CRAWLED WEBSITE CONTENT ===")
    for page in crawled_pages:
        parts.append(f"\n--- Page: {page['title']} ({page['section']}) | URL: {page['url']} ---")
        parts.append(page["content"])

    if search_snippets:
        parts.append("\n=== WEB SEARCH CONTEXT ===")
        for s in search_snippets:
            parts.append(f"- {s.get('title','')}: {s.get('snippet','')} ({s.get('link','')})")

    if competitor_snippets:
        parts.append("\n=== COMPETITOR SEARCH RESULTS ===")
        for s in competitor_snippets:
            parts.append(f"- {s.get('title','')}: {s.get('snippet','')} ({s.get('link','')})")

    return "\n".join(parts)


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    # Strip markdown fences if the model added them despite instructions
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: grab the largest {...} block
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise AIError("The AI model did not return valid JSON.")


async def generate_company_report(
    company_name: str,
    website: str,
    crawled_pages: list[dict],
    search_snippets: list[dict],
    competitor_snippets: list[dict],
    api_key: str,
    model: str,
) -> dict:
    user_prompt = _build_user_prompt(company_name, website, crawled_pages, search_snippets, competitor_snippets)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://company-research-assistant.app",
                "X-Title": "Company Research Assistant",
            },
            json=payload,
        )

    if resp.status_code == 401:
        raise AIError("Invalid OpenRouter API key.")
    if resp.status_code >= 400:
        raise AIError(f"OpenRouter request failed ({resp.status_code}): {resp.text[:300]}")

    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise AIError("Unexpected response format from OpenRouter.")

    return _extract_json(content)
