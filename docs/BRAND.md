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

The old repo's `favicon.svg` was a **simplified** version of this mark — a
solid teal shield with a teal centre dot and no G counter. It is evidence
that the teal-and-navy palette was GoodCISO's; it is **not** the artwork.
The distinction matters because the mark shipped today carries the G counter
and the **amber** dot, which the old favicon never had. See §3.

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
| LinkedIn / company avatar | `assets/brand/generated/linkedin-avatar-goodciso.png` | shipped 2026-11-20 (LinkedIn CDN: `goodciso_logo`) |
| LinkedIn / company cover | `assets/brand/generated/linkedin-cover-goodciso.png` | shipped 2026-11-20 (LinkedIn CDN: `goodciso_cover`) |
| GitHub org avatar | `github.com/GoodCISO` | shipped — teal shield with amber dot |
| Email signature | — | **no mark** — see below |
| Sales deck | `GoodCISO-AWARE-Deck.pptx` (old repo) | **no mark** — see below |
| X / Twitter banner | `x.com/goodciso` | **no mark** — see below |
| YouTube channel avatar | `youtube.com/@goodciso` | **no mark** — see below |

#### The off-repo surfaces, in detail

These surfaces live outside this repository, so CI cannot guard them and
they drift. All of them were audited on 2026-11-20 by reading the pixels
that are actually served, not by reading a filename, and **re-verified on
2026-11-21** the same way — the Live Audit note below records what that
second pass changed. The two that carried the wrong thing were corrected;
the generator that produces the assets is `make_offsite_assets.py`, which
builds them from the same committed sources the website uses, so an
off-repo surface cannot drift from the mark that ships.

| Surface | Where it lives | What it carried | Now |
|---|---|---|---|
| LinkedIn company avatar | `linkedin.com/company/goodciso` → Company Page Admin | An **unsaturated photo** — a greyscale image, max channel spread = 0 — uploaded 2024-09-19. Not a brand mark at all. | The corporate mark on the navy tile. Verified live on LinkedIn's CDN (`goodciso_logo`): teal shield, G-counter, amber dot; **0** AWARE-green pixels. |
| LinkedIn company cover | same | **ChangTech's** asset — a generic sunset stock photo whose CDN filename was literally `changtech_consultants_cover`, uploaded 2020-10-28. A cross-brand error, not a wrong-mark one. | The GoodCISO cover. Verified live on LinkedIn's CDN (`goodciso_cover`): teal shield with the amber dot, the "Good CISO" lockup and the tagline; **0** AWARE-green pixels. |
| GitHub org avatar | `github.com/GoodCISO` (org, not the `aware` repo) | The corporate mark — teal shield, amber dot, **0** green pixels. | Correct already. Left alone. Note the distinction: the **org** avatar is the company's; the **product** is the repo `GoodCISO/aware` under it. |
| Email signature | Gmail send-as `alvin@goodciso.org` (`gws-goodciso`) | `signature: ""` — **empty**. The block Alvin sends from is typed into the body. The alias `alfie@goodciso.org` is likewise empty. | Nothing to fix: there is no mark to be wrong. The ChangTech lane (`alvin@changtech.net`) is likewise text-only. |
| Sales deck | `~/projects/goodciso-website/GoodCISO-AWARE-Deck.pptx` | **No mark of any kind.** The package has no `ppt/media/` directory at all: zero `<a:blip>`, zero `p:pic`, zero `<a:path>` in any slide. Every slide's palette is `00A896 / 0B1120 / 94A3B8 / FFFFFF` — teal, no green. The wordmark is live text reading "AWARE", which is correct for an AWARE pitch deck. | Nothing to fix. Not a wrong-mark defect but a missing-mark one, and the deck is a binary asset that must not be re-authored. |
| X / Twitter banner | `x.com/goodciso` → Profile → Edit profile | A **pixel-art illustration** — a teal-and-purple blocky scene with a "Good CISO" wordmark in the lower left. Not a mark in any recognised sense: no shield, no G-counter, no amber dot. | Nothing to fix: no corporate mark is present to be wrong. Note the palette contains teal (the corporate hue) but no shield and no amber dot, so it does not read as either brand's mark. |
| YouTube channel avatar | `youtube.com/@goodciso` | A **purple** disc (`#512DA7`) with a white rounded-square glyph. No shield, no teal, no amber. The channel's one video ("Sentinel Flow", 7 months old) has a product-screenshot thumbnail — no brand mark either. | Nothing to fix. This is a third-brand look (purple) rather than a cross-brand one: neither GoodCISO's nor AWARE's mark appears. |

