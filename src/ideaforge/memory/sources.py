"""Web search — ground diverge phase in real-world information.

Uses DuckDuckGo (no API key needed) to fetch recent context.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

MAX_RESULTS = 5


def web_search(query: str, max_results: int = MAX_RESULTS) -> list[dict]:
    """Search the web and return top results with titles + snippets.

    Returns list of {"title": str, "snippet": str, "url": str}.
    """
    try:
        from ddgs import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return [
                {
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", ""),
                }
                for r in results
            ]
    except Exception:
        log.warning("Web search failed for query: %s", query)
        return []


def format_search_context(results: list[dict]) -> str:
    """Format search results into a context string for the LLM prompt."""
    if not results:
        return ""
    from ideaforge.utils.security import sanitize_prompt_input

    lines = ["Recent research and context:"]
    for i, r in enumerate(results, 1):
        title = sanitize_prompt_input(r.get("title", ""), max_length=150)
        snippet = sanitize_prompt_input(r.get("snippet", ""), max_length=250)
        lines.append(f"  {i}. {title}")
        if snippet:
            lines.append(f"     {snippet}")
    return "\n".join(lines)
