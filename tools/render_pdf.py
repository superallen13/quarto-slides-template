#!/usr/bin/env python3
"""Quarto reveal.js deck -> PDF, deterministically, via Playwright.

The old to_pdf.sh used Chrome's --print-to-pdf with --virtual-time-budget, a TIMED
snapshot that fires before the page settles -- so it raced two things and lost ~1/6:
lazy <img> loads, and client-side KaTeX's webfont application (math then shipped as
Times). It papered over this with an 8-try best-of-N lottery.

This driver removes the race instead of retrying it. It drives Chrome with Playwright
and WAITS for the real readiness signals before printing exactly once:
  - networkidle           -> images (incl. lazy) have loaded
  - document.fonts.ready  -> KaTeX woff2 are APPLIED, not pending (no Times fallback)
  - every <img> complete  -> no half-loaded figure
Then page.pdf() once. No retries, no heuristics.

Usage:
    python tools/render_pdf.py                  # slides.qmd -> slides.pdf
    python tools/render_pdf.py in.qmd out.pdf

Deps: playwright (pip install playwright). Uses the system Chrome (channel="chrome")
when present so there's no 150MB browser download; falls back to bundled chromium.
"""
from __future__ import annotations

import functools
import http.server
import socketserver
import subprocess
import sys
import threading
from pathlib import Path

DECK = Path(__file__).resolve().parent.parent


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # silence per-request logging
        pass


def render_quarto(qmd: Path) -> Path:
    """Render the .qmd to reveal.js HTML; return the .html path."""
    subprocess.run(
        ["quarto", "render", str(qmd), "--to", "revealjs"],
        cwd=DECK, check=True,
    )
    return qmd.with_suffix(".html")


def serve(directory: Path):
    """Serve `directory` on an ephemeral 127.0.0.1 port; return (httpd, port).

    Ephemeral (port 0) sidesteps the fixed-port collisions the old script hit.
    """
    handler = functools.partial(_QuietHandler, directory=str(directory))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def print_pdf(html_url_path: str, pdf: Path, port: int) -> None:
    from playwright.sync_api import sync_playwright

    url = f"http://127.0.0.1:{port}/{html_url_path}?print-pdf"
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(channel="chrome")
        except Exception:
            browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=120_000)
        # KaTeX webfonts must be APPLIED before the snapshot, else math -> Times.
        page.evaluate("async () => { await document.fonts.ready; return true; }")
        # No half-loaded figure.
        page.wait_for_function(
            "() => Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
            timeout=120_000,
        )
        # reveal's print-pdf plugin wraps each slide in a `.pdf-page`; that pagination runs
        # in JS AFTER load. Poll the `.pdf-page` count until it has STARTED (> 0) and SETTLED
        # (unchanged between checks). Without this, page.pdf() can fire before/mid-pagination
        # and emit a single un-paginated page instead of one page per slide.
        prev = -1
        for _ in range(150):            # ~15s ceiling; normally settles in a few ticks
            n = page.evaluate("document.querySelectorAll('.reveal .pdf-page').length")
            if n > 0 and n == prev:
                break
            prev = n
            page.wait_for_timeout(100)
        page.pdf(path=str(pdf), prefer_css_page_size=True, print_background=True)
        browser.close()


def render(qmd: Path, pdf: Path) -> Path:
    html = render_quarto(qmd)
    # URL path of the html relative to the served DECK root (POSIX separators).
    rel = html.resolve().relative_to(DECK).as_posix()
    httpd, port = serve(DECK)
    try:
        print_pdf(rel, pdf, port)
    finally:
        httpd.shutdown()
        httpd.server_close()
    return pdf


def main(argv: list[str]) -> int:
    qmd = Path(argv[1]).resolve() if len(argv) > 1 else DECK / "slides.qmd"
    pdf = Path(argv[2]).resolve() if len(argv) > 2 else qmd.with_suffix(".pdf")
    render(qmd, pdf)
    print(f"✓ {pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