**The predicted defect was not the one that was there.** The hypothesis was
that these surfaces carried AWARE's green shield-and-check. **None of them
did.** The avatar carried no mark, the cover carried another company's
stock photograph, and the signature and the deck carry no mark at all. The
AWARE mark appears only on the AWARE sites, which is where it belongs.

**Rule 1 applies off-repo too.** A mark never crosses sites — and a
corporate surface must never carry the product's mark *or another
company's asset*. The guard in `qa.py` cannot see a LinkedIn page, which
is why the two LinkedIn surfaces needed fixing by hand rather than by CI.

#### Live Audit — 2026-11-21

A second, independent pass over every surface in this section, reading the
bytes that are served **today** rather than trusting the 2026-11-20 record.
It found no new cross-brand defect, and it corrected three things the first
pass had wrong:

| Correction | The first pass said | The pixels say |
|---|---|---|
| LinkedIn avatar and cover | Fixed, verified live | **Confirmed.** Both re-fetched from LinkedIn's CDN today (`goodciso_logo`, `goodciso_cover`): teal shield, amber dot, **0** AWARE-green pixels. |
| LinkedIn carousel | "A teal **G logomark**" | A **wordmark** — white "GOOD CISO." in caps with a **teal** period dot. No shield, no G-counter, and the dot is teal where the canonical mark's dot is amber. |
| Sent mail | "The only images in 40 sent messages are third-party logos" | The **count** was wrong in a way that flattered the result: the bodies are base64-encoded, so a scan that reads the raw JSON sees zero images and reports a false clean. Decoded properly, 40 messages carry **22 `<img>` tags**. Every one was fetched and analysed: a RELX/LexisNexis/Elsevier strip, a 1×1 tracker, and a monochrome far.ai avatar. Still no brand mark — but the earlier clean was luck, not evidence. |

Two surfaces were **not on the record at all** and were added by this pass:
the X/Twitter **banner** and the YouTube **channel avatar**. Both carry no
corporate mark (see the table above), so neither is a defect — but a
surface that is not written down is a surface that cannot be checked.

**The method matters more than the result.** Every verdict in this section
comes from decoded pixels, not from filenames, CDN paths or a URL that
looks right. Two of the three corrections above were only findable because
the pixels were decoded.

#### Surfaces checked and found to carry nothing to fix

Also audited on 2026-11-20 and re-checked on 2026-11-21, and left
unchanged because they carry no mark, or already carry the right one:

| Surface | What it carries |
|---|---|
| LinkedIn post backgrounds (`galapagos-inFeedBackgroundImage`) | Photographs and illustrations. No mark. |
| LinkedIn carousel (`visuals/carousel-2026-08-11/*.png`, 7 files, old repo) | A **teal** period dot after a white "GOOD CISO." wordmark in caps. **No shield glyph and no G-counter** — the mark is a wordmark lockup, not the logomark, and the dot is teal where the canonical mark's dot is amber. No green — the mark is corporate. It is not the canonical lockup (§1: "Good" bold + "CISO" caps, no dot; the amber dot belongs to the shield), and it is a published LinkedIn post, so the PNG is not the live artefact. Canonicalisation is tracked separately; it is not a cross-brand defect. |
| Old repo `favicon.svg` | A simplified teal shield on navy — no amber dot, no G counter. The superseded repo is not deployed. |
| X / Twitter `@goodciso` avatar | A small monochrome glyph. No brand colour, no shield. (The **banner** on the same account is a pixel-art illustration — see the off-repo table above.) |
| Google Site "GoodCISO" (Drive) | An unused Google Sites template. No GoodCISO logo. |
| Sent mail from `alvin@goodciso.org` | No GoodCISO mark. 40 sent messages were decoded and every image in every body was fetched and analysed: the only images are a **RELX/LexisNexis/Elsevier** strip (a third-party logo, from job-application mail), a 1×1 tracking pixel, and a small monochrome far.ai avatar. No teal shield, no amber dot, no AWARE green. |
| `npm @goodciso/aware`, PyPI | No logo asset published. |

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

