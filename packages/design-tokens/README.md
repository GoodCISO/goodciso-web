# GoodCISO design tokens

The single source for the corporate site and AWARE. Every value in
`src/tokens.css` is a named token. Components reference tokens, never
literal values.

```
packages/design-tokens/src/tokens.css   the tokens
packages/ui/src/base.css                the component layer
```

The corporate site and the AWARE site **share the token layer and the
component layer**, and differ only by brand overrides and content. A brand
never forks the component CSS; it redefines the ramp, and the accent follows.

---

## Verifying the contrast ratios

`tokens.css` cites a contrast ratio beside almost every semantic token. Those
numbers are **measured, not asserted**, by `contrast.py` at the repository
root:

```bash
python3 build_all.py     # the tokens must be BUILT before they can be measured
python3 contrast.py
```

`contrast.py` reads the **built** CSS in `dist/`, resolves the custom
properties through the real cascade the way a browser would, and checks each
pair against its WCAG 2.2 threshold. It prints one line per check and exits
non-zero if any fail:

```
     PASS   5.29 (need 4.5)  accent-text on bg
     PASS   8.09 (need 3.0)  focus vs bg (>=3)
```

A check that cannot fail is not a check, so two properties of this script
matter more than the numbers it prints:

- It resolves **through the cascade**, not by reading a value in isolation. A
  token's value depends on which rule wins for the theme, and on what it
  references. Reading `--gc-accent-text` out of the file would report the
  AWARE value for the corporate site, which overrides the same ramp.
- It runs against `dist/`, so it measures **what ships**, not what is intended.

### Thresholds

| Check | Minimum | WCAG 2.2 |
|---|---|---|
| text on bg / surface / surface-2 | 4.5 | 1.4.3 Contrast (Minimum), AA |
| muted, subtle, accent-text, link | 4.5 | 1.4.3, AA |
| on-solid on accent-solid | 4.5 | 1.4.3, AA |
| focus vs bg | 3.0 | 1.4.11 Non-text Contrast, AA |
| border-strong vs bg | 3.0 | 1.4.11, AA |

---

## Measured ratios

Every value below was produced by `contrast.py` on 2026-11-20 against the
built output. All 104 checks pass — 13 pairs per theme, in both themes, on
four sites.

`contrast.py` reads the stylesheets **the built page actually loads**, in
document order, and resolves the custom properties through the cascade
with selector specificity. It does not read a hand-picked list of files:
a stylesheet the page loads but the checker does not read is measured
wrong, and that is how the button text colour escaped this check once
already (see the note in `packages/ui/README.md` under Buttons).

### Corporate (`goodciso.org`)

The corporate brand redefines the green ramp in **teal**, so its accent ratios
differ from AWARE's. This is the reason the ratios are measured rather than
read from the stylesheet.

| Pair | Light | Dark |
|---|---|---|
| text on bg | 17.06 | 16.33 |
| text on surface | 17.85 | 15.21 |
| text on surface-2 | 16.30 | 13.86 |
| muted on bg | 7.24 | 7.85 |
| subtle on bg | 4.55 | 7.85 |
| accent-text on bg | 5.29 | 10.82 |
| accent-text on surface | 5.53 | 10.07 |
| link on bg | 5.29 | 10.82 |
| on-solid on accent-solid | 5.53 | 8.09 |
| focus vs bg (≥3) | 5.29 | 8.09 |
| border-strong vs bg (≥3) | 4.55 | 7.85 |

### AWARE (`aware.goodciso.org`), Docs and Demo

These three sites share the token layer unmodified, so their ratios are
identical. AWARE's accent is **Signal green**; the corporate site's is teal.

| Pair | Light | Dark |
|---|---|---|
| text on bg | 17.06 | 15.19 |
| text on surface | 17.85 | 13.86 |
| text on surface-2 | 16.30 | 12.75 |
| muted on bg | 7.24 | 7.30 |
| subtle on bg | 4.55 | 7.30 |
| accent-text on bg | 4.79 | 10.74 |
| accent-text on surface | 5.02 | 9.80 |
| link on bg | 4.79 | 10.74 |
| on-solid on accent-solid | 5.02 | 8.22 |
| focus vs bg (≥3) | 3.15 | 8.22 |
| border-strong vs bg (≥3) | 4.55 | 3.71 |

---

## The two brand traps

Both brands hit the same trap, and the ramp is what absorbs it.

**The brand colour fails AA as text.** GoodCISO teal `#00A896` is **2.85:1** on
the light background and AWARE's Signal green `#22C55E` is **2.18:1**. Both
stay the brand colour for fills, icons and the logomark. The ramp carries
darker steps for anything a person has to read:

| Token | GoodCISO | AWARE | Role |
|---|---|---|---|
| `--gc-accent` | `#00A896` | `#22C55E` | fills, icons, marks |
| `--gc-accent-text` | `#007669` | `#15803D` | accent **as text** (AA) |
| `--gc-accent-solid` | `#007669` | `#15803D` | solid button fill (AA) |

**The focus ring needed the same treatment.** `--gc-focus` uses the accessible
ramp step rather than the brand colour, because the brand colour is below the
3:1 a focus indicator requires. The corporate focus ring is teal-700
(`#007669`, 5.29:1); AWARE's is green-500 (3.15:1 light, 8.22:1 dark).

---

## Rules for using the tokens

1. **No magic numbers in components.** If a value is not a token, it is not
   allowed in `packages/ui/src/base.css`.
2. **Never hard-code a text colour on a brand fill.** `--gc-accent-on-solid`
   exists because a dark accent fill needs dark text and a mid-tone fill needs
   white; hard-coding either one fails AA in the other theme.
3. **A brand overrides the ramp, not the component CSS.** If a component needs
   to differ per brand, the difference belongs in a token.
4. **Contrast is verified, not eyeballed.** Run `contrast.py` after changing
   any token. If a ratio in this file changes, this file changes with it.
