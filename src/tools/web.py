import httpx
from markdownify import markdownify
from pydantic_settings import BaseSettings

from tools._base import Tool


class WebSearch(Tool):
    class Config(BaseSettings):
        brave_api_key: str

    @staticmethod
    async def run(query: str, count: int = 5) -> str:
        """Search the web and return a summary of results."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params={"q": query, "count": count},
                    headers={"Accept": "application/json", "X-Subscription-Token": WebSearch._cfg.brave_api_key},
                    timeout=10.0,
                )
                resp.raise_for_status()
                results = resp.json().get("web", {}).get("results", [])
        except Exception as exc:
            return f"search error: {exc}"

        if not results:
            return "no results"
        lines = []
        for r in results:
            lines.append(f"[{r.get('title', '')}]({r.get('url', '')})")
            snippet = r.get("description", "")
            if snippet:
                lines.append(snippet)
            lines.append("")
        return "\n".join(lines).strip()


class WebFetch(Tool):
    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        half = max_chars // 2
        return text[:half] + f"\n...[truncated {len(text) - max_chars} chars]...\n" + text[-half:]

    @staticmethod
    async def run(url: str, max_chars: int = 20_000) -> str:
        """Fetch a URL and return its content as markdown."""
        try:
            async with httpx.AsyncClient(follow_redirects=True, max_redirects=5) as client:
                resp = await client.get(url, timeout=15.0, headers={"User-Agent": "monoclaw/1.0"})
                resp.raise_for_status()
                ct = resp.headers.get("content-type", "")
                if "html" in ct:
                    text = markdownify(resp.text, strip=["script", "style"])
                else:
                    text = resp.text
            return WebFetch._truncate(text, max_chars)
        except Exception as exc:
            return f"fetch error: {exc}"
