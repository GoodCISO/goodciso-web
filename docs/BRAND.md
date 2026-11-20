# BRAND.md — GoodCISO and AWARE

> The record of what the two marks are, which surfaces each one appears on,
> and why they are kept apart. Written 2026-11-20, in response to the
> question "was the favicon change intended?" — the answer is in §3.

GoodCISO is the **company**. AWARE is the **product it sells**. They share
a component layer, a type scale and a spacing scale, and nothing else.
Every brand decision below follows from that one distinction.

---

## 1. The two brands

| | **GoodCISO** | **AWARE** |
|---|---|---|
| What it is | The company — advisory and engineering practice | The product — open-source control plane for autonomous AI agents |
| Sites | `goodciso.org` | `aware.goodciso.org`, `docs.aware.goodciso.org`, `demo.aware.goodciso.org` |
| Logomark | Teal shield with a G-shaped counter and an amber centre dot | Shield with a checkmark |
| Mark colour | Teal `#00A896` | Signal green `#22C55E` |
| Ground | Navy `#030712` | Midnight `#0B1220` |
| Accent text | `#007669` (5.29:1 on `#F8FAFC`) | `#15803D` (4.79:1) |
| Type | Editorial, light, generous measure | Dense, technical, dark-first |
| Registered mark | "Good CISO" and the shield are trademarks of Good CISO Limited | — |

**The source of truth for the GoodCISO mark is the original artwork:**
`~/projects/good-ciso-logo/good-ciso-logo.png`, a 1024×1024 JPEG. The
mark is *cut* from those pixels (`extract_logo.py`), never redrawn. Its
palette — teal `#00a896`, navy `#030712`, amber `#F5A623` — is recorded in
that project's `README.md`.

---

## 2. Where each mark appears

This is the answer to "what is the intended full set of places the mark
appears". A row marked **missing** is work not yet done.

### GoodCISO (goodciso.org)

| Surface | Asset | State |
|---|---|---|
| Favicon (browsers) | `assets/brand/favicon-goodciso.png` → `/favicon.png` | shipped |
| Favicon (legacy `/favicon.ico`) | `assets/brand/favicon-goodciso.ico` | shipped |
| iOS home-screen icon | `assets/brand/apple-touch-icon.png` | shipped |
| Browser chrome colour | `#030712` (`<meta name="theme-color">`) | shipped |
| Header logomark | `assets/brand/goodciso-shield.png` | shipped |
| Header wordmark | live text: "Good" bold + "CISO" caps | shipped |
| Social / OG image | `assets/brand/generated/og-corporate.png` → `/og.png` | shipped |
| LinkedIn / company avatar | — | **not in this repo** |
| Email signature | — | **not in this repo** |
| Sales deck | `GoodCISO-AWARE-Deck.pptx` (old repo) | **not in this repo** |

### AWARE (aware.goodciso.org, docs…, demo…)

| Surface | Asset | State |
|---|---|---|
| Favicon | `assets/brand/favicon-aware.svg` → `/favicon.svg` | shipped |
| Browser chrome colour | `#0B1220` | shipped |
| Header wordmark | live text: "AWARE" | shipped |
| Social / OG image | `assets/brand/generated/og-aware.png` → `/og.png` | shipped |

### The old repo

`~/projects/goodciso-website` is superseded and is **not** deployed. It is
kept for provenance. Note that it shipped AWARE's mark on the corporate
domain — the header logo was a teal rounded square with a white check and
the wordmark read "AWARE". The 2026-11-16 build inherited that error.

---

## 3. The favicon change of 2026-11-16 — what happened

**It was not intended. It was a defect, and it is fixed.**

| | |
|---|---|
| **Introduced** | `e5f8736` (2026-11-16 21:01) — "feat: GoodCISO + AWARE sites, design system and capability register" |
| **Live on goodciso.org** | 2026-11-16 21:37 → 2026-11-18 12:40 — **~39 hours** |
| **Fixed** | `0aa78e3` (2026-11-18 12:40), then `a7bf229` (18:08) for the artwork itself |
| **Cause** | `build_all.py` copied **one** favicon file to all four sites. The corporate site inherited AWARE's mark. |
| **Secondary cause** | The corporate palette was not overridden, so AWARE's Signal green became the corporate accent as well. |

The old live site's `favicon.svg` (teal shield, teal centre dot) was GoodCISO's
own mark and was correct. It was retired by accident, not by decision.

Alvin was not notified, and should have been. See §6.

---

## 4. Rules

1. **A mark never crosses sites.** The corporate site must never serve
   AWARE's mark, and the AWARE sites must never serve GoodCISO's. A
   corporate favicon that is the product's logo misrepresents the
   relationship between the two companies — and the favicon is what ends up
   in a browser history, a bookmark and a shared link.
