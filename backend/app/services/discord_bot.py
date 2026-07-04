"""
Sends the finished PDF report + applicant/company metadata to a Discord
channel using the Discord Bot HTTP API directly (no discord.py dependency
needed for a one-shot message + file upload).
"""
import base64
import httpx

DISCORD_API = "https://discord.com/api/v10"


class DiscordError(Exception):
    pass


async def send_report_to_discord(
    bot_token: str,
    channel_id: str,
    applicant_name: str,
    applicant_email: str,
    company_name: str,
    company_website: str | None,
    pdf_bytes: bytes,
) -> None:
    embed_content = (
        f"**New Company Research Report**\n"
        f"**Applicant:** {applicant_name} ({applicant_email})\n"
        f"**Company:** {company_name}\n"
        f"**Website:** {company_website or 'N/A'}"
    )

    filename = f"{company_name.lower().replace(' ', '-')}-research-report.pdf"

    files = {
        "file": (filename, pdf_bytes, "application/pdf"),
    }
    data = {
        "payload_json": (
            '{"content": ' + _json_escape(embed_content) + "}"
        ),
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{DISCORD_API}/channels/{channel_id}/messages",
            headers={"Authorization": f"Bot {bot_token}"},
            data=data,
            files=files,
        )

    if resp.status_code == 401:
        raise DiscordError("Invalid Discord bot token.")
    if resp.status_code == 403:
        raise DiscordError("Bot lacks permission to post in that channel.")
    if resp.status_code == 404:
        raise DiscordError("Discord channel not found. Check the channel ID.")
    if resp.status_code >= 400:
        raise DiscordError(f"Discord API error ({resp.status_code}): {resp.text[:300]}")


def _json_escape(text: str) -> str:
    import json
    return json.dumps(text)
