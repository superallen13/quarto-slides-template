"""Unit tests for tools/init.py brand-switching (pure string transforms, no render)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import init  # noqa: E402

# Neutral default: no `logo:` line (the neutral deck ships no corner logo).
SAMPLE = '''---
title: "X"
author: "Y"
format:
  revealjs:
    #   theme: [default, theme/_base.scss, theme/_brand-uq.scss]
    theme: [default, theme/_base.scss]
    title-slide-attributes:
      data-background-image: assets/divider.svg
      data-background-size: cover
---

## [01]{.chapnum} D {.divider background-image="assets/divider.svg" background-size="cover"}

## Thank You {.oncolor background-image="assets/thankyou.svg" background-size="cover" data-state="oncolor"}
'''


def test_switch_to_uq_then_back_is_a_clean_round_trip():
    uq = init.set_brand(SAMPLE, "uq")
    assert "\n    theme: [default, theme/_base.scss, theme/_brand-uq.scss]\n" in uq
    # neutral had no logo; switching to uq INSERTS one right after the theme line
    assert "\n    logo: assets/uq-logo.png\n" in uq
    assert "assets/uq-divider.svg" in uq and "assets/uq-thankyou.svg" in uq
    # both the cover background and the divider slide swap to the UQ wave
    assert "assets/divider.svg" not in uq

    back = init.set_brand(uq, "neutral")
    assert "\n    theme: [default, theme/_base.scss]\n" in back
    assert not re.search(r'(?m)^\s*logo:', back)        # neutral carries NO corner logo
    assert "assets/uq-logo.png" not in back
    assert "assets/uq-divider.svg" not in back
    assert "assets/divider.svg" in back                  # swapped back to neutral wave


def test_commented_example_line_is_never_rewritten():
    # the `#   theme: ...` example line must survive a brand switch verbatim
    out = init.set_brand(SAMPLE, "uq")
    assert "    #   theme: [default, theme/_base.scss, theme/_brand-uq.scss]\n" in out


def test_set_field_replaces_title_and_author():
    out = init.set_field(SAMPLE, "title", "My Talk")
    out = init.set_field(out, "author", "Me<br>Somewhere")
    assert 'title: "My Talk"' in out
    assert 'author: "Me<br>Somewhere"' in out
