# Coframe assessment — what it is, and whether the concept applies to us

**Date:** 2026-11-25
**Subject:** Coframe (coframe.com) — an AI-powered CRO platform — assessed for adoption or concept-transfer to goodciso.org and aware.goodciso.org.
**Method:** the product's own site and docs read directly, plus the Terms of Use, the Privacy Policy, HN Algolia, and independent search. Every claim below is marked as *Coframe's own claim* or *independently verified*.

---

## 1. What Coframe actually is

**Not a landing-page builder.** It is an **AI-powered conversion-rate-optimisation platform**: a service where AI agents build and run experiments on a website you already have, and generate new landing pages for campaigns.

Its four product lines, per its own navigation:

| Line | What it does |
|---|---|
| **AI conversion optimisation** | Plans, builds and runs experiments on your existing site; learns from results to pick the next test |
| **AI landing pages** | Generates and tests landing pages per campaign/audience/offer, published to your domain |
| **Ad revenue optimisation** | Routes each ad to a tailored page, optimising for revenue rather than clicks |
| **AEO / GEO** | Serves agent-readable versions of pages for AI answer engines |

The pitch is *"Turn your traffic into revenue"* with *"AI agents build and run experiments on your site and ads."* It raised **$35M** and acquired HaystacksAI in March 2026, appointing its founder Bo Mohazzabi as VP of GTM. The acquisition post is by **Josh Payne** — the Klaviyo founder, which is a strong signal about the pedigree.

### The five-step loop, in its own words

> 01 Analyze and ideate · 02 Success prediction · 03 Design · 04 Development and QA · 05 Analysis

Step 02 is the interesting one: it **scores and ranks experiment ideas by expected conversion and revenue impact**, so experiments are queued by predicted value rather than by whoever asked first. Step 05 feeds results back into generating the next round.

### The algorithm

Not a fixed A/B test. It uses a **multi-armed bandit** with an "Optimizer" algorithm: continuously test many variants, drop under-performing arms, and use generative AI to propose new ones.

