# quarto-slides-template

A plain-text, single-file [Quarto](https://quarto.org) + reveal.js template for academic
talks (thesis / seminar / conference). Write your whole talk in one markdown file, preview
it live as you type, and export a deterministic PDF.

- **Plain text, single file.** One `slides.qmd` is the whole talk: easy to edit, diff, and
  version-control. What you write is what renders.
- **Live preview.** `quarto preview` hot-reloads the deck in your browser on every save.
- **Crisp math.** Client-side KaTeX (vendored, offline); the PDF export waits for the
  webfonts, so formulas never fall back to Times.
- **Deterministic PDF.** `python tools/render_pdf.py`: one pass, no render lottery.
- **Lightweight.** Quarto + Python + Playwright. No node, npm, or decktape.

## Quickstart

**1. Get the template.** On GitHub click **Use this template → Create a new repository**
(or `git clone` this repo), then open a terminal in the folder.

```bash
# 2. Install. Quarto must already be installed: https://quarto.org/docs/get-started/
pip install -r requirements.txt
# (only if you don't have Google Chrome installed:)
#   playwright install chromium

# 3. Make it yours: set title/author, pick a brand, optionally clear the demo
python tools/init.py

# 4. Preview live — opens in your browser and hot-reloads on every save
quarto preview slides.qmd

# 5. Export the final PDF
python tools/render_pdf.py            # -> slides.pdf
```

## Writing your slides

Everything is in **`slides.qmd`**, in plain markdown. The basics:

```markdown
## My Slide Title          <!-- one `##` starts a new slide -->

- A bullet, with a **keyword** in the accent colour
- Inline math $E = mc^2$, or a display block:

$$\hat{A}_i = \frac{R_i - \mathrm{mean}(R)}{\mathrm{std}(R)}$$

![](assets/demo/placeholder.svg)     <!-- a figure; drop your own image in assets/ -->

::: notes
Speaker notes — never shown on the slide, but kept in the PDF and presenter view.
:::
```

Save the file and the live preview reloads instantly. The shipped `slides.qmd` is itself
the manual: every slide demonstrates a feature and its `::: notes` explains how to edit it.
For two-column layouts, section dividers, captions, comparison tables, and the house style,
see **[`docs/CONVENTIONS.md`](docs/CONVENTIONS.md)**.

## Branding

The deck ships **neutral** by default. A brand is a small bundle — a colour layer plus a
logo and two wave images — and `init.py` wires them together for you:

```bash
python tools/init.py --brand uq        # University of Queensland purple + waves
python tools/init.py --brand neutral   # back to the neutral default
```

To add **your own** brand: copy `theme/_brand-uq.scss` to `theme/_brand-<you>.scss` and
change the colours; drop in your `assets/<you>-logo.*`, `assets/<you>-divider.svg`, and
`assets/<you>-thankyou.svg`; then add a `<you>` entry to the `BRANDS` map in `tools/init.py`.
See `docs/CONVENTIONS.md` for the wave-SVG recipe.

## Project layout

```
slides.qmd            ← the single content source (edit this)
theme/_base.scss      neutral theme + structural fixes baked in as CSS
theme/_brand-uq.scss  UQ colour layer (example of how to brand)
assets/               vendored KaTeX, slide numbering, logo + wave SVGs, demo placeholder
tools/render_pdf.py   deterministic Quarto→PDF (Playwright)
tools/init.py         scaffold: brand / title / author / clear
docs/CONVENTIONS.md   authoring conventions + the gotchas handled for you
tests/                a render regression test (math + figure land in the PDF)
```

## Asset licensing

The code is MIT-licensed (see `LICENSE`). The **University of Queensland logo and wave
assets** (`assets/uq-*`) are UQ's property, included here only as a working brand example —
**replace them with your own** institution's assets for any non-UQ use.
