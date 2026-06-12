"""Integration test for tools/render_pdf.py: a real Quarto render + Playwright print,
asserting the two things the old lottery raced on -- KaTeX math (not Times) and a
loaded figure -- actually land in the PDF. Skipped unless quarto, the poppler CLIs,
and playwright are all available."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

DECK = Path(__file__).resolve().parent.parent
FIXTURE = DECK / "tests" / "fixtures" / "math_min.qmd"

_missing = [t for t in ("quarto", "pdffonts", "pdfinfo", "pdfimages") if not shutil.which(t)]
try:
    import playwright  # noqa: F401
except Exception:
    _missing.append("playwright")

pytestmark = pytest.mark.skipif(bool(_missing), reason=f"missing tools: {_missing}")


def _run(*args):
    return subprocess.run(args, capture_output=True, text=True)


def test_render_pdf_embeds_katex_and_figure(tmp_path):
    pdf = tmp_path / "out.pdf"
    proc = _run(sys.executable, str(DECK / "tools" / "render_pdf.py"),
                str(FIXTURE), str(pdf))
    assert proc.returncode == 0, f"render_pdf.py failed:\n{proc.stdout}\n{proc.stderr}"
    assert pdf.exists() and pdf.stat().st_size > 8000, "PDF missing or blank"

    # Math rendered with real KaTeX faces, NOT a Times fallback (0 faces = the old bug).
    fonts = _run("pdffonts", str(pdf)).stdout
    katex_faces = sum(1 for line in fonts.splitlines() if "katex" in line.lower())
    assert katex_faces >= 4, f"expected KaTeX faces, got {katex_faces}:\n{fonts}"

    # The figure loaded (image path didn't lose its race).
    images = _run("pdfimages", "-list", str(pdf)).stdout.splitlines()
    image_rows = [ln for ln in images[2:] if ln.strip()]
    assert len(image_rows) >= 1, f"no embedded image:\n{chr(10).join(images)}"

    # One slide per page (at least the two we wrote).
    info = _run("pdfinfo", str(pdf)).stdout
    pages = next((int(ln.split()[1]) for ln in info.splitlines() if ln.startswith("Pages:")), 0)
    assert pages >= 2, f"expected >=2 pages, got {pages}"
