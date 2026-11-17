# Production Handover — GoodCISO + AWARE

**Date:** 2026-11-16
**Repository:** https://github.com/GoodCISO/goodciso-web (branch `main`)
**Status:** all four sites live, verified, and under CI.

---

## 1. Production URLs

| Site | Domain | Netlify site id | Netlify hostname |
|---|---|---|---|
| GoodCISO corporate | https://goodciso.org | `e7f43642-d6f1-4625-a4c9-3cfdb0525446` | `cozy-alfajores-7fbd44.netlify.app` |
| AWARE product | https://aware.goodciso.org | `628c454e-0569-4664-a61c-792f3c0a3420` | `aware-goodciso.netlify.app` |
| AWARE docs | https://docs.aware.goodciso.org | `916fcf43-c51b-4198-a268-4384c4d90a4c` | `aware-docs.netlify.app` |
| AWARE playground | https://demo.aware.goodciso.org | `66acc7fe-692f-440b-a9e9-1437010ccc03` | `aware-playground.netlify.app` |

**Account:** Netlify `alvin-rxep8y` (Good CISO), user `alvin@goodciso.org`.
**DNS:** Cloudflare zone `goodciso.org` (`492c93499a5fd0bb7660dfba5bec38a9`), Free plan.
**TLS:** Let's Encrypt via Netlify. All four verified with `ssl_verify_result = 0` and the correct CN.

---

## 2. Deployment architecture

```
git push to main
      │
      ▼
launchd: ai.goodciso-web-deploy  (every 5 minutes)
      │
      └─► deploy_watcher.py
            ├─ read main's commit SHA from the GitHub API
            ├─ compare with deploy/state.json
            ├─ (unchanged) → exit, nothing happens
            └─ (changed) →
                 ├─ build_all.py       → dist/{aware,corporate,docs,demo}
                 ├─ netlify_config.py  → netlify.toml + redirects per site
                 ├─ qa.py              → link/heading/metadata/sitemap gate
                 ├─ deploy.py --site X → Netlify deploy, per site
                 └─ verify_production.py → TLS, headers, sitemap, every URL
```

The QA gate runs **before** any deploy. A build that breaks a link, drops a heading, or loses a canonical URL does not reach production.

### Why a host-side watcher rather than GitHub Actions

This is a constraint, not a preference, and it is worth understanding before changing it.

The GitHub PAT on this host has the `repo` scope but **not** `workflow`. GitHub refuses to create or update anything under `.github/workflows/` with such a token: the git push is rejected with an explicit scope message, and the contents API returns a deliberate `404` rather than `403`. Netlify's own GitHub integration is also unavailable — the production site is linked to a GitHub App installation on the personal `alvin-chang/website` account, and installing that App on the GoodCISO organisation requires an interactive OAuth authorisation that a scheduled job cannot perform.

So the CI lives on this host. `deploy_watcher.py` does the same job a workflow would: it detects that `main` has moved, builds, gates on QA, deploys only what changed, and re-verifies production.

The Actions workflow is kept at **`ci/deploy.yml`** with a header explaining how to switch to it. To switch: move it to `.github/workflows/deploy.yml` using a token with the `workflow` scope, and confirm the four `NETLIFY_BUILD_HOOK_*` secrets are set on the repository.

### Running a deploy by hand

```bash
cd /Users/alfie/projects/goodciso-web
python3.12 deploy_watcher.py --check   # report only, change nothing
python3.12 deploy_watcher.py           # deploy if main has moved
python3.12 deploy_watcher.py --force   # deploy regardless
```

---

## 3. Environment variables

**Names only. No secret values are recorded here or in the repository.**

### GitHub repository secrets

Registered and secret-backed, and currently unused — the active CI is the host-side watcher. They exist so that switching to GitHub Actions needs no Netlify change.