2. **GoodCISO's mark is the original artwork.** It is cut from the source
   JPEG, never redrawn. The vector trace in `trace_logo.py` loses the
   G-shaped counter and is not used.
3. **The favicon is on a tile.** The artwork's counter is knocked out to
   transparency for the header, so a transparent favicon would show the G
   against whatever colour the browser tab happens to be. The navy tile
   fixes the backdrop.
4. **The brand colour is for fills, not text.** Teal `#00A896` is 2.85:1 on
   `#F8FAFC` and fails AA as text. It stays the brand colour for the mark
   and for fills; the ramp carries darker steps for anything readable.
5. **A brand colour override belongs in both themes.** A rule that applies
   in only one theme is a bug waiting for a theme switch.
6. **Shared tokens carry a green ramp.** The token names (`--gc-green-*`) are
   shared across brands for component-level reuse; each brand
   overrides the *values*. So the presence of green in `tokens.css` is not
   a defect — but a corporate site whose *resolved* accent is green is.
7. **Every surface carries its own brand, and the build proves it.** The
   favicon, the social card and the accent colour are all checked against
   the committed brand assets by content, not by filename. A surface that
   is missing fails the build as loudly as one that is wrong: a shared
   link with no card renders as a bare URL, and the brand never arrives.

---

## 5. Checks

### Automated — runs in CI before every deploy

`qa.py` carries a brand guard that runs against the **built output**, not
the source, and fails the deploy on any of:

- the corporate `/favicon.png` is not the committed GoodCISO brand asset;
- the corporate `/favicon.png` is missing;
- the corporate `--gc-accent`, `--gc-accent-text` or `--gc-accent-solid`
  resolves to AWARE's Signal green in **either** theme;
- `--gc-hero-glow` is a literal rather than derived from the accent, or
  is AWARE's Signal green;
- an AWARE site's `/favicon.svg` is missing or is not the AWARE mark;
- the corporate `/og.png` is missing or is not the GoodCISO social card;
- an AWARE site's `/og.png` is missing or is not the AWARE social card;
- a page carries no `og:image`, or one that is off-site or not in the build.

The accent check resolves the cascade rather than grepping for a hex
string, because `tokens.css` is the shared base layer and legitimately
carries a green ramp that `brand.css` overrides. The card check compares
by content rather than by filename, because the build copies each card to
the same name (`/og.png`) on every site — only the bytes can tell the two
brands apart.

`test_brand_guard.py` proves the guard can fail. It breaks each condition
in turn and asserts the guard fires — a check that cannot fail is not a
check.

```bash
python3.12 build_all.py && python3.12 qa.py && python3.12 test_brand_guard.py
```

### Contrast

```bash
python3.12 build_all.py && python3.12 netlify_config.py && python3.12 contrast.py
```

Resolves the built CSS through the real cascade and checks every
foreground/background pair against its WCAG 2.2 threshold, in both themes,
on all four sites.

### Manual — after any brand change

1. Open the corporate site and confirm the tab shows the **teal shield with
   the amber dot**, not a green tick.
2. Confirm the same on `aware.goodciso.org` — the tab shows the **green
   shield-and-check**.
3. Confirm the corporate header shows the teal shield and the "Good CISO"
   wordmark.
4. Toggle the theme on both sites. The corporate dark theme must stay
   GoodCISO navy; the AWARE sites stay midnight.
5. `curl -sI https://goodciso.org/favicon.ico` and
   `.../apple-touch-icon.png` must both return 200.
6. `curl -sI https://goodciso.org/og.png` must return 200, and
   `curl -s https://goodciso.org/ | grep og:image` must point at
   `goodciso.org`. Paste a goodciso.org link into a chat and confirm the
   preview card shows the **GoodCISO** mark, not AWARE's.

### Regenerating the brand assets

```bash
python3.12 make_brand_assets.py
```

The generator needs Pillow, and headless Chrome for the AWARE set. It is
**not** run in CI — the runner installs no packages — so the two Open Graph
cards are committed to the repository and the build copies them. If the
mark or the palette changes, re-run the generator and commit the new
cards alongside the change, or CI will ship the old card.

---

## 6. Notification

**A change to the GoodCISO corporate brand notifies the operator.** This
covers the mark, the palette, the wordmark, the favicon set, the browser
chrome colour, and the tone of the copy on `goodciso.org`.

The reasoning: the corporate brand is the company's public face and a
registered trademark. A change to it is a business event, not a design
detail — and it was made silently for ~39 hours in November 2026, which is
how the operator found out that the favicon had changed.

Notification goes to the operator on Telegram (`899522722`). It does not
require approval: the operator is told what changed, with the before and
after, and the reason.

This rule lives in `~/.hermes/profiles/designer/AGENTS.md` so it does not
depend on anyone remembering it.
