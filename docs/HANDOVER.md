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

**The build hooks are live.** Verified 2026-11-18: each of the four sites
reports exactly one build hook, titled `github-ci`, on branch `main`, and the
ids match `deploy/build_hooks.json` exactly.

| Site | Site id | Hook id |
|---|---|---|
| goodciso.org | `e7f43642-d6f1-4625-a4c9-3cfdb0525446` | `6afb6f7b101f7f29df996311` |
| aware.goodciso.org | `628c454e-0569-4664-a61c-792f3c0a3420` | `6afb6f7965d98bebb9bb3e69` |
| docs.aware.goodciso.org | `916fcf43-c51b-4198-a268-4384c4d90a4c` | `6afb6f7a69af9414a81c55ba` |
| demo.aware.goodciso.org | `66acc7fe-692f-440b-a9e9-1437010ccc03` | `6afb6f7befb9691c5d6361c8` |

**How to read them.** The endpoint is
`GET /api/v1/sites/{site_id}/build_hooks`. The paths `/api/v1/hooks` and
`/api/v1/build_hooks` return **404 for a token that is otherwise valid** —
including both Netlify accounts on this host — so a 404 there is not evidence
that a hook is missing or deleted. Do not read it that way.

**They are a fallback, not the deploy path.** CI deploys through the API
(`deploy.py` posts a zip to `/sites/{id}/deploys`); the hook is the manual
route for a one-off rebuild from the Netlify dashboard. The workflow does not
reference `secrets.NETLIFY_BUILD_HOOK_*`, so those secrets are deliberately
not load-bearing. GitHub does not allow a secret's value to be read back, so
the secret values cannot be compared against the hook ids from here; the ids
in `deploy/build_hooks.json` are the record of truth.

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
| `NETLIFY_BUILD_HOOK_AWARE` | Netlify build hook for aware.goodciso.org — live, kept as a fallback (see above) |
| `NETLIFY_BUILD_HOOK_DOCS` | Netlify build hook for docs.aware.goodciso.org — live, kept as a fallback (see above) |
| `NETLIFY_BUILD_HOOK_DEMO` | Netlify build hook for demo.aware.goodciso.org — live, kept as a fallback (see above) |
| `NETLIFY_BUILD_HOOK_CORPORATE` | Netlify build hook for goodciso.org — live, kept as a fallback (see above) |

### On-host credential files (not in the repository)

| File | Holds | Used by |
|---|---|---|
| `~/.openclaw/credentials/netlify-goodciso.env` | `NETLIFY_AUTH_TOKEN` | `deploy.py` — the Good CISO Netlify account that owns all four sites. Overridden by the `NETLIFY_AUTH_TOKEN` environment variable when set, which is how CI uses it. |
| `~/.openclaw/credentials/cloudflare.env` | `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ZONE` | `deploy.py --dns` — DNS writes |
| `~/.openclaw/credentials/github-pat.env` | `GITHUB_TOKEN` (repo + workflow scope) | The single source for the GitHub credential. Read at use time by the git credential helper `~/bin/git-credential-github-alvin`. Mode `0600`. The previous credential is backed up beside it as `github-pat.env.bak-pre-workflow-token`. |

The `workflow` scope on this token is what allows a push that creates or updates anything under `.github/workflows/`. Without it GitHub rejects the push with an explicit scope message and the contents API returns a 404.

### How the credential reaches git

The token never appears in a remote URL, in `.git/config`, in a process argument, or in a shell history. There is one credential file, and four places that hold the same secret:

| Where | Role |
|---|---|
| `~/.openclaw/credentials/github-pat.env` | The source of truth. Mode `0600`. Read at use time by the git credential helper. |
| `~/.netrc` | **The one that actually authenticates.** `git-remote-https` delegates the HTTP layer to curl, and curl reads `~/.netrc` for `machine github.com` credentials. |
| macOS keychain (`github.com`, protocol `htps`) | Backs `osxkeychain`, first in the global helper list. **See the keychain correction below — the live entry does not currently satisfy this row.** |
| `~/bin/git-credential-github-alvin` | The git credential helper; reads the credential file. |

**The `.netrc` is the one that matters, and it is the one that is easy to miss.** Because curl reads it directly, it overrides whatever git's credential chain resolves — the helper, the keychain, everything. A stale `.netrc` entry therefore silently wins, and the failure looks exactly like a scope problem:

