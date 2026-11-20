# The GoodCISO component layer

`src/base.css` is the component layer. It is shared by every site: the
corporate site, the AWARE product site, the docs site and the playground.

```
packages/design-tokens/src/tokens.css   the tokens (colours, type, space)
packages/ui/src/base.css                this layer (the components)
build.py                                 each site's brand overrides
```

**The token layer decides the values. This layer decides the structure.**
A brand never forks the component CSS — it redefines the ramp, and the
components follow. That is the whole reason the two brands can look
different without looking unrelated.

This file is the specification. The CSS is the implementation; where the two
disagree, the CSS is the truth and this file is the bug.

---

## Why this file exists

The previous site shipped four components with no specification at all —
`arch-flow`, `stats-bar`, `compliance-grid` and `.trust-badge-note` existed
in the stylesheet and in no document. Nobody could tell whether they were
correct, and a coder could not know when it was safe to use one.

This file covers all **60** classes in the layer. A component that is not
listed here does not belong in the layer.

The count is enforced, not asserted: `qa.py` fails the build if a class
appears in the layer and not in this file, and if a class appears in this
file and not in the layer.

---

## Accessibility

| Class | What it is |
|---|---|
| `skip-link` | The "Skip to content" link, the first focusable thing on every page. Off-screen until it takes focus, then pinned to the top-left |

`skip-link` is not a component so much as an obligation: every page has
one, it is the first focusable element, and it must be reachable by
keyboard before anything else. It is off-screen with
`position: absolute; left: -9999px` and moves to `left: 0` on `:focus`.
Never remove it, and never give it `display: none` — that removes it
from the tab order as well as from the screen.

---

## The rules that hold everywhere

1. **No magic numbers.** Every value in a component is a token. The
   exceptions are the few values that are not a scale value and are
   listed under **The raw values, and why** below. Do not add to that
   list without a reason in the same sentence.
2. **No raw colour in a component.** The layer contains exactly one
   literal hex, `#FFFFFF`, and it is the fallback for
   `--gc-accent-on-solid`. It is scoped to the light theme: it must not
   reach the dark theme, where the fill is the bright brand colour and
   needs the dark text the token layer provides.
3. **Brands override tokens, never components.** If a component needs to
   differ per brand, the difference belongs in a token.
4. **Contrast is measured, not assumed.** `contrast.py` resolves the
   built CSS and checks every pair against WCAG 2.2. A token change that
   breaks a ratio fails the build.
5. **A new component is added with its spec.** The CSS and this file land
   together. That is the rule whose absence caused the drift above.

### The raw values, and why

A rule that says "no magic numbers" and then has exceptions nobody
wrote down is a rule that decays. These are the raw values in the layer
and the reason each one is allowed:

| Value | Where | Why it is not a token |
|---|---|---|
| `1px` | hairline borders | A hairline is a device-pixel line, not a step on the 4px scale |
| `2px` | focus `outline-offset`, underline thickness | The offset is the gap between the ring and the element, not a spacing step. The outline's own width is `--gc-focus-width` |
| `3px` | `text-underline-offset` | Matches the underline's offset to the text, not a spacing step |
| `5px` | inline code padding | A fixed optical inset around a code run, smaller than any space step |
| `6px` | the status pill's dot | The dot's diameter; it is not a box and must not scale with the space scale |
| `12px` | header `backdrop-filter` blur | A blur radius, not a length in the layout |
| `26px` × `30px` | the logo mark | The artwork's own aspect ratio |
| `36px` | the theme toggle | A square icon target; the WCAG floor is 24px and the button floor is 44px, and this is neither |
| `44px` | the button's `min-height` | The WCAG 2.2 target size (AAA 2.5.5; AA is 24px) |
| `1.125rem` | the wordmark | The wordmark's type size, set to the artwork's proportions rather than to the type scale |
| `0.9em` | `code`, `kbd`, `pre` | A relative reduction from the surrounding type, so it follows whatever the reader's size is |
| `160px` | the footer's `auto-fit` minimum | A track minimum for a fluid grid, not a layout width |

If you need a new one of these, add it here in the same commit as the
CSS. That is the whole point of the list.

---

## Layout

| Class | What it is | Notes |
|---|---|---|
| `gc-container` | The page's content width | `max-width: var(--gc-container)`, centred, `--gc-space-6` inline padding |
| `gc-container-narrow` | A narrower measure | For long-form prose that should not run the full width |
| `gc-section` | A page band | `--gc-space-20` vertical padding |
| `gc-section-tight` | A page band, less air | `--gc-space-12`. Use between related bands, not between sections that stand alone |
| `gc-measure` | A reading measure | `max-width: 68ch`. Apply to prose, never to a grid |
| `gc-center` | Centre the text | Use once per page, on a closing call to action. The rest of the page is left-aligned |