| Name | Purpose |
|---|---|
| `NETLIFY_BUILD_HOOK_AWARE` | Netlify build hook for aware.goodciso.org |
| `NETLIFY_BUILD_HOOK_DOCS` | Netlify build hook for docs.aware.goodciso.org |
| `NETLIFY_BUILD_HOOK_DEMO` | Netlify build hook for demo.aware.goodciso.org |
| `NETLIFY_BUILD_HOOK_CORPORATE` | Netlify build hook for goodciso.org |

### On-host credential files (not in the repository)

| File | Holds | Used by |
|---|---|---|
| `~/.openclaw/credentials/netlify-goodciso.env` | `NETLIFY_AUTH_TOKEN` | `deploy.py` — the Good CISO Netlify account that owns all four sites |
| `~/.openclaw/credentials/cloudflare.env` | `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ZONE` | `deploy.py --dns` — DNS writes |

Token scope required on Netlify: site read/write, domain read/write, build-hook read/write, deploy read/write.

---

## 4. DNS configuration

| Name | Type | Content | Proxied |
|---|---|---|---|
| `goodciso.org` | CNAME | `apex-loadbalancer.netlify.com` | no |
| `www.goodciso.org` | CNAME | `cozy-alfajores-7fbd44.netlify.app` | no |
| `aware.goodciso.org` | CNAME | `aware-goodciso.netlify.app` | no |
| `docs.aware.goodciso.org` | CNAME | `aware-docs.netlify.app` | no |
| `demo.aware.goodciso.org` | CNAME | `aware-playground.netlify.app` | no |

Existing records (MX, SPF, DMARC, DKIM, CAA, MTA-STS, TLSRPT) were **not modified**. `_mta-sts` and `mta-sts` continue to point at the corporate site.

---

## 5. CI/CD configuration

- **Trigger:** a push to `main`, detected by `deploy_watcher.py` within 5 minutes.
- **Scheduler:** launchd agent `ai.goodciso-web-deploy` (`~/Library/LaunchAgents/ai.goodciso-web-deploy.plist`), `StartInterval` 300s. launchd rather than cron because it survives reboot and is visible in `launchctl list`.
- **Logs:** `~/.hermes/profiles/designer/artifacts/webdeploy.log` and `.err`.
- **Build:** `python3.12 build_all.py` → `python3.12 netlify_config.py`.
- **Gate:** `python3.12 qa.py` must exit 0. Currently 55 pages, 0 errors.
- **Deploy:** `python3.12 deploy.py --site <name>` for each site. A failure on one site does not block the others, and the failure is reported.
- **Post-deploy:** `python3.12 verify_production.py` — TLS, security headers, robots, sitemap, and every sitemap URL resolves 200.
- **Idempotence:** the watcher records the deployed SHA in `deploy/state.json`. A run with no change exits without deploying. A lock file (`deploy/watcher.lock`) prevents two overlapping runs from both deploying.
- **Manual trigger:** `launchctl kickstart -k gui/$(id -u)/ai.goodciso-web-deploy`.

The four Netlify build hooks remain registered and secret-backed, so switching to GitHub Actions needs no Netlify change.

---

## 6. Rollback procedure

**The corporate site is the only one that replaced existing production content.**

### Roll back goodciso.org to its previous deploy

The deploy ids are recorded in `deploy/rollback.json`. The most recent pre-redesign production deploy was `6afa2c810df61721600f16c1` (2026-11-15).

```bash
# 1. List the site's deploys
python3.12 - <<'PY'
import json, urllib.request, os
env = dict(l.strip().split("=", 1) for l in
           open(os.path.expanduser("~/.openclaw/credentials/netlify-goodciso.env"))
           if "=" in l and not l.startswith("#"))
tok = env["NETLIFY_AUTH_TOKEN"].strip().strip('"')
req = urllib.request.Request(
    "https://api.netlify.com/api/v1/sites/e7f43642-d6f1-4625-a4c9-3cfdb0525446/deploys?per_page=20",
    headers={"Authorization": "Bearer " + tok})
with urllib.request.urlopen(req, timeout=40) as r:
    for d in json.load(r):
        print(d["id"], d.get("state"), d.get("created_at"), d.get("title", "")[:60])
PY

# 2. Restore the chosen deploy (this republishes it as the live deploy)
curl -X POST \
  -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
  "https://api.netlify.com/api/v1/sites/e7f43642-d6f1-4625-a4c9-3cfdb0525446/deploys/6afa2c810df61721600f16c1/restore"

# 3. Confirm
curl -s https://goodciso.org/ | grep -o "<title>[^<]*"
```

