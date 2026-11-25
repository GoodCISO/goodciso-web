# Plan — port the first-party analytics collector to the four GoodCISO/AWARE sites

**Date:** 2026-11-25
**Source:** `~/.openclaw/projects/cofactor/site/netlify/functions/analytics.mjs` (live on cofactor.work since 2026-11-13)
**Target:** goodciso.org, aware.goodciso.org, docs.aware.goodciso.org, demo.aware.goodciso.org
**Why now:** the Coframe assessment concluded that measurement is the precondition for every other decision. We have a working, self-verifying collector already in production on a sister site. Reusing it is a port, not a build.

---

## 1. What the source collector actually is

Read the whole file rather than trusting the summary. It is a **Netlify Function (v2 runtime)** — `export default async (req, context)`, returning a WHATWG `Response`.

**What it records**, one JSON object per line:

| Field | Meaning | Max |
|---|---|---|
| `t` | ISO timestamp | 40 |
| `type` | `view` or `submission` | — |
| `p` | path | 300 |
| `r` | referrer | 500 |
| `s` | `?src=` source tag | 80 |
| `form` | which form was submitted | 80 |
| `w` | viewport width — **coarse device class only** | — |

**What it deliberately does not record:** no IP, no user-agent fingerprint, no cookie, no cross-site identifier, no session. The file's own header states this as a design constraint, not an accident: *"a security-led UK service should not ship a third-party tracking pixel to the buyer it is trying to reassure."*

**Storage** — append-only NDJSON, three candidate paths tried in order, first that accepts a write wins:

1. `ANALYTICS_LOG` env override
2. `<deploy dir>/analytics/events.ndjson` — survives container recycling
3. `/tmp/cofactor-analytics.ndjson` — always writable, per-container

Rotated at 1 MB.

**Failure behaviour:** never throws. A broken endpoint must never break a page. Storage failure is reported as `stored: false` — visible, not silent.

**Self-verification:** every response carries `count`, the number of events recorded so far. Two calls with a rising count prove the write persisted; a 200 alone does not.

### The three production bugs it documents in its own comments

These are the parts that matter for a port — each is a way the previous version failed *in production*, not in theory:

1. **The v2 runtime requires a WHATWG `Response`.** Returning the legacy `{statusCode, headers, body}` object throws *"Function returned an unsupported value"* and the endpoint answers **502**.
2. **v2 hands the handler a `ReadableStream` body, not a string.** `JSON.parse(req.body)` silently yields `{}` and every event records empty fields. The body must be read with `await req.text()`.
3. **Netlify's form scanner registered forms but never captured them**, because served HTML strips `data-netlify` after processing.

---

## 2. What is different on the target

| | cofactor.work | goodciso-web |
|---|---|---|
| Site count | 1 | **4** — each is a separate Netlify site with its own deploy root |
| Function source | in the site's own tree | **must be added to the repo**, or CI cannot build it |
| Build | Astro (`npm run build`) | **Python generator** — `build.py` / `build_all.py` |
| Deploy | Netlify API zip of `dist/` | Netlify API zip of the site root |
| Forms | 1 (`waitlist-hero`) | 1 (`contact` on goodciso.org) |
| Analytics today | **none** on any of the four | — |

**The hard part:** the four sites are deployed as **four independent zips**, each with its own `netlify.toml` and its own function bundle. A Netlify Function has to be inside the deployed directory tree, under `netlify/functions/`, and the `netlify.toml` must declare `[functions] directory = "netlify/functions"`.

So the port is not "copy a file". It is:

- a **shared** function source in the repo,
- **copied into each site's deploy root** by the builder,
- a `[functions]` block in **each site's** generated `netlify.toml`,
- and a **client** that posts to it from every page.

---

## 3. The plan

### Step 1 — the function, in the repo

`netlify/functions/analytics.mjs` at the repo root, shared by all four sites.

Changes from the cofactor original:

| Change | Why |
|---|---|
| Site name in the log filename | `/tmp/cofactor-analytics.ndjson` would collide across four sites in the same function environment. Per-site name. |
| `Access-Control-Allow-Origin: "*"` → same-origin | The original allows any origin to POST to the collector, which lets a third-party site use ours as a free telemetry sink. We serve four sites on four domains; the allow-list must cover exactly those. |
| Reject oversized bodies | The original reads the body with no length cap. A 10 MB POST would be parsed. Cap at 4 KB and ignore the rest. |
| Field name is already generic (`p`, `r`, `s`) | Keep the wire format identical, so the two sites' logs are directly comparable. |
| Everything else — storage order, rotation, self-verification, never-throws | Unchanged. It is correct, it is in production, and it is documented why. |

**Deliberately NOT changed:** the field set, the storage strategy, the response shape. Changing those would make the cofactor log unreadable by the same tooling.

### Step 2 — the client

One small inline script, added to every page of every site, in the shared layout so it cannot drift:

```js
(function () {
  if (window.__gcAnalytics) return;      // once per page
  window.__gcAnalytics = true;
  var d = document;
  var w = window.innerWidth || 0;
  var p = { p: location.pathname,
            r: document.referrer || "",
            s: new URLSearchParams(location.search).get("src") || "",
            t: new Date().toISOString(),
            w: w };
  // sendBeacon first: it survives page unload, which a pageview does
  // not. fetch with keepalive as the fallback.
  var body = JSON.stringify(p);
  if (navigator.sendBeacon) {
    navigator.sendBeacon("/.netlify/functions/analytics",
      new Blob([body], { type: "application/json" }));
  } else {
    fetch("/.netlify/functions/analytics", { method: "POST",
      body: body, keepalive: true,
      headers: { "Content-Type": "application/json" } })
      .catch(function () {});
  }
})();
```

