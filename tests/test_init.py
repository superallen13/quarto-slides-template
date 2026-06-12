"""Unit tests for tools/init.py brand-switching (pure string transforms, no render)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import init  # noqa: E402

SAMPLE = '''---
title: "X"
author: "Y"
format:
  revealjs:
    #   theme: [default, theme/_base.scss, theme/_brand-uq.scss]
    theme: [default, theme/_base.scss]
    logo: assets/logo-placeholder.svg
---

## [01]{.chapnum} D {.divider background-image="assets/divider.svg" background-size="cover"}

## Thank You {.oncolor background-image="assets/thankyou.svg" background-size="cover" data-state="oncolor"}
'''


def test_switch_to_uq_then_back_is_a_clean_round_trip():
    uq = init.set_brand(SAMPLE, "uq")
    # the REAL theme line (indented, no leading #) carries the brand layer
    assert "\n    theme: [default, theme/_base.scss, theme/_brand-uq.scss]\n" in uq
    assert "logo: assets/uq-logo.png" in uq
    assert "assets/uq-divider.svg" in uq and "assets/uq-thankyou.svg" in uq
    assert "assets/logo-placeholder.svg" not in uq

    back = init.set_brand(uq, "neutral")
    assert "\n    theme: [default, theme/_base.scss]\n" in back
    assert "logo: assets/logo-placeholder.svg" in back
    # no UQ assets leak back through (the commented example line is left untouched)
    assert "assets/uq-logo.png" not in back
    assert "assets/uq-divider.svg" not in back and "assets/uq-thankyou.svg" not in back


def test_commented_example_line_is_never_rewritten():
    # the `#   theme: ...` example line must survive a brand switch verbatim
    out = init.set_brand(SAMPLE, "uq")
    assert "    #   theme: [default, theme/_base.scss, theme/_brand-uq.scss]\n" in out


def test_set_field_replaces_title_and_author():
    out = init.set_field(SAMPLE, "title", "My Talk")
    out = init.set_field(out, "author", "Me<br>Somewhere")
    assert 'title: "My Talk"' in out
    assert 'author: "Me<br>Somewhere"' in out
