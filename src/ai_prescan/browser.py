"""Browser-backed fetch for hosts that block scripted requests.

whoop.com returns 403 to every header combination while serving a real browser normally, and
Cloudflare-style blocking is common enough that losing those hosts would quietly depress recall —
a headline evaluation metric. So the fallback is a real browser, used only after a plain fetch has
already been refused.

Installed as `fetch.browser_fetch` by `install()`. Kept behind that hook so the rest of the system
has no opinion about how a page was obtained, only about what provenance it carries.
"""

from __future__ import annotations

import logging

from . import fetch

log = logging.getLogger(__name__)

_TIMEOUT_MS = 30_000
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def browser_fetch(url: str) -> tuple[str, bytes] | None:
    """Render `url` in headless Chromium. Returns (final_url, content) or None.

    Returning None rather than raising keeps the caller's contract: a page we cannot obtain becomes
    an unavailable source, never an exception that ends the scan.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.warning("playwright not installed; blocked hosts stay unavailable")
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page(user_agent=UA, locale="en-GB")
                page.goto(url, timeout=_TIMEOUT_MS, wait_until="domcontentloaded")
                content = page.content().encode("utf-8")
                final = page.url
            finally:
                browser.close()
        return final, content
    except Exception as exc:  # noqa: BLE001 — a failed fallback is data, not a crash
        log.warning("browser fetch failed for %s: %s", url, type(exc).__name__)
        return None


def install() -> None:
    """Register the fallback. Called once at startup by the CLI."""
    fetch.browser_fetch = browser_fetch