**Section rhythm.** A page is a sequence of `gc-section` bands with
`gc-section-tight` used only between bands that continue the same thought.
Alternating the two without a reason reads as a rhythm mistake.

---

## Grids

`.gc-grid-N` is a **column count**, and the layout honours it.

| Class | Columns | Used for |
|---|---|---|
| `gc-grid` | 1 (base) | Always pair with a count class |
| `gc-grid-2` | 2 | Two-up content; a 2×2 of service cards |
| `gc-grid-3` | 3 | The capability grids |
| `gc-grid-4` | 4 | Wide card rows |
| `gc-grid-5` | 5 | The T0–T4 tier ladder — five levels that read as a progression |

**The collapse ladder is chosen so no grid strands a single card.** A last
row holding one card looks like a mistake, so the number of columns at each
breakpoint is chosen against the number of items the grid actually holds:

```
5 items -> 5, 3, 1     (4 and 2 leave one card alone)
4 items -> 4, 2, 1     (3 leaves one card alone)
3 items -> 3, 1        (2 leaves one card alone)
6 items -> 6, 3, 2, 1  (5 and 4 leave one card alone)
```

At ≤1100px `gc-grid-5` goes to 3. At ≤900px `gc-grid-4` goes to 2,
`gc-grid-5` to 1, and `gc-grid-3` to 1 — **not** 2, because a three-up row
of three items at two columns leaves the third card alone. At ≤620px
everything is one column.

**Before adding a grid, count the items.** The class must divide evenly at
every breakpoint, or the last row must hold two or more.

---

## Header

| Class | What it is |
|---|---|
| `gc-header` | Sticky bar, translucent with a backdrop blur, `--gc-header-h` tall |
| `gc-header-inner` | The flex row inside it |
| `gc-logo` | The brand lockup — the mark plus the live wordmark |
| `gc-logo-mark` | The mark image. 26×30, `object-fit: contain` |
| `gc-wordmark` / `gc-wordmark-good` | The wordmark as text, so it stays selectable. "Good" is the heavier weight |
| `gc-nav` | The nav links |
| `gc-nav-toggle` | The menu button, shown at ≤900px |
| `gc-header-actions` | Theme toggle and the header CTA |
| `gc-theme-toggle` | 36×36 icon button |

**The wordmark is text, not an image.** The mark is the authentic artwork, so
it is an image; the wordmark is live text so it stays crisp and selectable.

**Current page** is marked with `aria-current="page"` on the link — never
with a class.

### The focus ring

`:focus-visible` paints a 2px `--gc-focus` outline with `outline-offset:
2px`. That offset puts the ring **outside** the element's border box, so the
ring is drawn on the surface the element *sits on* — the card behind a link,
the translucent header behind a button — not on the page background.

That is why `contrast.py` checks `--gc-focus` against `--gc-bg`,
`--gc-surface` **and** `--gc-surface-2`, each at 3:1 (WCAG 2.2 SC 1.4.11
Non-text Contrast). A ring that is fine on the page background can be
invisible on a card: in the dark themes there are colours that pass against
the background and fail against the surface, and the surface check is what
catches them.

**The brand colour is not the focus colour.** GoodCISO teal `#00A896` is
2.85:1 on the light background and fails the 3:1 a focus indicator needs, so
`--gc-focus` uses the darker ramp step (`#007669`). The brand colour still
drives the mark and the accent fill.

**Never remove the outline.** `outline: none` without a replacement is a
WCAG failure, and it is invisible in a screenshot review.

---

## Buttons

| Class | What it is |
|---|---|
| `gc-btn` | The base. 44px minimum height, `--gc-space-3`/`--gc-space-5` padding |
| `gc-btn-primary` | Filled with the accent. One per view |
| `gc-btn-secondary` | Surface with a strong border |
| `gc-btn-ghost` | Text only, no border |
| `gc-btn-lg` | The larger variant for a hero |

**The text colour on a primary button comes from `--gc-accent-on-solid`,
never from a literal.** A dark accent fill needs dark text; a mid-tone fill
needs white. Hard-coding either one fails AA in the other theme. The
corporate theme sets it per theme; the shared layer provides `#FFFFFF` as a
fallback.

**The fallback is scoped to the light theme, and it must stay that way.**
The layer used to declare it as `:root, [data-theme="light"]`. Because
`:root` and `[data-theme="dark"]` have the same specificity and `base.css`
loads after `tokens.css`, the dark theme inherited the light theme's
white — and every solid button on AWARE, the docs site and the demo
rendered **white on Signal green, 2.28:1**, where AA needs 4.5:1.

