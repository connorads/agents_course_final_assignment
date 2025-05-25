"""
safe_duck_tool.py
A resilient, family-friendly DuckDuckGo search Tool for Pydantic-AI.
"""

from __future__ import annotations

import functools
import time
from dataclasses import dataclass
from typing_extensions import TypedDict

import anyio
import anyio.to_thread
from duckduckgo_search import DDGS, exceptions
from pydantic import TypeAdapter
from pydantic_ai.tools import Tool


# ──────────────────────────────────────────────────────────────────────────
# 1. Types
# ──────────────────────────────────────────────────────────────────────────
class DuckDuckGoResult(TypedDict):
    title: str
    href: str
    body: str


duckduckgo_ta = TypeAdapter(list[DuckDuckGoResult])


# ──────────────────────────────────────────────────────────────────────────
# 2. Search wrapper with cache + back-off
# ──────────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=512)
def _safe_search(
    query: str,
    *,
    ddgs_constructor_kwargs_tuple: tuple,
    safesearch: str,
    max_results: int | None,
    retries: int = 5,
) -> list[dict[str, str]]:
    wait = 1
    for _ in range(retries):
        try:

            ddgs = DDGS(**dict(ddgs_constructor_kwargs_tuple))

            return list(
                ddgs.text(query, safesearch=safesearch, max_results=max_results)
            )
        except exceptions.RatelimitException as e:
            time.sleep(getattr(e, "retry_after", wait))
            wait = min(wait * 2, 30)
    raise RuntimeError("DuckDuckGo kept rate-limiting after multiple attempts")


# ──────────────────────────────────────────────────────────────────────────
# 3. Tool implementation
# ──────────────────────────────────────────────────────────────────────────
@dataclass
class _SafeDuckToolImpl:
    ddgs_constructor_kwargs: dict  # Renamed from client_kwargs
    safesearch: str  # Added to store safesearch setting
    max_results: int | None

    async def __call__(self, query: str) -> list[DuckDuckGoResult]:
        search = functools.partial(
            _safe_search,
            # Convert dict to sorted tuple of items to make it hashable
            ddgs_constructor_kwargs_tuple=tuple(
                sorted(self.ddgs_constructor_kwargs.items())
            ),
            safesearch=self.safesearch,  # Pass stored safesearch
            max_results=self.max_results,
        )
        results = await anyio.to_thread.run_sync(search, query)
        # validate & coerce with Pydantic
        return duckduckgo_ta.validate_python(results)


def safe_duckduckgo_search_tool(
    *,
    safesearch: str = "moderate",  # "on" | "moderate" | "off"
    timeout: int = 15,
    max_results: int | None = None,
    proxy: str | None = None,  # e.g. "socks5h://user:pw@host:1080"
) -> Tool:
    """
    Create a resilient, Safe-Search-enabled DuckDuckGo search Tool.

    Drop-in replacement for `pydantic_ai.common_tools.duckduckgo.duckduckgo_search_tool`.
    """
    # Arguments for DDGS constructor
    ddgs_constructor_kwargs = dict(
        timeout=timeout,
        proxy=proxy,
    )
    # Arguments for ddgs.text() method are handled separately (safesearch, max_results)

    impl = _SafeDuckToolImpl(
        ddgs_constructor_kwargs=ddgs_constructor_kwargs,
        safesearch=safesearch,
        max_results=max_results,
    )
    return Tool(
        impl.__call__,
        name="safe_duckduckgo_search",
        description=(
            "DuckDuckGo web search with Safe Search, automatic back-off, and "
            "LRU caching. Pass a plain-text query; returns a list of results."
        ),
    )