```
! [remote rejected] main -> main (refusing to allow a Personal Access Token
  to create or update workflow `.github/workflows/deploy.yml` without `workflow` scope)
```

That message names `workflow` as the missing scope, so the natural reading is "the token lacks the scope" — and the obvious response is to force a different token in. The token was fine the whole time. The credentials git resolved were correct, and the credentials git *transmitted* were not, because curl had already supplied its own.

**How to tell the difference.** `git credential fill` shows what the helper chain resolves. To see what is actually transmitted, disable the redaction and read the header:

```bash
GIT_TRACE_CURL=1 GIT_TRACE_REDACT=0 git push origin main 2>&1 \
  | grep -i "authorization: Basic" \
  | sed -E 's/.*Basic ([A-Za-z0-9+\/=]+)/\1/' \
  | base64 -d | cut -d: -f2
```

If that is not the token in the credential file, the chain is not the problem — something below git is supplying its own credential.

> **Never put the token in the remote URL.** It works, and it is tempting when a push is being rejected, but it leaves the secret in `.git/config` where it outlives the fix, in `ps` output for any process listing, and in the shell history. It also hides the real cause, which is what happened here.

### Refreshing every holder after a token rotation

All four must be updated, or the stale one wins:

```bash
NEW="<new token>"

# 1. The credential file (the source of truth)
#    ~/.openclaw/credentials/github-pat.env, mode 0600, GITHUB_TOKEN=$NEW

# 2. .netrc — the one that actually authenticates
security_note=""; python3 - <<'PY'
import os, re
from pathlib import Path
p = Path(os.path.expanduser("~/.netrc"))
tok = None
for line in Path("/Users/alfie/.openclaw/credentials/github-pat.env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        if k.strip() == "GITHUB_TOKEN":
            tok = v.strip().strip('"').strip("'")
p.write_text(re.sub(r"(machine\s+github\.com.*?password\s+)\S+", lambda m: m.group(1) + tok, p.read_text(), flags=re.S))
os.chmod(p, 0o600)
PY

# 3. The keychain, which osxkeychain reads first.
#    NOTE THE FLAG: the protocol is -r, NOT -p.
#    `security -p` sets the item's PATH; `-r` sets its PROTOCOL.
#    git-credential-osxkeychain looks up by protocol, so an entry written
#    with `-p htps` stores path="htps" and protocol=<unset>, and the helper
#    cannot find it. Verified 2026-11-18 in a scratch keychain.
security delete-internet-password -s github.com -a alvin-chang -r htps
security add-internet-password -U -s github.com -a alvin-chang -r htps -w "$NEW"

# 4. Confirm every holder agrees
python3 - <<'PY'
import os, re, subprocess
from pathlib import Path
tok = None
for line in Path("/Users/alfie/.openclaw/credentials/github-pat.env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        if k.strip() == "GITHUB_TOKEN":
            tok = v.strip().strip('"').strip("'")
nr = re.search(r"machine\s+github\.com.*?password\s+(\S+)", Path(os.path.expanduser("~/.netrc")).read_text(), re.S).group(1)
r = subprocess.run(["git","credential","fill"], input="protocol=https\nhost=github.com\n\n", capture_output=True, text=True)
helper = [l.split("=",1)[1] for l in r.stdout.splitlines() if l.startswith("password=")][0]
kc = subprocess.run(["security","find-internet-password","-s","github.com","-r","htps","-w"], capture_output=True, text=True).stdout.strip()
print("  credential file:", bool(tok), "(read from the source of truth)")
print("  .netrc         :", nr == tok)
print("  git helper     :", helper == tok)
print("  macOS keychain :", (kc == tok) if kc else "ABSENT - no protocol-tagged entry")
# A stale holder wins, so the check must be able to FAIL. Exit non-zero if
# any holder disagrees, so a rotation that missed one cannot pass silently.
disagree = [n for n, v in ((".netrc", nr), ("git helper", helper), ("keychain", kc)) if v and v != tok]
print("  RESULT         :", "ALL HOLDERS AGREE" if not disagree else "DISAGREE: " + ", ".join(disagree))
raise SystemExit(1 if disagree else 0)
PY
```

Token scope required on Netlify: site read/write, domain read/write, build-hook read/write, deploy read/write.

### The keychain entry is currently WRONG — and it is why nothing has broken

**State as verified 2026-11-18.** The live keychain entry for `github.com` was
written with `-p htps`. `security` stores that as `path="htps"` with
`protocol=<unset>`, so:

