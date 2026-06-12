#!/usr/bin/env python3
"""Scaffold a talk from this template.

Sets the deck's brand (neutral or uq), title, and author by editing slides.qmd in
place — the theme layer list, the `logo:` field, and the divider / thank-you
`background-image=` paths all move together, so you don't have to hunt for them.

    python tools/init.py                         # interactive
    python tools/init.py --brand uq              # just switch brand
    python tools/init.py --brand neutral \
        --title "My Talk" --author "Me<br>Somewhere"
    python tools/init.py --clear                 # also reset slides to a skeleton

Re-runnable: switch brand as often as you like.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

DECK = Path(__file__).resolve().parent.parent
SLIDES = DECK / "slides.qmd"

# A brand bundles a colour layer + a logo + the two wave images. To add your own,
# copy theme/_brand-uq.scss and the assets/<name>-*.{png,svg}, then add an entry here.
BRANDS = {
    "neutral": {
        "theme": "[default, theme/_base.scss]",
        "logo": "assets/logo-placeholder.svg",
        "divider": "assets/divider.svg",
        "thankyou": "assets/thankyou.svg",
    },
    "uq": {
        "theme": "[default, theme/_base.scss, theme/_brand-uq.scss]",
        "logo": "assets/uq-logo.png",
        "divider": "assets/uq-divider.svg",
        "thankyou": "assets/uq-thankyou.svg",
    },
}

SKELETON = """\
## Your First Slide

- Replace this with your content
- One `##` heading starts one slide
- **Bold** is a keyword in the accent colour

::: notes
Speaker notes go here — they don't show on the slide.
:::
"""


def set_brand(text: str, brand: str) -> str:
    b = BRANDS[brand]
    # theme list — match the real YAML line, never the commented example (`#   theme:`)
    text = re.sub(r'(?m)^(\s*)theme:\s*\[[^\]]*\]', rf'\1theme: {b["theme"]}', text)
    text = re.sub(r'(?m)^(\s*)logo:\s*\S+', rf'\1logo: {b["logo"]}', text)
    text = re.sub(r'assets/(?:\w+-)?divider\.svg', b["divider"], text)
    text = re.sub(r'assets/(?:\w+-)?thankyou\.svg', b["thankyou"], text)
    return text


def set_field(text: str, field: str, value: str) -> str:
    # replace `field: "..."` in the YAML header (value may contain <br>, ·, etc.)
    pat = rf'(?m)^({field}:\s*)".*"'
    if re.search(pat, text):
        return re.sub(pat, lambda m: f'{m.group(1)}"{value}"', text, count=1)
    return text


def clear_slides(text: str) -> str:
    # keep the YAML header (up to and including the closing ---), replace the body
    m = re.match(r'(?s)^(---\n.*?\n---\n)', text)
    head = m.group(1) if m else ""
    return head + "\n" + SKELETON


def main(argv=None):
    ap = argparse.ArgumentParser(description="Scaffold a talk from this template.")
    ap.add_argument("--brand", choices=sorted(BRANDS))
    ap.add_argument("--title")
    ap.add_argument("--author")
    ap.add_argument("--clear", action="store_true", help="reset slides to a one-slide skeleton")
    args = ap.parse_args(argv)

    interactive = not any([args.brand, args.title, args.author, args.clear])
    if interactive:
        args.title = input("Talk title: ").strip() or None
        args.author = input("Author line (HTML ok, e.g. Name<br>Affiliation): ").strip() or None
        b = input(f"Brand {sorted(BRANDS)} [neutral]: ").strip().lower() or "neutral"
        args.brand = b if b in BRANDS else "neutral"
        args.clear = input("Clear demo slides to a skeleton? [y/N]: ").strip().lower() == "y"

    text = SLIDES.read_text()
    if args.clear:
        text = clear_slides(text)
    if args.title:
        text = set_field(text, "title", args.title)
    if args.author:
        text = set_field(text, "author", args.author)
    if args.brand:
        text = set_brand(text, args.brand)
    SLIDES.write_text(text)

    print(f"✓ updated {SLIDES.relative_to(DECK)}"
          + (f"  brand={args.brand}" if args.brand else "")
          + ("  (slides cleared)" if args.clear else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