### The correction that changes the answer — 2026-11-21

The paragraph above is right about the **defect** and wrong about the
**history**. It says the teal shield-and-dot was "GoodCISO's own mark on the
site for months" and was "retired by accident". Read against the old repo's
actual git history, that is only true for part of the window, and the
distinction changes what the restore means.

**The teal shield-and-dot favicon was live for ~6 months, not "for months
of identity".** It was committed at `8d5f04b` (2026-05-20) and last
published from the `main` branch. A different favicon — the AWARE teal
rounded-square-with-white-check — was committed at `d29380f` (2026-06-29),
but that commit is **not an ancestor of `main`**: it lives only on
`feat/aws-monitor-calculator`. `git merge-base --is-ancestor d29380f main`
returns false. So the AWARE favicon was **never published from `main`** and
never reached production via that commit.

**The corporate *header* carried AWARE's mark for six months, and it is
still the reason this card exists.** Since `00ce804` (2026-05-19, "AWARE
website rebuild"), the old site's header has been a teal rounded square
with a white check and the wordmark "AWARE" — AWARE's mark, on the
corporate domain. `00ce804` changed only the wordmark text from "Good CISO"
to "AWARE"; the glyph was already the AWARE square. That is the error the
2026-11-16 build **inherited**, and §"The old repo" above describes it.

So there were **two** defects, not one, and they are different in kind:

| | Defect | Window | Fixed |
|---|---|---|---|
| A | The **favicon** carried AWARE's green shield-and-check on goodciso.org | 2026-11-16 21:37 → 2026-11-18 12:40 (~39 h) | `0aa78e3` / `a7bf229` |
| B | The **header** carried AWARE's teal square-and-check, with the wordmark reading "AWARE", on goodciso.org | 2026-05-19 → 2026-11-16 (~6 months) | `a7bf229` (2026-11-18) |

Defect A is the one Alvin saw: a green tick where a teal shield had been.
Defect B is older and quieter — for six months the *page* said AWARE in
the corner of every screen, and nobody noticed because the favicon was
still the teal shield.

**What this means for the current mark.** The teal shield-with-G-and-amber-dot
now on goodciso.org is **not** a byte-restoration of what was live in
November 2026. It is the original artwork from `~/projects/good-ciso-logo`
— verified below — but the mark that was live in the tab was a *simplified*
teal shield with a **teal** centre dot and **no G counter** (the old
`favicon.svg`: a solid teal shield with a navy inner cut-out and a teal
dot). The current favicon is the **full** logo artwork: teal shield, G-shaped
counter, amber dot, on a navy tile.

That is a deliberate improvement, and it is defensible — the original
artwork is the trademark, the simplified favicon was a hand-made
approximation of it, and the approximation is the one that had no G counter
and no amber. But it is a **change to the corporate mark**, and §6 requires
that a change to the corporate brand notifies the operator. The 2026-11-20
notification (`/tmp/brand-notify.txt`, sent via `hermes send`, confirmed
delivered) says the mark is "restored" and "your original pixels, cut from
the source artwork" — it does **not** say that the tab mark's *shape*
differs from the November favicon (no G counter before, G counter now),
and it does not mention the six-month header defect at all.

**The correction to make.** The accurate statement is:

> GoodCISO's corporate mark was **restored from the original artwork**, not
> restored byte-for-byte from the previous favicon. The previous favicon was
> a simplified teal shield with a teal dot and no G counter; the mark now
> shipped is the full original logomark — teal shield, G counter, amber dot
> — on a navy tile. The mark that was live in the tab for the previous six
> months was a simplification; the mark on the site now is the trademark.

That sentence should be in the notification to the operator, because
"restored" and "changed" are different business events and only one of them
is what actually happened.

#### The verification behind the "original artwork" claim

"Restored from the original artwork" is a claim about pixels, so it was
checked against pixels rather than asserted.

The source is `~/projects/good-ciso-logo/good-ciso-logo.png` — a 1024×1024
file that is a JPEG despite the `.png` extension. `extract_logo.py` cuts the
shield from it and the cut is reproducible. Re-running that cut in memory
and comparing the result to the committed `assets/brand/goodciso-shield.png`:

| Measure | Result |
|---|---|
| Size | 64×73, both |
| Alpha mask | **pixel-identical**, 0 differing pixels |
| Shape IoU | **1.0000** |
| Mean abs RGB difference on opaque pixels | **0.0, 0.0, 0.0** |
| Amber dot centroid | (31.82, 34.00) in both, 66 px each |

So the shipped shield is the original artwork, cut — not a redraw and not
a vector trace. That is the claim `trace_logo.py` exists to disprove: the
three SVG traces in `references/goodciso-logo-restoration.md` scored 0.33,
0.44 and 0.41 IoU, and none of them is in the build.

The live corporate favicon was checked the same way — pixels, not filename:

| Surface (live, fetched 2026-11-21) | Teal px | Amber px | AWARE green px |
|---|---|---|---|
| `goodciso.org/favicon.png` (512×512) | 52,575 | 1,674 | **0** |
| `goodciso.org/og.png` (1200×630) | 2,147 | 68 | **0** |
| `aware.goodciso.org/og.png` (1200×630) | 0 | 0 | **1,798** |

Each live asset is byte-identical (SHA-256) to its committed counterpart in
`assets/brand/`. The corporate header shield renders teal + amber with 0
green pixels, confirmed by reading the pixels of the served image.

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
- a page carries no `og:image`, or one that is off-site or not in the build;
- **the header mark is the wrong brand's**, on any page, on any site. The
  corporate header must reference the GoodCISO shield artwork and carry the
  "Good CISO" wordmark; the AWARE headers must carry neither. The check
  reads the `<header>` element specifically, because the footer repeats the
  logo — a page-scoped check would let a correct footer satisfy a wrong
  header, and would pass a header with no mark at all.

The header check keys on the **shape** of AWARE's shield, not its colour.
The June 2026 defect put a *teal* rounded square with a white check in the
corporate header; teal is the corporate hue, so a colour-based guard would
have passed it. The shape is what distinguishes the two marks, so the shape
is what the guard looks for.

The accent check resolves the cascade rather than grepping for a hex
string, because `tokens.css` is the shared base layer and legitimately
carries a green ramp that `brand.css` overrides. The card check compares
by content rather than by filename, because the build copies each card to
the same name (`/og.png`) on every site — only the bytes can tell the two
brands apart.

`test_brand_guard.py` proves the guard can fail. It breaks each condition
in turn and asserts the guard fires — a check that cannot fail is not a
check.

**Thirteen conditions** are covered: the corporate favicon (wrong brand and
missing), the corporate accent (repointed at AWARE's green), the hero glow
(hard-coded green, and hard-coded to anything rather than derived), the AWARE
favicon (wrong brand), the social card on both brands (wrong brand and
missing), and the **header mark** — AWARE's shield in the corporate header,
"AWARE" as the corporate wordmark, a corporate header with no mark while the
footer still has one, and GoodCISO's shield in an AWARE header.

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

It reads **the stylesheets the built page loads**, in document order, and
resolves the custom properties with selector specificity. It does not
read a hand-picked list of files: a stylesheet the page loads but the
checker does not read is measured wrong, and that is how a button's text
colour escaped this check — the component layer declared a fallback that
the checker never saw, so the check measured a value the browser never
used, and the dark theme shipped white-on-green at 2.28:1.

The measured ratios, the thresholds, and the two brand traps (the brand
colour failing AA as text, and the focus ring needing the same treatment)
are documented in `packages/design-tokens/README.md`. That is the file
`tokens.css` cites when it says the ratios are computed and verified there,
so the citation and the document now agree.

### JavaScript

```bash
python3.12 build_all.py && python3.12 test_javascript.py
```

Parses every script the built pages load. `site.js` shipped with an
unclosed `if` block, so the browser rejected the whole file and the theme
toggle and the mobile navigation did nothing on every page of every site.
No other gate looked at JavaScript, so the build stayed green.

### Component spec

```bash
python3.12 build_all.py && python3.12 qa.py
```

`qa.py` fails the build if a class is in the component layer and not in
`packages/ui/README.md`, or in the spec and not in the layer. The spec is
the contract; the CSS is the implementation.

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