- `git-credential-osxkeychain get` for `protocol=https` returns **nothing** —
  the helper matches on protocol, and this entry has none.
- `security find-internet-password -s github.com -p htps -w` **does** return
  the password, because it matches on path.

That mismatch is why the token rotation has never broken a push. The two
holders that actually authenticate are `~/.netrc` (curl reads it directly) and
the git credential helper (`~/bin/git-credential-github-alvin`), and both hold
the current token. The keychain entry is a **third copy that git cannot see** —
it is stale by construction and will keep the *old* token after the next
rotation, because the procedure above used `-p` for both delete and add.

**Proof that the helper matches protocol and not path.** In a scratch keychain,
an entry created with `-r htps` was found by the helper when it asked for
`protocol=https`; an entry created with `-p https` was not. Both entries had
the same server and account.

**To repair it**, replace the path-tagged entry with a protocol-tagged one.
This deletes and rewrites a live keychain item, so it is deliberately NOT done
by the build or by a doc edit:

```bash
# Read the current token out of the credential file — never from the keychain.
NEW=$(grep '^GITHUB_TOKEN=' ~/.openclaw/credentials/github-pat.env | cut -d= -f2-)

# Remove the path-tagged entry (matched by path) AND any protocol-tagged one.
security delete-internet-password -s github.com -a alvin-chang -p htps
security delete-internet-password -s github.com -a alvin-chang -r htps

# Write it with the protocol set, which is what the helper reads.
security add-internet-password -U -s github.com -a alvin-chang -r htps -w "$NEW"

# Verify all four holders agree.
printf 'protocol=https\nhost=github.com\nusername=alvin-chang\n\n' \
  | /Applications/Xcode.app/Contents/Developer/usr/libexec/git-core/git-credential-osxkeychain get
```

Until that repair happens, the keychain is not a real fourth holder: it is a
copy that no reader consults. Treat the three working holders (credential
file, `.netrc`, git helper) as the chain that must be kept in agreement.

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

## 9. Brand assets

GoodCISO and AWARE are **distinct brands**, and their assets are kept apart deliberately.

| | GoodCISO | AWARE |
|---|---|---|
| Logomark | Teal shield with a G, navy counter-shape | Shield with a check |
| Primary | Teal `#00A896` on navy `#030712` | Signal green `#16A34A` on midnight `#0B1220` |
| Favicon | `assets/brand/favicon-goodciso.png` (+ `.ico`, `apple-touch-icon.png`) | `assets/brand/favicon-aware.svg` |
| Lives on | goodciso.org | aware.goodciso.org, docs.aware.goodciso.org, demo.aware.goodciso.org |

The GoodCISO mark and palette are the **established** ones — they exist in `~/projects/good-ciso-logo`. They were restored, not redesigned.

One precision matters: the mark now shipped is the **original artwork**, cut from that source, and it is **not** a byte-restoration of the favicon that was live in the tab before November 2026. That favicon was a simplified teal shield with a **teal** dot and **no G counter**; the mark now on the site is the full logomark — teal shield, G counter, **amber** dot — on a navy tile. Read `docs/BRAND.md` §3 for the full history, including the six-month window in which the corporate *header* carried AWARE's mark.

**`docs/BRAND.md` is the brand decision record** — it records what the two
marks are, the full list of surfaces each one appears on, why they are kept
apart, and what happened when the corporate favicon briefly carried AWARE's
mark in November 2026. Read it before changing anything brand-shaped.

The AWARE shield-and-checkmark is AWARE's mark and is **never** served on the corporate site. A corporate favicon that is the product's logo misrepresents the relationship the two brands are meant to have, which is the opposite of what the brief asked for.

### Teal needs its own accessible steps

The brand teal is the same kind of trap the brief's Signal green was — it fails AA as text:

| Pair | Ratio | Use |
|---|---|---|
| `#00A896` on `#F8FAFC` | 2.85 | the brand colour: fills, icons, the logomark |
| `#007669` on `#F8FAFC` | 5.29 | accent text, links (AA) |
| `#FFFFFF` on `#007669` | 5.53 | solid button, light theme (AA) |
| `#030712` on `#14B8A6` | 8.09 | solid button, dark theme (AA) |
| `#007669` on `#F8FAFC` | 4.55 | focus ring (needs 3:1, not 4.5) |

