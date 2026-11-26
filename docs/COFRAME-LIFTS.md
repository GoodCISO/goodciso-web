# What we lift from Coframe — and what we don't

**Date:** 2026-11-26
**Companion to:** `docs/COFRAME-ASSESSMENT.md` (the assessment), `docs/ANALYTICS-PORT-PLAN.md` (the measurement that unlocks the rest).

---

## The thesis, distilled

> **A website should be a system that continuously tests, learns and automatically optimises itself — and AI is what finally makes that affordable.**

Everything in Coframe follows from that sentence: the multi-armed bandit (stop wasting traffic on losers), the generator (stop waiting for humans to write variants), the success-prediction step (rank ideas by expected value), the approval gate (humans keep the judgement), and the AEO line (publish what an answer engine can read and cite).

The unbundling is the sharpest part, and it is Coframe's own:

> *"AI is good at some of the mechanical work of A/B testing, such as drafting variants, building them and summarizing results. What it's not good at is the hard work around a test: taste, approvals and scientific interpretation."*

---

## Lifted, and already shipped

### 1. AEO — pages an answer engine can read and cite ✅

**Coframe:** *"Help your brand get recommended in AI answers with pages that AI agents can read, understand and cite."* Their example is a per-page agent-readable rendering: a title, "Who it is for", "Key facts", and FAQs.

**Ours:** 52 per-page markdown renderings across the four sites, generated from the same source as the HTML so they cannot drift, served as `text/markdown`, each HTML page declaring its twin with `<link rel="alternate" type="text/markdown">`, and `llms.txt` listing them so they are discoverable rather than merely present.

Shipped in `24d95e7`. No vendor, no script, no third-party processor.

### 2. The approval gate ✅ — and ours is stricter

**Coframe:** variants are built and then reviewed before launch; compliance and legal review is a first-class step for regulated customers (StartEngine).

**Ours:** the **capability register** is a pre-approval gate on claims, enforced by `qa.py`'s build-time guards — brand bleed, retired assets, redirect shadows, the analytics privacy contract, the component spec, plus the capability-status labelling across all four sites. The claim is gated before it is designed, not after it is built.

### 3. Ranked ideas by expected value ✅

**Coframe:** *"Success prediction — scores and ranks experiment ideas by expected conversion and revenue impact."*

**Ours:** Sterling's `MARKETING-GAPS` assessment already ranks the work with owners and costs, and the Coframe assessment ranked its own recommendations the same way. The discipline is present; only the model is absent, and we do not need a model to apply it.

---

## Lifted, and next

### 4. The success-prediction step, applied to content rather than copy

Coframe ranks *experiments*. The transferable idea is ranking *work* by expected evidence value before building it — which is what our own assessment did, but not systematically.

Concretely, and cheaply: the analytics collector now records path, referrer and `?src=` per view. After a week of that, we can rank **pages by traffic** and answer "where should the next piece of writing go?" with a number rather than an opinion.

This is the only lift that depends on the data we just collected, and it is the natural next use of it.

### 5. Per-page agent-readable renderings for the *AWARE* sites

We ship markdown twins for all four sites, and `llms.txt` on the corporate site. Two gaps worth closing, both small:

- **`docs.aware.goodciso.org`** has the most technical content on the fleet and is the surface an AI assistant is most likely to be asked about ("how do I install AWARE", "what does the policy engine return"). Its markdown twins exist but are not indexed anywhere.
- **An `llms.txt` on the AWARE sites.** The corporate site has one; the product site, the docs and the playground do not. A developer asking an assistant about AWARE gets the corporate framing rather than the product's.

### 6. The "ad revenue optimisation" idea, inverted

Coframe sends every ad to a tailored page and optimises for revenue rather than clicks. We have no ads. But the inversion is interesting: **one page per audience** — which is exactly what Sterling's assessment recommended and warned against on the grounds that we would lose the breadth axis.

The honest version: we should not build per-segment pages. Our differentiator is a *precise* position — audit-readiness for a UK regulated buyer — and segmenting dilutes it. The concept transfers as a discipline (know which audience a page is for) rather than as a mechanism (build a page per audience).

---

## Not lifted

### The bandit, and AI-generated variants — for now, and possibly never

**The precondition is traffic.** Coframe's own documentation:

> *"Faster building does not make a test on a low-traffic page conclusive."*
> *"Speed moves the bottleneck to QA, traffic and reading results."*

Its entry point is *"Analyze your site. Takes 1 minute"* — an analysis that runs against traffic data. **We had none at all until last week's port.** That is why the collector came first.

**And the mechanism is wrong for what we sell.** Coframe's cases are consumer e-commerce: L-Nutra, Sur La Table, Dropbox, a grocery brand. The question is *which CTA sells more product*. Ours is *whether a procurement officer trusts us with an agent-security product*.

Testing which value proposition converts best against a capability register is not conversion optimisation — it is finding out **what we may say**. And a machine optimising for the shortest distance between a visitor and a button will find the shortest distance, and the shortest distance is frequently a claim we cannot substantiate.

### The AI agent on our site

Coframe's "Agent view" is a feature that lets a visitor ask a question of their page. Ours does the same job better and without the script: the `.md` twin is the agent-readable page, and `llms.txt` is the guidance file. We do not need a chat widget that talks to a model; we need a page a model can read.

### Their vendor risk

US-only, enterprise SOW pricing, no published pricing, no self-hosted option, export controls, a third-party script on every page of a security company's website — and a Terms clause that disclaims the very performance outcomes its homepage advertises.

---

## The ordering that follows

**Measurement → ranked work → one thing at a time.**

1. **Measure.** The collector is live on all four domains. Let it run. A week of data is enough to know which pages exist for an audience.
2. **Rank.** When the data exists, rank the content work by expected evidence value instead of arguing about it.
3. **Lift the cheap structural wins** — an `llms.txt` for the AWARE sites, and indexing the docs site's markdown twins. Both are an hour, and both help the same audience Coframe's AEO line targets.

And keep the discipline Coframe is right about: **the human keeps the judgement.** For us that is the capability register and the brand rules. The machine proposes; the register disposes.
