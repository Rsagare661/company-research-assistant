# Company Research Assistant

AI-powered company research: give it a company name or URL and it finds the official
site, crawls the pages that matter, and returns a summary, products/services, AI-generated
pain points, competitor analysis, and a downloadable PDF — all in a ChatGPT-style interface.

Built for the Relu Consultancy AI & Automation Developer Hiring Challenge.

```
┌─────────────┐     ┌───────────────┐     ┌──────────────┐     ┌────────────┐
│  React UI   │────▶│  FastAPI      │────▶│  Serper.dev  │     │            │
│  (Vercel)   │◀────│  (Render/     │────▶│  Crawler     │────▶│ OpenRouter │
└─────────────┘     │   Railway)    │     │  ReportLab   │◀────│    AI      │
                     └───────────────┘     └──────────────┘     └────────────┘
                            │
                            ▼
                     Discord Bot API (optional)
```

## Features

- **Flexible input** — accepts a company name ("Figma") or a URL ("https://figma.com")
- **Website discovery** — resolves a company name to its official site via Serper.dev,
  filtering out LinkedIn/Wikipedia/Crunchbase-style noise
- **Intelligent crawling** — scores and fetches Home, About, Products, Services,
  Solutions, Contact, and Pricing pages; skips logins/duplicates/near-empty pages;
  dedupes by content hash
- **AI synthesis** — sends crawled content + search context to any OpenRouter model
  (user-selectable) and gets back a strict-JSON company report
- **Competitor analysis** — grounded in live Serper.dev search results, not just
  model memory, with name + website for each competitor
- **PDF report** — a clean, branded one-pager generated server-side with ReportLab,
  returned as base64 for instant client-side download
- **Discord bonus** — configure a bot token + channel ID and every completed report
  auto-posts (with the PDF attached) along with the applicant's name/email
- **Caching** — identical queries are served from an in-memory TTL cache instead of
  re-crawling/re-calling the AI
- **Chat-style UI** — dark, terminal-inspired interface with live progress tracking,
  source citations, error states, and full mobile responsiveness

## Project structure

```
company-research-assistant/
├── backend/                 FastAPI service
│   ├── app/
│   │   ├── main.py          App entrypoint + CORS
│   │   ├── config.py        Settings/env
│   │   ├── cache.py         In-memory TTL cache
│   │   ├── models/schemas.py
│   │   ├── routers/
│   │   │   ├── research.py  POST /api/research (main pipeline)
│   │   │   └── config.py    GET /api/models, /api/health
│   │   └── services/
│   │       ├── serper.py    Search / website resolution / competitors
│   │       ├── crawler.py   Website crawling + extraction
│   │       ├── ai.py        OpenRouter integration
│   │       ├── pdf_report.py PDF generation
│   │       └── discord_bot.py Discord bot HTTP API
│   ├── requirements.txt
│   ├── render.yaml
│   ├── Procfile
│   └── .env.example
└── frontend/                React (Vite + Tailwind)
    ├── src/
    │   ├── App.jsx           Chat orchestration
    │   ├── components/       Sidebar, Hero, ChatInput, ProgressTracker,
    │   │                     CompanyReport, ErrorCard
    │   └── api/client.js     Axios wrapper
    ├── vercel.json
    └── .env.example
```

## How it works

1. User enters a company name or URL in the chat input.
2. **If a name**: `serper.py` searches `"{name} official website"`, filters out
   known non-official domains (LinkedIn, Wikipedia, Crunchbase, etc.), and picks
   the top real candidate.
3. `crawler.py` fetches the homepage, extracts internal links, scores them against
   target sections (home/about/products/services/pricing/contact), and fetches the
   highest-scoring unique pages — skipping login/cart/legal pages and deduping by
   content hash so template pages with no real content don't waste a crawl slot.
4. `serper.py` runs two more searches: general company/industry context, and a
   competitor search, to ground the AI step in current web results rather than
   pure model memory.
5. `ai.py` sends everything to the user's chosen OpenRouter model with a strict
   JSON-only system prompt and validates/repairs the response.
6. `pdf_report.py` renders the final report as a PDF with ReportLab.
7. If Discord is configured, `discord_bot.py` posts the PDF + applicant/company
   metadata to the given channel via the Discord Bot HTTP API.
8. The frontend renders the structured report, offers a one-click PDF download,
   and shows source citations for every page/search result used.