Rollback is a single API call and takes effect in seconds. The DNS records for all four domains are untouched by a rollback, so no DNS change is needed to revert.

### The other three sites

`aware`, `docs` and `demo` are new. To roll them back, redeploy the previous build:

```bash
cd /Users/alfie/projects/goodciso-web
git checkout <previous-sha>
python3.12 build_all.py && python3.12 netlify_config.py
python3.12 deploy.py --site aware    # etc.
```

---

## 7. URL preservation

Every URL from the previous goodciso.org sitemap is preserved by a 301. All 15 were verified against production after the deploy.

| Previous URL | Now redirects to |
|---|---|
| `/pricing.html`, `/pricing` | `/services/regulatory-readiness` |
| `/book.html`, `/book` | `/contact` |
| `/services.html` | `/services` |
| `/demo`, `/demo/` | `/aware` |
| `/aws-monitor`, `/aws-monitor/` | `/services/security-architecture` |
| `/aws-monitor/calculator`, `/aws-monitor/calculator/` | `/services/security-architecture` |
| `/security-policy.html` | `/about` |
| `/contact.html` | `/contact` |
| `/privacy.html` | `/privacy` |
| `/terms.html` | `/terms` |
| `/blog/` | `/insights` |
| `/blog/2026-06-08-container-security-gap-nobody-talks-about.html` | `/insights/container-security-gap` |
| `/blog/2026-06-08-why-llm-threat-models-fail.html` | `/insights/why-llm-threat-models-fail` |
| `/blog/2026-06-08-devsecops-dead-long-live-devops.html` | `/insights/devsecops-is-dead` |
| `/blog/what-we-learned-building-agentic-security-workflows.html` | `/insights/what-we-learned-building-agentic-security-workflows` |

The redirect table lives in `netlify_config.py` and is emitted into `deploy/redirects.json`.

**Also preserved:** `llms.txt`, `agent-instructions.txt`, `/.well-known/security.txt` (RFC 9116), `robots.txt`.

> **Note on `.well-known`:** Netlify's deploy API silently drops dot-directories from a zipped upload. `security.txt` is therefore written to `/security.txt` and served at `/.well-known/security.txt` through a redirect rule — the same mechanism the live site already used for MTA-STS. Verified live: HTTP 200.

---

## 8. Verification performed

