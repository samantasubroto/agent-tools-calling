"""Web tools: DuckDuckGo search (no API key needed)."""

import time

from ddgs import DDGS

# DuckDuckGo sometimes returns nothing for one backend, so try a fallback.
_BACKENDS = ("auto", "lite", "html", "bing", "yahoo")


def web_search(query: str, max_results: int = 5) -> str:
    """Search DuckDuckGo and return title, URL and snippet for each result."""
    max_results = max(1, min(int(max_results), 10))
    last_error = None
    for attempt in range(2):  # second round after a pause helps with rate limits
        if attempt:
            time.sleep(3)
        for backend in _BACKENDS:
            try:
                results = DDGS().text(query, max_results=max_results, backend=backend)
            except Exception as exc:
                last_error = exc
                continue
            if results:
                return "\n\n".join(
                    f"{i}. {r.get('title', '')}\n   {r.get('href', '')}\n   {r.get('body', '')}"
                    for i, r in enumerate(results, 1)
                )
    raise RuntimeError(f"No search results found ({last_error}).")


WEB_TOOL_SCHEMAS = [
    {
        "name": "web_search",
        "description": (
            "Search the web (DuckDuckGo) for current information. Returns titles, "
            "URLs and snippets. Use for recent facts, news, prices or research."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."},
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return (1-10). Default 5.",
                },
            },
            "required": ["query"],
        },
    },
]

WEB_TOOL_FUNCTIONS = {
    "web_search": web_search,
}
