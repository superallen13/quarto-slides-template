# Conventions

How to author a deck with this template, and the sharp edges it files down for you.

## The one rule

Edit **`slides.qmd`** and nothing else. `theme/`, `assets/`, and `tools/` are scaffolding
you configure once. One `##` heading starts one slide.

> Gotcha handled: do **not** put text or an HTML comment *before* the first `##` — Quarto
> turns it into a blank slide. Keep notes-to-self inside the YAML header (`#` comments) or
> inside a slide.

## Layout blocks

**Two-column** (portrait figure left, text right — sharpest for tall images):

```markdown
:::::: {.columns}
::::: {.column width="46%"}
![](assets/demo/placeholder.svg)
:::::
::::: {.column width="54%"}
- your bullets
:::::
::::::
```

**Stacked** (wide figure on top, bullets below — best for wide diagrams). Tag the image
`{.bigfig}` to span full width, or `{.centerfig}` to centre it under a sensible height cap:

```markdown
![](assets/demo/placeholder.svg){.centerfig}

- your bullets
```

**Section divider** (full-bleed wave). The `[01]{.chapnum}` is an optional accent number;
`::: pubtitle` / `::: pubmeta` are the optional title / byline lines:

```markdown
## [01]{.chapnum} Section Title {.divider background-image="assets/divider.svg" background-size="cover"}

::: pubtitle
Optional section subtitle
:::
::: pubmeta
Optional byline · venue
:::
```

**Closing slide** (white text over the accent wave):

```markdown
## Thank You {.oncolor background-image="assets/thankyou.svg" background-size="cover" data-state="oncolor"}
```

## Inline blocks

| Block | Use |
|-------|-----|
| `::: notes` | Speaker notes — never shown on the slide; appear in the PDF and presenter view. Put "how to edit this" detail here and keep the visible slide clean. |
| `::: transition` | A short accent hand-off line that sits low on the slide. |
| `::: caption` | A grey source/citation line, auto-pinned to the slide foot (clear of the page number). |

## Math

Client-side KaTeX, vendored under `assets/katex/`. Write `$...$` inline or `$$...$$` for a
block. `\boldsymbol`, `\mathcal`, `\operatorname`, `cases`, etc. all render. The PDF driver
waits for the KaTeX webfonts, so math never ships as a Times fallback.

## House style

- **Bold = a keyword**, rendered in the accent colour. Don't bold whole sentences.
- **No em-dash.** Use a spaced "—"-free phrasing, a colon, or parentheses.
- **Title Case** headings: capitalise the entities, lowercase articles/short prepositions.
- Prefer splitting a dense slide across two (repeat the title) over overflowing one.

## Branding

A brand is a **bundle**: a colour layer (`theme/_brand-<name>.scss`) plus a logo and two
wave images (`assets/<name>-logo.*`, `assets/<name>-divider.svg`, `assets/<name>-thankyou.svg`).
`tools/init.py` flips `slides.qmd` between brands (theme line + logo + wave paths move
together). Colour alone does not recolour the waves — they are SVG files, so a full brand
swaps the assets too.

Wave SVGs are 1280×720 with `preserveAspectRatio="xMidYMid slice"`; the slide uses
`background-size="cover"`, which fits 16:9 art onto the 16:9 page exactly. (This sidesteps a
Chrome-print bug that clips a *stretched* CSS background to a left sliver — see below.)

## Gotchas handled for you (in theme/_base.scss)

You shouldn't hit these, but here's what the base stylesheet is quietly fixing:

- **Two columns** stay side-by-side — Quarto resets `.columns` to inline; the theme forces flex.
- **Figures don't clip bullets** — inline images are height-capped so they can't push content
  off the page (and off the printed PDF).
- **Captions pin to the foot** in both live and print, never floating up under short content.
- **Dividers & the closing wave** bleed to all four edges in the PDF (cover-fit background).
- **The slide number** sits bottom-right with no dark pill, in both the live deck and the PDF.
- **Arrow/approx glyphs** (`↑ ≈ →`) get a Helvetica fallback so the print path doesn't
  substitute a serif glyph (Nunito lacks them).

## Bonus components

- `<div class="claimrow">` of `<div class="claim">` cards — parallel takeaways in a row.
- `<table class="cmptable">` — a booktabs-style comparison table (mark the highlighted row
  with `class="ours"`; use `<span class="yes/no">✓/✗</span>` for marks).
- `::: agenda` with `[item]{.here}` — a "you are here" contents list.