> *"Traditional experimentation finds winners ~15% of the time. We, on the other hand, find winners 90%+ of the time."*
> — Coframe, [how-coframe-finds-winners](https://www.coframe.com/post/how-coframe-finds-winners-90-percent-of-the-time)

**The 15% figure is Coframe citing Optimizely, VWO and Convert.com** — so the baseline is sourced from third parties, though Coframe's own 90% is self-reported.

### How it integrates

A **one-time script install on your site**. After that, variants are built by Coframe (including larger layout changes), then **your team reviews and approves before anything launches**. It explicitly does *not* run unsupervised:

> *"generative AI is not acting without permission or supervision on your website; you have full control to approve variants"* — Coframe

---

## 2. The evidence — and its quality

This is where the assessment turns on honesty rather than enthusiasm.

### Coframe's own performance claims

| Claim | Source | Independently verified? |
|---|---|---|
| +158% conversion in 6 months (Sur La Table) | Coframe's homepage | **No.** No independent verification found. |
| +410% enterprise conversion in 3 months | Coframe's homepage | **No.** |
| +60% conversion in 3 months | Coframe's homepage | **No.** |
| $300M+ incremental revenue | Coframe's homepage | **No.** |
| "90%+ win rate" | Coframe blog | **No.** Self-reported. The 15% baseline is cited to third parties. |
| "Finds winners 90% of the time" (Sept 2024) | Coframe blog | **No.** |
| $35M raised | Coframe homepage | **No independent coverage found** — no TechCrunch result, no Crunchbase access (403). |

**I found no independent verification of any of these numbers.** Not because the claims are necessarily false — but because the evidence is entirely first-party. Searching HN Algolia for the product returns ~460 hits that are all for unrelated things (*Coframe Coffee*, an open-source React component generator; *crowdtilt*). There is no independent practitioner commentary to weigh.

### The clause that contradicts the marketing

From Coframe's **Terms of Use**, effective 1 January 2026:

> **"Notwithstanding the foregoing, the Company makes no guarantees regarding website performance improvements or business outcomes."**
> — §1.4

That is Coframe's own contract disclaiming the performance outcomes its homepage headlines. Worth knowing before anyone points at "+158%" in a board deck.

### Coframe's own honesty about where it fails

This is the most credible material on the site, and it is worth quoting because it constrains the concept:

> *"AI is good at some of the mechanical work of A/B testing, such as drafting variants, building them and summarizing results. What it's not good at is the hard work around a test: taste, approvals and scientific interpretation."*
> — [do-ai-ab-testing-tools-work](https://www.coframe.com/answers/do-ai-ab-testing-tools-work)

> *"Faster building does not make a test on a low-traffic page conclusive."*

> *"Speed moves the bottleneck to QA, traffic and reading results."*

> *"The costly bugs are broken behavior. A form that stops submitting, an analytics event that stops firing, or a link that loses its tracking parameters can skew a test or hurt revenue while nothing looks wrong."*

That last one is a direct warning about the failure mode we would be most exposed to: **a variant that silently breaks the form or the analytics** would not look broken, and would corrupt the measurement.

### The traffic requirement

Not stated as a hard number anywhere I could find. But the logic is explicit: with a bandit allocating traffic across arms, each arm needs enough visits to reach significance. Our situation makes this decisive — see §3.

### Pricing

**Not published.** `/pricing` returns 404. There is a free trial ("Try it free for 14 days") and a "Get a demo" path. Commercial model appears to be **enterprise SOW-based**: the Terms describe delivery through *"a Statement of Work ('SOW')"* with fees and timeline, and recurring SOWs requiring authorised signatures. **There is no self-hosted and no open-source option** — the Terms explicitly prohibit reverse engineering and derivative works.

---

## 3. Why the concept does not transfer to our sites — the decisive constraint

**We do not have the traffic, and we do not have the measurement.**

Verified on 2026-11-25:

| Site | Analytics |
|---|---|
| goodciso.org | **none** |
| aware.goodciso.org | **none** |
| docs.aware.goodciso.org | **none** |
| demo.aware.goodciso.org | **none** |
| cofactor.work | first-party collector, live since 2026-11-13 |

**goodciso.org has no analytics at all.** No pageview count, no referrer, no source tag, nothing. We do not know how many people visit it, let alone which proposition they prefer.

Coframe's own documentation says the thing that stops us:

> *"Faster building does not make a test on a low-traffic page conclusive."*

And Coframe's entry point is *"Analyze your site. Takes 1 minute."* — that analysis runs against traffic data we do not have.

For scale: the one measurement we *do* have across the whole fleet is cofactor's, and it shows **a single real signup on 2026-11-20**. A bandit splitting traffic across competing arms at that volume produces noise, not signal. The decision Coframe would make — "variant B is winning" — would be a coin flip dressed as a result.

**The second constraint: what would we even be testing?**

Coframe's own case studies are consumer/e-commerce: L-Nutra, Sur La Table, Dropbox, Replit, a grocery brand, L.A.B. Golf. The mechanism is *find the CTA wording that sells more product*. Our proposition is not a product at a price; it is *"we will help you survive a procurement review."*

Testing different value propositions against different visitors on a security consultancy's site is not a conversion optimisation. It is **finding out what claims we can make that convert best** — which runs straight into the capability register. An A/B test that discovers "the version promising 'SOC 2 in 14 days' converts better" produces a version we may not be allowed to publish.

**The third constraint: the brand and evidence rules.**

GoodCISO's positioning rests on being the party that says what *is* true. The capability register governs it; execution assurance is roadmap and labelled as such; the testimonials and certifications are not invented. A machine optimising for conversion is a machine optimising for the shortest distance between a visitor and a button — and the shortest distance is frequently a claim we cannot substantiate. Coframe's own docs acknowledge this failure mode in a different context: *"A result can be statistically convincing and still be a change your company cannot use."*

**The fourth constraint: US-only, with export controls.**

The Terms forbid export from the United States and apply EAR/DFAR-style classification as "commercial items" (§2.2), and the Privacy Policy treats Coframe as an enterprise US service. For a UK company selling to UK and EU regulated buyers, sending our site content, audience data and experiment results to a US SaaS under those terms is a data-transfer question we would have to answer before any trial — and it is a question a security consultancy selling to procurement officers cannot afford to answer badly.

**The fifth: it would install a script on our site.** Our sites are static HTML generated by a Python script with no runtime JavaScript beyond a few lines. A CRO tag is a third-party script on every page of a security company's website, on the pages a customer reads before deciding whether to trust us with an agent-security product.

---

## 4. What IS worth taking — the transferable concepts

Adopting the tool is the wrong answer. **Three of its concepts transfer, and two of them we already have.**

### 4.1 AEO / GEO — worth taking, and partly done

Coframe's AEO line serves *"agent-readable versions of pages published with Coframe."* Their example shows a markdown-style rendering of the page with `##` headings, "Key facts", and FAQs — which is exactly the shape of our `llms.txt` and `agent-instructions.txt`.

**We already do this**, and we do it without a third party:
- `goodciso.org/llms.txt` — 200, live
- `goodciso.org/agent-instructions.txt` — 200, live
- The site's own answer-engine guidance in `docs/BRAND.md`

**The gap worth closing** is the one Coframe's example shows and ours does not: a **per-page agent-readable version**, not just site-level text files. Right now a crawler reading `goodciso.org/pricing/` gets HTML. A crawler reading a machine-readable rendering of that page gets facts it can cite. That is cheap to build in a static generator, needs no SaaS, and no vendor.

**Verdict: take the concept, not the vendor.**

### 4.2 Success prediction — worth taking, in a different form

Coframe ranks experiment ideas by *expected* impact so the best one runs first. The underlying idea is sound: **not every idea is worth running**.

For us, the useful version is not "rank A/B tests" but **"rank work by expected evidence value"** — which is what Sterling's `MARKETING-GAPS` assessment already does (ranked, with owners and costs). We have the concept. We don't need a model to apply it.

### 4.3 The approval gate — already ours, and ours is stricter

Coframe's whole loop depends on a human approving each variant before it goes live, and it offers *"preview links to review the website as a visitor would see it."* It also documents compliance and legal review as a first-class step for StartEngine, a regulated company.

Our equivalent is stronger and already enforced: **the capability register is a pre-approval gate on claims**, and `qa.py` fails the build on nine brand conditions plus the redirect-shadow and retired-asset checks. We do not need an AI to decide what may ship.

### 4.4 What we should actually do

Two concrete changes, both small:

**A. Add per-page agent-readable renderings.** The generator already emits HTML per page. Emit `page.md` alongside it — headings, key facts, FAQs, the capability status — and serve it at `page.md` with `Content-Type: text/markdown`. Our `llms.txt` already points at the right files; this completes the pattern.

**B. Add first-party analytics to goodciso.org.** This is the real gap, and it is the *precondition* for ever doing any of this. We have a working, self-verifying collector on cofactor.work — first-party, no cookie, no IP, no third party. Porting it to the four GoodCISO/AWARE sites is a known quantity, and it is worth doing **regardless** of any CRO tool, because right now we cannot answer "does anyone read the pricing page?"

Until (B) exists, no experiment of any kind — Coframe's, ours, or anyone's — can be evaluated. **Measurement first, optimisation second.**

---

## 5. The verdict

| Question | Answer |
|---|---|
| Adopt Coframe? | **No.** US-only enterprise SOW pricing, no self-hosted option, third-party script on a security company's site, no published pricing, and a Terms clause disclaiming the performance outcomes its homepage advertises. |
| Apply the concept? | **Partly, and two of the three applicable parts we already have.** |
| What to take | Per-page agent-readable renderings (AEO). The approval gate and the ranked-ideas discipline are already in place and stricter. |
| What not to take | Bandit-driven variant generation on a site with no traffic and no measurement. Value-proposition testing against a capability register. |
| What to do first | **Add first-party analytics to goodciso.org.** Nothing else on this list is decidable without it. |

**The uncomfortable summary:** Coframe is a well-built tool aimed at sites with traffic and a repeatable purchase decision. We have neither, and our purchase decision is a trust decision rather than a checkout decision. Adopting it would mean asking a machine to optimise the thing we sell — precision and credibility — against a metric that rewards overclaiming.

The concept worth taking from it is the one Coframe's AEO product quietly points at: publish pages that an AI answer engine can read and cite. We have started that. Finishing it costs a build change, not a contract.

---

## 6. Sources

**Primary — Coframe:**
- [coframe.com](https://www.coframe.com/) — product, performance claims, four product lines
- [do-ai-ab-testing-tools-work](https://www.coframe.com/answers/do-ai-ab-testing-tools-work) — its own account of where AI fails in A/B testing
- [how-coframe-finds-winners-90-percent-of-the-time](https://www.coframe.com/post/how-coframe-finds-winners-90-percent-of-the-time) — the bandit/Optimizer approach, and the 15% baseline sourced to Optimizely/VWO/Convert.com
- [ab-test-setup-time](https://www.coframe.com/answers/ab-test-setup-time) — hand-off and QA costs
- [ab-testing-without-developers](https://www.coframe.com/answers/ab-testing-without-developers) — integration model, the one-time script install, StartEngine
- [ai-ab-tests-with-human-approval](https://www.coframe.com/answers/ai-ab-tests-with-human-approval) — the approval workflow, compliance/legal review
- [Terms of Use](https://www.coframe.com/terms-of-use) — §1.4 no-guarantee clause; §1.1 SOW delivery model; §2.1–2.2 restrictions, export control, no derivative works
- [Privacy Policy](https://www.coframe.com/privacy-policy) — enterprise US service posture
- [Coframe Acquires Haystacks](https://www.coframe.com/post/coframe-acquires-haystacks) — March 2026, Josh Payne byline

**Independent:**
- HN Algolia API — searched `coframe`, `coframe CRO`, `coframe.ai`. No independent discussion of the CRO product; matches are for unrelated projects.
- TechCrunch RSS search for "coframe" — zero items.
- Crunchbase — 403, not accessible.

**Our own systems, verified 2026-11-25:**
- `goodciso.org`, `aware.goodciso.org`, `docs.aware.goodciso.org`, `demo.aware.goodciso.org` — no analytics of any kind
- `cofactor.work` — first-party collector at `/.netlify/functions/analytics`, live since 2026-11-13
- `goodciso.org/llms.txt`, `/agent-instructions.txt` — live, 200