## Local setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- A [Serper.dev](https://serper.dev) API key (free tier available)
- An [OpenRouter](https://openrouter.ai) API key
- (Optional) A Discord bot token + channel ID for the Discord bonus feature

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit if you want server-side fallback keys
uvicorn app.main:app --reload --port 8000
```

The API is now live at `http://localhost:8000` (interactive docs at `/docs`).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local      # set VITE_API_BASE_URL if backend isn't on :8000
npm run dev
```

Open `http://localhost:5173`. Paste your OpenRouter and Serper.dev keys into the
sidebar (they're only ever sent from your browser directly in each research
request — the backend doesn't persist them).

## Environment variables

### Backend (`backend/.env`)
| Variable | Required | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | No | Server-side fallback if the client doesn't send one |
| `SERPER_API_KEY` | No | Server-side fallback if the client doesn't send one |
| `ALLOWED_ORIGINS` | Yes (prod) | Comma-separated list of allowed frontend origins for CORS |
| `MAX_PAGES_TO_CRAWL` | No | Default `8` |
| `CRAWL_TIMEOUT_SECONDS` | No | Default `10` |
| `MAX_CONTENT_CHARS_PER_PAGE` | No | Default `6000`, keeps AI prompts within budget |
| `CACHE_TTL_SECONDS` | No | Default `3600` |
| `DEFAULT_AI_MODEL` | No | Default `anthropic/claude-sonnet-4.5` |

### Frontend (`frontend/.env.local`)
| Variable | Required | Description |
|---|---|---|
| `VITE_API_BASE_URL` | Yes | URL of the deployed FastAPI backend |

API keys entered in the sidebar (OpenRouter, Serper.dev, Discord bot token) are
kept in browser memory only and sent per-request — never written to `.env` or a
database. This lets every user bring their own keys safely in a shared deployment.

## Deployment

### Backend → Render (or Railway)
1. Push this repo to GitHub.
2. On Render: **New → Web Service**, point it at `backend/`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Set `ALLOWED_ORIGINS` to your Vercel frontend URL once it exists.
   (`render.yaml` in `backend/` automates this if you use Render's Blueprint deploy.)

Railway: same build/start commands, or just point Railway at `backend/Procfile`.

### Frontend → Vercel
1. Import the repo, set the project root to `frontend/`.
2. Framework preset: Vite.
3. Add environment variable `VITE_API_BASE_URL` = your Render/Railway backend URL.
4. Deploy. `vercel.json` handles SPA routing.

Once both are live, update the backend's `ALLOWED_ORIGINS` with the final Vercel
URL and redeploy the backend so CORS allows it.

## API reference

### `POST /api/research`
```json
{
  "query": "figma.com",
  "openrouter_api_key": "sk-or-v1-...",
  "serper_api_key": "...",
  "ai_model": "anthropic/claude-sonnet-4.5",
  "discord_bot_token": null,
  "discord_channel_id": null,
  "applicant_name": null,
  "applicant_email": null
}
```
Returns `{ status, report, pdf_base64, discord_sent, error }`.

### `GET /api/models`
Returns the curated list of OpenRouter models shown in the UI dropdown.

### `GET /api/health`
Basic liveness check.

## Design notes

- **Why per-request keys instead of server env vars?** So the deployed demo can be
  shared publicly without exposing a shared API key or paying for every visitor's
  usage — each user configures their own keys client-side, matching the sidebar
  config screen in the product spec.
- **Why an in-memory cache instead of Redis?** The free-tier deployment target is a
  single instance; an in-memory TTL cache is zero-dependency and sufficient. The
  cache is isolated behind `app/cache.py` so swapping in Redis later is a one-file change.
- **Why ReportLab instead of an HTML→PDF renderer?** No headless-browser dependency,
  which keeps the Render/Railway free-tier build fast and light.

## Known limitations

- Crawling respects robots.txt implicitly only in that it uses a normal HTTP client;
  it does not currently parse `robots.txt` rules explicitly. For production use
  beyond a hackathon, add a robots.txt check before fetching.
- Very heavy JS-rendered (SPA) marketing sites may return sparse content, since the
  crawler doesn't run a headless browser. The AI step gracefully returns `null`/
  empty fields when data isn't found rather than guessing.
- Discord bonus assumes a bot has already been added to the target server. Bot
  token creation itself is outside the app's scope.