The rule that fixes it: **a fallback belongs where it is used, not on the
root.** `:root` matches every theme; only `:root:not([data-theme="dark"])`
means "the light theme, or no theme at all". A fallback on `:root` will
reach the dark theme and fight the token that owns it.

`contrast.py` now reads the stylesheets the built page loads, so this
class of bug fails the build rather than shipping.

**44px is not decoration.** It is the WCAG 2.2 target size (AAA 2.5.5; the AA
minimum is 24px). Do not reduce it, and do not put a smaller control next to
a button of this size.

**One primary per view.** Two primary buttons on a page mean neither is
primary.

---

## Cards and content

| Class | What it is |
|---|---|
| `gc-card` | A surface with a border and `--gc-space-6` padding |
| `gc-eyebrow` | The small uppercase label above a heading |
| `gc-list` | A bulleted list |
| `gc-checklist` | A list with a ✓ marker, in the accent colour |
| `gc-code` | A code block on a dark surface, horizontally scrollable |
| `gc-table` | A data table |
| `gc-table-wrap` | The scroll container for a wide table |
| `gc-muted` | De-emphasised text |
| `gc-callout` | A bordered note. Its `strong` is the title |
| `gc-callout-warn` / `gc-callout-danger` | The other two severities |

**A callout's `strong` is always the title**, displayed as a block above the
body. A callout without one is a paragraph with a border.

---

## Status — the honesty components

Two families, and they are not interchangeable.

**`gc-badge`** — an implementation state. This is the capability register
rendered.

| Class | State |
|---|---|
| `gc-badge-shipped` | Shipped |
| `gc-badge-partial` | Partially shipped |
| `gc-badge-roadmap` | Not shipped |
| `gc-badge-demo` | A demonstration, not the product |

**`gc-status`** — an engine decision, with a coloured dot.

| Class | Decision |
|---|---|
| `gc-status-allow` | ALLOW |
| `gc-status-deny` | DENY |
| `gc-status-audit` | AUDIT |
| `gc-status-none` | NO_POLICY |

**A badge states what exists; a status states what a decision was.** Never
use one for the other. If a page needs to say "this capability is not
shipped", that is a badge, and the copy must say so in words as well — the
badge is not the disclosure.

---

## Hero

| Class | What it is |
|---|---|
| `gc-hero` | The page opener. Carries the brand glow |
| `gc-hero h1` | The headline, `max-width: 18ch` in the shared layer |
| `gc-hero-sub` | The standfirst, `--gc-text-lg`, 62ch measure |
| `gc-hero-actions` | The CTA row |

**The glow is derived from the accent** (`color-mix(in srgb, var(--gc-accent)
10%, transparent)`), so it follows the brand in every theme. It must never
be written as a literal — that is how a green glow ended up behind a teal
logomark. `qa.py` fails the build if it is a literal.

**A brand may override the hero's `max-width`** for its own measure; the
corporate site uses 16ch.

---

## Footer

| Class | What it is |
|---|---|
| `gc-footer` | The footer band |
| `gc-footer-grid` | The column layout. `auto-fit minmax(160px, 1fr)` — a footer is fluid by nature, unlike a content grid |
| `gc-footer h4` | A column heading, uppercase and tracked |
| `gc-footer-bottom` | The legal line, split by `justify-content: space-between` |

---

## Utilities

| Class | What it does |
|---|---|
| `gc-mt-4`, `gc-mt-6`, `gc-mt-8`, `gc-mt-12` | Margin-top, in space tokens |
| `gc-mb-0` | Removes the bottom margin |
| `gc-center` | Centre the text |
| `gc-measure` | 68ch reading measure |
| `gc-flex` | Flex row |

Utilities exist for the one-off adjustment. If a page needs a second one,
the component needs a variant instead.

---

## Spacing and type

Everything comes from the token layer:

- **Space** is a 4px scale: `--gc-space-1` (4px) through `--gc-space-24`
  (96px). Section padding is `--gc-space-20`; the tight variant is
  `--gc-space-12`.
- **Type** runs `--gc-text-xs` (12px) to `--gc-text-5xl` (48px), with
  `--gc-leading-tight` for headings and `--gc-leading-normal` for body copy.
- **Radius**: `--gc-radius-sm` through `--gc-radius-xl`, plus
  `--gc-radius-full` for pills.

The measured ratios for every text/background pair are in
`../design-tokens/README.md`.

---

## Adding a component

1. Write the CSS in `src/base.css`, under a section comment, using tokens
   only.
2. Add it to this file, with what it is and when to use it.
3. If it introduces a new colour, add the token to `tokens.css` with its
   measured contrast ratio, and add the pair to `contrast.py`'s checks.
4. If it is a new colour on a surface, add the pair to `contrast.py` — the
   check resolves the built CSS, so a token that is never checked is a token
   nobody has verified.

A component that is not in this file does not exist yet.