**Properties that matter:**

- **No cookie, no localStorage, no identifier.** The function stores no IP and the client sends none.
- **Never blocks.** `sendBeacon` is fire-and-forget; there is no await, no error path that can affect rendering.
- **Respects nothing about consent, because there is nothing to consent to.** No identifier means no cross-site tracking and therefore nothing to ask about. That is a property worth stating in the privacy notice.
- **Only on pages, not on assets.** The script is inline in the document.

### Step 3 — the form submission signal

The collector distinguishes `view` from `submission` via a `form` field. goodciso.org has one form (`contact`), so the form handler adds `form: "contact"` to its payload.

**The form should also carry a `source` field**, so a submission can be tied to where it came from — exactly as cofactor's `waitlist-hero` does with its hidden `source` input. Without it, a submission is a conversion with no attribution.

### Step 4 — the deploy plumbing

- `build_all.py` copies `netlify/functions/analytics.mjs` into **each** site's deploy root, with the site key substituted.
- `netlify_config.py` adds to **each** site's generated `netlify.toml`:
  ```toml
  [functions]
    directory = "netlify/functions"
    node_bundler = "esbuild"
  ```
- `deploy.py` ships the whole site root.

**The deploy must go through the Netlify CLI, not the API's zip upload.** This was the hardest-won finding of the whole port, and it is worth stating precisely because the API's behaviour is actively misleading:

| Method | Result |
|---|---|
| `POST /sites/{id}/deploys` with a zip containing `netlify/functions/analytics.mjs` | **"No functions deployed"** — on a scratch site *and* on the production corporate site |
| The same tree through `netlify deploy` | **"Finished hashing 55 files and 1 functions"**, and the function answered 200 |

The zip contained the function. Netlify's file-listing API showed it there. The deploy reported success. And the function was simply not there — `/.netlify/functions/analytics` answered 404 with a 200 on the site itself, so nothing looked broken.

Three layouts were tried (`netlify/functions/`, `functions/`, and the root, with `[functions] directory` set to each) and none of them worked through the API. The CLI worked on the first attempt with the same tree.

Netlify's own documentation confirms the mechanism the CLI uses: *"The default location is YOUR_BASE_DIRECTORY/netlify/functions"*. With `publish = "."` the base directory is the deploy root, so the function sits in `netlify/functions/` beside the site.

**A consequence worth stating:** because the API path silently drops functions, any deployment that goes through it would appear to succeed while the collector quietly vanished. The deploy now goes through the CLI, and the post-deploy verification asserts the function is mounted — a 405 on a GET, which proves the function is there, as opposed to a 404, which proves it is not.

### Step 5 — the verification

| Check | How |
|---|---|
| The function is deployed | `GET /.netlify/functions/analytics` → 405 with `method not allowed` (the function is live; a 404 means it did not ship) |
| It accepts a write | `POST` a probe → `stored: true`, `count` increments |
| The count is per-site | probe site A and site B; each has its own count |
| The page sends one | browser → network tab, or the function log shows a `view` for the path |
| No IP is stored | read the log: the event has exactly the seven fields |
| The function cannot break a page | the client has no await in the render path, and the function never throws |

### Step 6 — the guard

A check that fails the build if any of these regress:

- every built page contains exactly one analytics beacon call
- no page sets a cookie, a `localStorage` key, or an identifier
- the generated `netlify.toml` for each site declares `[functions]`
- the function source is in the repo and is byte-identical across the four deploy roots

---

## 4. What this does NOT do, deliberately

- **No IP, no user agent, no fingerprint, no cookie, no identifier.** Not a later decision — the constraint is inherited from the source and is the reason the whole thing is acceptable on a security company's site.
- **No third-party analytics.** Not GA4, not Plausible, not PostHog. The collector is the alternative.
- **No cross-site identifier between the four sites.** Each site's log is separate. A visitor moving from goodciso.org to aware.goodciso.org is not linkable, and that is the correct behaviour for a product site that must not inherit the corporate site's tracking.
- **No change to the privacy notice beyond stating the facts**, because the facts are unchanged from cofactor and the notice there already describes them.
- **No dashboards, no reporting pipeline, no alerting.** Those come after there is data worth reporting. The `count` in each response is enough to prove it is working.

---

## 5. Risks

| Risk | Mitigation |
|---|---|
| The function ships but the `netlify.toml` lacks `[functions]`, so it is not mounted | The build check asserts the block is present in each generated config, and Step 5 checks the live endpoint |
| A 4th site shares a function environment and collides on the log filename | The filename is per-site; the count is verified per site |
| The collector becomes a free telemetry sink for another origin | `Access-Control-Allow-Origin` is restricted to our four domains |
| A large POST body is parsed | 4 KB cap, ignored beyond that |
| The function breaks a page | It never throws; the client never awaits |
| Volume grows the log without bound | 1 MB rotation, already in the source |

---

## 6. Sequence

1. The function, in the repo, with the four changes above.
2. The client script, in the shared layout.
3. The `source` field on the contact form.
4. The builder copies the function into each deploy root; the config declares it.
5. The build check.
6. Deploy to a **scratch** site first, verify all six checks against it, then the four production sites.
7. Read a production log and confirm the seven fields and nothing else.

**Effort:** roughly two hours. **The measurement it unblocks is the precondition for every other decision** — including the Coframe question, which cannot be answered at all until we know our traffic.