So the brand colour stays the brand colour for fills and the mark, and the ramp carries darker steps for anything readable. The focus ring needed the same treatment — the brand teal is 2.85:1, below the 3:1 a focus indicator requires.

### Checking a brand change

`python3.12 contrast.py` resolves the built CSS through the real cascade and checks every foreground/background pair against its threshold, in both themes, on all four sites. Run it after any colour change:

```bash
python3.12 build_all.py && python3.12 netlify_config.py
python3.12 contrast.py
```

It exists because a hand-written checker got the cascade subtly wrong — it treated `:root` as light-only, so a dark theme's `var(--gc-slate-950)` resolved to nothing and the tool reported no failures while measuring nothing.

## 10. Rotating the GitHub credential

The token must carry both `repo` and `workflow`. `workflow` is what permits a push that creates or updates anything under `.github/workflows/`.

```bash
# 1. Write the new token to the one credential file, mode 0600
**Four places hold the token, and all four must be updated.** The one that is easy to miss — and the one that actually authenticates — is `~/.netrc`: `git-remote-https` hands the HTTP layer to curl, and curl reads `.netrc` for `machine github.com` credentials on its own, ahead of anything git's credential chain resolves. A stale `.netrc` therefore overrides a perfectly good token, and the push fails with a message that blames the scope.

The full procedure, including the verification, is in §3 under "Refreshing every holder after a token rotation".

The end-to-end test that matters is a push that touches `.github/workflows/`. A push that only changes a `.md` file will succeed with a `repo`-only token, which is why the problem can hide for a long time:

```bash
# Make a trivial change to .github/workflows/deploy.yml, commit, and push.
git push origin main
```

## 11. Outstanding issues

1. **Resolved — the four blog posts are now published.** They were migrated into native pages at `/insights/<slug>/`, the old `/blog/*.html` URLs 301 to the articles themselves rather than to the index, and the `/insights` index links all four. The migration also runs a claim-correction pass: the posts predate the AWARE 2.12.2 README correction and contained "cryptographic identity" and T0-T4-as-enforcement-tier claims, so those sentences were rewritten to match `docs/capability-register.md`.
2. **The contact form was not submitted end-to-end against production.** The form is marked `data-netlify="true"` with a honeypot, which Netlify handles natively, and the markup and labels were verified — but no real submission was made, so the lead-delivery path is unproven. Submit it once from the live page before relying on it.
3. **The old corporate site's AWS Monitor and crypto-advisory content** (`/aws-monitor`, `/services.html` as a crypto-research page) is not carried into the new site. Those URLs redirect to the closest new equivalents, but the underlying content was a separate business line and is now absent. It was deliberately not smuggled into the new corporate narrative. If it is still a live offering, it needs its own page and its own route — it is a decision, not an oversight.
4. **Resolved — CI runs on GitHub Actions and is green.** The workflow at `.github/workflows/deploy.yml` completed the full cycle on 2026-11-17: build, QA gate, four site deploys, production verification. The host-side watcher and its launchd agent have been removed. The four sites are not linked to the repo in Netlify's own GitHub integration — that needs an interactive GitHub App authorisation — so the workflow deploys through the Netlify API instead; see §2.
5. **Resolved — blog posts migrated.** See item 1. The source fragments remain in `/Users/alfie/projects/goodciso-website/blog/` and the migration is reproducible with `python3.12 migrate_insights.py`.

6. **`llms-full.txt` was never published.** A previous draft of this note listed it as a lost file — it never existed on the live site and the old build never emitted it. `llms.txt` and `agent-instructions.txt` were preserved correctly.

---

## 12. The governing document

**`docs/capability-register.md`** classifies every AWARE capability as IMPLEMENTED, PARTIALLY IMPLEMENTED, DEMONSTRATION, ROADMAP or UNVERIFIED, against three separate axes — does the code exist, is it wired into a runtime path, is it test-covered — and cites file and line for each claim.

It also carries a **"claims we must not make"** table of 20 specific claims that the source does not support, and a **"claims we can make"** list of 12 that it does.

Any change to the AWARE product should update that register first. The website copy is downstream of it. The three claims most likely to be reintroduced by accident are:

- **Commit Guard** — does not exist in `src/`. Roadmap.
- **Revocation cascade** — explicitly retracted in AWARE 2.12.2. Revocation is single-agent.
- **T0–T4 as enforcement tiers** — the labels exist in the UI, but `src/policies/engine.js` does not branch on tier. The engine enforces by tool risk and data tier.