| Check | Result |
|---|---|
| TLS on all four domains | Pass — valid cert, correct CN, `ssl_verify_result = 0` |
| Security headers on all four | Pass — HSTS, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options` |
| Sitemap URLs resolving | Pass — 47 URLs across the four sites, 0 broken |
| Page integrity | Pass — 46 pages checked, exactly one `<h1>` each, no degraded shells |
| Internal link integrity | Pass — 51 built pages, 0 broken links |
| Heading structure | Pass — no skipped levels within a page body |
| Metadata | Pass — unique titles, descriptions and canonicals on every page |
| Redirects | Pass — 20 rules, all returning 301 and landing on 200 |
| Migrated articles | Pass — 4 articles live, each with 1 h1, section headings and only valid internal links |
| 404 behaviour | Pass — unknown paths return 404, not a soft 200 |
| Playground interaction | Pass — 7 scenarios, switching updates the readout, `aria-pressed` tracks state |
| Console errors | Pass — none on the live playground |
| Horizontal overflow | Pass — none |
| Mobile nav, 44px targets, reduced motion | Pass — all rules shipped and confirmed in the live CSS |

### Acceptance check

`python3.12 acceptance.py` checks the brief's criteria against the live production sites — **94 of 94 pass**. It covers the corporate page set, the AWARE page set, the docs page set, the playground, HTTPS, security headers, robots and sitemaps on every site, every sitemap URL resolving, the contact form's registration with Netlify, and the claim discipline (that the unsupported marketing claims from the previous site are gone).

**Not performed:** Lighthouse/CWV scoring against production, and an independent (axe) automated a11y audit. The manual and programmatic checks above are the evidence offered. A Lighthouse run and an axe sweep are the sensible next QA step.

**Page count:** 55 built pages across the four sites — corporate 17, docs 19, aware 15, demo 2 (page + 404).

### A note on the contact form

Netlify strips the `data-netlify` attribute from the **served** HTML once it has registered a form at build time. The attribute is present in the source and in the deploy; its absence from the live page is not a defect. The authoritative check is Netlify's form registry, which shows the `contact` form live with all six fields (`bot-field`, `name`, `email`, `organisation`, `topic`, `message`). The registry also still holds the previous site's `contact-form`, which has 2 historical submissions — that is the old form, not the new one.

A real submission has still not been made, so the lead-delivery path — where the notification actually goes — remains unproven. Submit it once from the live page.

---

## 9. Outstanding issues

1. **Resolved — the four blog posts are now published.** They were migrated into native pages at `/insights/<slug>/`, the old `/blog/*.html` URLs 301 to the articles themselves rather than to the index, and the `/insights` index links all four. The migration also runs a claim-correction pass: the posts predate the AWARE 2.12.2 README correction and contained "cryptographic identity" and T0-T4-as-enforcement-tier claims, so those sentences were rewritten to match `docs/capability-register.md`.
2. **The contact form was not submitted end-to-end against production.** The form is marked `data-netlify="true"` with a honeypot, which Netlify handles natively, and the markup and labels were verified — but no real submission was made, so the lead-delivery path is unproven. Submit it once from the live page before relying on it.
3. **The old corporate site's AWS Monitor and crypto-advisory content** (`/aws-monitor`, `/services.html` as a crypto-research page) is not carried into the new site. Those URLs redirect to the closest new equivalents, but the underlying content was a separate business line and is now absent. It was deliberately not smuggled into the new corporate narrative. If it is still a live offering, it needs its own page and its own route — it is a decision, not an oversight.
4. **CI has run end to end.** `deploy_watcher.py` was executed through the launchd agent and completed the full cycle — build, QA gate, four deploys, production verification. The Actions workflow is parked at `ci/deploy.yml` and is not active; see §2 for why, and for how to switch to it.
5. **Resolved — blog posts migrated.** See item 1. The source fragments remain in `/Users/alfie/projects/goodciso-website/blog/` and the migration is reproducible with `python3.12 migrate_insights.py`.

6. **`llms-full.txt` was never published.** A previous draft of this note listed it as a lost file — it never existed on the live site and the old build never emitted it. `llms.txt` and `agent-instructions.txt` were preserved correctly.

---

## 10. The governing document

**`docs/capability-register.md`** classifies every AWARE capability as IMPLEMENTED, PARTIALLY IMPLEMENTED, DEMONSTRATION, ROADMAP or UNVERIFIED, against three separate axes — does the code exist, is it wired into a runtime path, is it test-covered — and cites file and line for each claim.

It also carries a **"claims we must not make"** table of 20 specific claims that the source does not support, and a **"claims we can make"** list of 12 that it does.

Any change to the AWARE product should update that register first. The website copy is downstream of it. The three claims most likely to be reintroduced by accident are:

- **Commit Guard** — does not exist in `src/`. Roadmap.
- **Revocation cascade** — explicitly retracted in AWARE 2.12.2. Revocation is single-agent.
- **T0–T4 as enforcement tiers** — the labels exist in the UI, but `src/policies/engine.js` does not branch on tier. The engine enforces by tool risk and data tier.
