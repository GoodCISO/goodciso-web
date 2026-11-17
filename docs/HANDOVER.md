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
GitHub Actions: .github/workflows/deploy.yml
      │
      ├─ build job
      │    ├─ build_all.py       → dist/{aware,corporate,docs,demo}
      │    ├─ netlify_config.py  → netlify.toml + redirects per site
      │    ├─ qa.py              → link/heading/metadata/sitemap gate
      │    ├─ upload artifact (dist/ + .deploy-hashes/)
      │    └─ decide which sites changed, by content hash
      │
      └─ deploy job (only if something changed)
           ├─ download the artifact
           ├─ deploy.py --site X → Netlify deploy, per site
           ├─ record the deploy hashes
           └─ verify_production.py → TLS, headers, sitemap, every URL
```

The QA gate runs **before** any deploy. A build that breaks a link, drops a heading, or loses a canonical URL does not reach production.

### Deploying through the Netlify API, not build hooks

The four sites are **not** linked to the repository in Netlify's own GitHub integration. Linking them requires an interactive GitHub App authorisation for the GoodCISO organisation, which cannot be done unattended. The build hooks are therefore registered but unused — firing one would rebuild the site from whatever Netlify already has checked out, not from this repository.

The workflow deploys through the Netlify API using `deploy.py`, which zips `dist/<site>` and creates a deploy against the site's id. The site ids are declared in `deploy.py`'s `SITES` map rather than read from a gitignored state file, so CI knows where to deploy.

### Repository secrets

| Name | Purpose |
|---|---|
| `NETLIFY_AUTH_TOKEN` | The Netlify credential for the account that owns all four sites. Read from the environment by `deploy.py`, so it works in CI. |
| `NETLIFY_BUILD_HOOK_AWARE` | Build hook for aware.goodciso.org — registered, kept as a fallback |
| `NETLIFY_BUILD_HOOK_DOCS` | Build hook for docs.aware.goodciso.org — registered, kept as a fallback |
| `NETLIFY_BUILD_HOOK_DEMO` | Build hook for demo.aware.goodciso.org — registered, kept as a fallback |
| `NETLIFY_BUILD_HOOK_CORPORATE` | Build hook for goodciso.org — registered, kept as a fallback |

### Deploying by hand

```bash
cd /Users/alfie/projects/goodciso-web
python3.12 build_all.py && python3.12 netlify_config.py
python3.12 qa.py                                  # must pass
python3.12 deploy.py --site corporate            # or aware / docs / demo
python3.12 verify_production.py
```

### A note on paths

Every script derives the repository root from its own location, and host-only paths (the credential store, the previous corporate site) are environment-variable overrides with the current values as defaults. An earlier version hardcoded `/Users/alfie/...` throughout, which meant the build only worked on the machine it was written on — the first CI run failed on it.

---

## 3. Environment variables

**Names only. No secret values are recorded here or in the repository.**

### GitHub repository secrets

| Name | Purpose |
|---|---|
| `NETLIFY_AUTH_TOKEN` | The Netlify credential used by `deploy.py` in CI |
| `NETLIFY_BUILD_HOOK_AWARE` | Netlify build hook for aware.goodciso.org — registered, kept as a fallback |
| `NETLIFY_BUILD_HOOK_DOCS` | Netlify build hook for docs.aware.goodciso.org — registered, kept as a fallback |
| `NETLIFY_BUILD_HOOK_DEMO` | Netlify build hook for demo.aware.goodciso.org — registered, kept as a fallback |
| `NETLIFY_BUILD_HOOK_CORPORATE` | Netlify build hook for goodciso.org — registered, kept as a fallback |

### On-host credential files (not in the repository)

| File | Holds | Used by |
|---|---|---|
| `~/.openclaw/credentials/netlify-goodciso.env` | `NETLIFY_AUTH_TOKEN` | `deploy.py` — the Good CISO Netlify account that owns all four sites. Overridden by the `NETLIFY_AUTH_TOKEN` environment variable when set, which is how CI uses it. |
| `~/.openclaw/credentials/cloudflare.env` | `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ZONE` | `deploy.py --dns` — DNS writes |
| `~/.openclaw/credentials/github-pat.env` | `GITHUB_TOKEN` (repo + workflow scope) | The single source for the GitHub credential. Read at use time by the git credential helper `~/bin/git-credential-github-alvin`. Mode `0600`. The previous credential is backed up beside it as `github-pat.env.bak-pre-workflow-token`. |

The `workflow` scope on this token is what allows a push that creates or updates anything under `.github/workflows/`. Without it GitHub rejects the push with an explicit scope message and the contents API returns a 404.

### How the credential reaches git

There is **one** credential file, and the token never appears in a remote URL, in `.git/config`, in a process argument, or in a shell history.

```
git push
   │
   ├─ credential.https://github.com.helper  →  ~/bin/git-credential-github-alvin
   │        reads ~/.openclaw/credentials/github-pat.env at use time
   │        (the token never enters the script's argv)
   │
   └─ the macOS keychain holds the same secret for github.com
            (a fallback for tools that do not use git's helper chain)
```

`osxkeychain` comes first in the global helper list, from Xcode's system gitconfig. It is backed by a keychain entry for `github.com`, and **a stale entry there silently overrides the credential file** — git never reaches the file helper, so a push touching `.github/workflows/` is rejected even though the file holds a token with the right scope. When that happened, the symptom looked like a scope problem and the real cause was a cached secret.

To refresh the keychain entry after a token rotation:

```bash
security delete-internet-password -s github.com -a alvin-chang -p htps
security add-internet-password -U -s github.com -a alvin-chang -p htps -w "<token>"
```

> **Never put the token in the remote URL.** It works, and it is tempting when a push is being rejected, but it leaves the secret in `.git/config` where it outlives the fix, in `ps` output for any process listing, and in the shell history. The credential chain above needs no such workaround — and when a push is rejected, the cause is nearly always a stale cached credential, not the URL.

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

- **Trigger:** a push to `main`, or manual dispatch from the Actions tab.
- **Workflow:** `.github/workflows/deploy.yml`, named "Deploy sites".
- **Build:** `python3.12 build_all.py` → `python3.12 netlify_config.py`.
- **Gate:** `python3.12 qa.py` must exit 0. Currently 55 pages, 0 errors. A failure stops the workflow before any deploy.
- **Change detection:** the build job hashes each site's built output and deploys only the sites whose content changed. The hashes live in `.deploy-hashes/` and are carried to the deploy job in the build artifact.
- **Deploy:** `python3.12 deploy.py --site <name>` for each changed site. A failure on one site does not block the others, and the failure is reported.
- **Post-deploy:** `python3.12 verify_production.py` — TLS, security headers, robots, sitemap, and every sitemap URL resolves 200.
- **Concurrency:** `concurrency: deploy-${{ github.ref }}` with `cancel-in-progress`, so two pushes in quick succession do not race.
- **Permissions:** `contents: read` only. The workflow never writes to the repository except the deploy-hash record, which it commits with the `github-actions[bot]` identity.

**Status:** the workflow ran green end to end on 2026-11-17 — build, QA gate, four site deploys, production verification, all successful.

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

## 9. Rotating the GitHub credential

The token must carry both `repo` and `workflow`. `workflow` is what permits a push that creates or updates anything under `.github/workflows/`.

```bash
# 1. Write the new token to the one credential file, mode 0600
cat > ~/.openclaw/credentials/github-pat.env <<'EOF'
# GitHub credential — GoodCISO org and goodciso-web (repo + workflow scope).
# Read at use time by ~/bin/git-credential-github-alvin for github.com.
GITHUB_TOKEN=***
EOF
chmod 600 ~/.openclaw/credentials/github-pat.env

# 2. Refresh the macOS keychain entry, which osxkeychain consults FIRST.
#    Skipping this is the trap: git will serve the stale cached secret and
#    the push fails with a scope error that looks like a token problem.
security delete-internet-password -s github.com -a alvin-chang -p htps
security add-internet-password -U -s github.com -a alvin-chang -p htps -w "<new token>"

# 3. Confirm the chain serves the new token
git credential fill <<< $'protocol=https\nhost=github.com\n'   # password must be the new one

# 4. Confirm the scopes
curl -sI -H "Authorization: Bearer <new token>" https://api.github.com/user | grep -i x-oauth-scopes
#   -> x-oauth-scopes: repo, workflow

# 5. A push that touches .github/workflows/ is the real test
git push origin main
```

## 10. Outstanding issues

1. **Resolved — the four blog posts are now published.** They were migrated into native pages at `/insights/<slug>/`, the old `/blog/*.html` URLs 301 to the articles themselves rather than to the index, and the `/insights` index links all four. The migration also runs a claim-correction pass: the posts predate the AWARE 2.12.2 README correction and contained "cryptographic identity" and T0-T4-as-enforcement-tier claims, so those sentences were rewritten to match `docs/capability-register.md`.
2. **The contact form was not submitted end-to-end against production.** The form is marked `data-netlify="true"` with a honeypot, which Netlify handles natively, and the markup and labels were verified — but no real submission was made, so the lead-delivery path is unproven. Submit it once from the live page before relying on it.
3. **The old corporate site's AWS Monitor and crypto-advisory content** (`/aws-monitor`, `/services.html` as a crypto-research page) is not carried into the new site. Those URLs redirect to the closest new equivalents, but the underlying content was a separate business line and is now absent. It was deliberately not smuggled into the new corporate narrative. If it is still a live offering, it needs its own page and its own route — it is a decision, not an oversight.
4. **Resolved — CI runs on GitHub Actions and is green.** The workflow at `.github/workflows/deploy.yml` completed the full cycle on 2026-11-17: build, QA gate, four site deploys, production verification. The host-side watcher and its launchd agent have been removed. The four sites are not linked to the repo in Netlify's own GitHub integration — that needs an interactive GitHub App authorisation — so the workflow deploys through the Netlify API instead; see §2.
5. **Resolved — blog posts migrated.** See item 1. The source fragments remain in `/Users/alfie/projects/goodciso-website/blog/` and the migration is reproducible with `python3.12 migrate_insights.py`.

6. **`llms-full.txt` was never published.** A previous draft of this note listed it as a lost file — it never existed on the live site and the old build never emitted it. `llms.txt` and `agent-instructions.txt` were preserved correctly.

---

## 11. The governing document

**`docs/capability-register.md`** classifies every AWARE capability as IMPLEMENTED, PARTIALLY IMPLEMENTED, DEMONSTRATION, ROADMAP or UNVERIFIED, against three separate axes — does the code exist, is it wired into a runtime path, is it test-covered — and cites file and line for each claim.

It also carries a **"claims we must not make"** table of 20 specific claims that the source does not support, and a **"claims we can make"** list of 12 that it does.

Any change to the AWARE product should update that register first. The website copy is downstream of it. The three claims most likely to be reintroduced by accident are:

- **Commit Guard** — does not exist in `src/`. Roadmap.
- **Revocation cascade** — explicitly retracted in AWARE 2.12.2. Revocation is single-agent.
- **T0–T4 as enforcement tiers** — the labels exist in the UI, but `src/policies/engine.js` does not branch on tier. The engine enforces by tool risk and data tier.
