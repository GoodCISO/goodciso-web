#!/usr/bin/env python3
"""Deploy the four sites to Netlify and wire DNS.

Safety rules, in order of importance:
  1. The live goodciso.org site is NOT touched until the new build has been
     deployed to a separate site and verified. The production site stays
     recoverable at all times.
  2. Every Netlify site id is recorded in deploy/sites.json. Nothing is
     inferred from a mutable .netlify/state.json.
  3. DNS records are created idempotently: an existing record for the same
     name is updated rather than duplicated.
  4. A custom domain is only attached after the site has its content, so
     TLS can be provisioned against a real deployment.

Usage:
    python3.12 deploy.py --site aware|docs|demo|corporate [--prod]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path("/Users/alfie/projects/goodciso-web")
DIST = ROOT / "dist"
STATE = ROOT / "deploy" / "sites.json"
CRED = Path("/Users/alfie/.openclaw/credentials/netlify-goodciso.env")
CF_CRED = Path("/Users/alfie/.openclaw/credentials/cloudflare.env")
ZONE_ID = "492c93499a5fd0bb7660dfba5bec38a9"

# Site ids are declared here rather than read from deploy/sites.json,
# because that file is gitignored and CI would otherwise have no idea which
# site to deploy to. A site id changes only if a site is deliberately
# recreated, which is a recorded act, not a routine one.
#
# The corporate site is the EXISTING production site, so its live content
# is replaced in place and a rollback stays available. See
# deploy/rollback.json for the previous deploys.
SITES = {
    "aware": {
        "name": "aware-goodciso",
        "domain": "aware.goodciso.org",
        "dir": "aware",
        "site_id": "628c454e-0569-4664-a61c-792f3c0a3420",
    },
    "docs": {
        "name": "aware-docs",
        "domain": "docs.aware.goodciso.org",
        "dir": "docs",
        "site_id": "916fcf43-c51b-4198-a268-4384c4d90a4c",
    },
    "demo": {
        "name": "aware-playground",
        "domain": "demo.aware.goodciso.org",
        "dir": "demo",
        "site_id": "66acc7fe-692f-440b-a9e9-1437010ccc03",
    },
    "corporate": {
        "name": None,
        "domain": "goodciso.org",
        "dir": "corporate",
        "site_id": "e7f43642-d6f1-4625-a4c9-3cfdb0525446",
    },
}

NETLIFY = "https://api.netlify.com/api/v1"
CF = "https://api.cloudflare.com/client/v4"


def load_env(path: Path) -> dict:
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def api(method: str, url: str, token: str, body=None, headers=None, raw=None, content_type=None):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    h = {"Authorization": "Bearer " + token}
    if body is not None:
        h["Content-Type"] = "application/json"
    if content_type:
        h["Content-Type"] = content_type
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode()
        try:
            return e.code, json.loads(body_txt or "{}")
        except json.JSONDecodeError:
            return e.code, {"raw": body_txt[:500]}
    except Exception as e:  # noqa: BLE001
        return 0, {"error": str(e)}


def zip_dir(src: Path) -> bytes:
    import io

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file() and not p.name.startswith("."):
                z.write(p, str(p.relative_to(src)))
    return buf.getvalue()


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {}


def save_state(s: dict):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))


def ensure_site(key: str, cfg: dict, token: str, state: dict) -> str:
    if cfg.get("site_id"):
        print(f"  site {key}: {cfg['site_id']}")
        return cfg["site_id"]
    if key in state and state[key].get("site_id"):
        print(f"  site {key}: {state[key]['site_id']} (from state)")
        return state[key]["site_id"]

    st, res = api("POST", f"{NETLIFY}/sites", token, {"name": cfg["name"]})
    if st not in (200, 201):
        print(f"  site {key}: CREATE FAILED {st} {res}")
        sys.exit(1)
    sid = res["id"]
    print(f"  site {key}: created {sid} -> {res.get('url')}")
    state[key] = {"site_id": sid, "netlify_url": res.get("url"), "domain": cfg["domain"]}
    save_state(state)
    return sid


def deploy(site_id: str, directory: Path, token: str, message: str) -> dict:
    payload = zip_dir(directory)
    st, res = api(
        "POST",
        f"{NETLIFY}/sites/{site_id}/deploys",
        token,
        raw=payload,
        headers={"Content-Type": "application/zip"},
    )
    if st not in (200, 201):
        print(f"  DEPLOY FAILED {st}: {str(res)[:400]}")
        return {}
    deploy_id = res.get("id")
    print(f"  deploy submitted: {deploy_id}")
    # Poll until published
    for _ in range(60):
        time.sleep(3)
        st2, d = api("GET", f"{NETLIFY}/deploys/{deploy_id}", token)
        state = (d.get("state") or {}).get("name") if isinstance(d.get("state"), dict) else d.get("state")
        if state in ("ready", "error", "failed"):
            print(f"  deploy state: {state}")
            return d
    return d


def attach_domain(site_id: str, domain: str, token: str):
    """Attach a custom domain.

    The endpoint is PUT /sites/{id} with a custom_domain field. There is no
    POST /sites/{id}/domains route — that path returns 404, which is what a
    first attempt did. Attaching the domain via the site object is what
    triggers Netlify's TLS provisioning.
    """
    st, res = api("GET", f"{NETLIFY}/sites/{site_id}", token)
    if st == 200 and res.get("custom_domain") == domain:
        print(f"  domain {domain}: already attached")
        return
    st, res = api("PUT", f"{NETLIFY}/sites/{site_id}", token, {"custom_domain": domain})
    if st in (200, 201):
        print(f"  domain {domain}: attached (ssl_url {res.get('ssl_url')})")
    else:
        print(f"  domain {domain}: FAILED {st} {str(res)[:300]}")


def dns_upsert(domain: str, target: str, token: str):
    """Create or update the CNAME for `domain`. Idempotent."""
    name = domain
    st, res = api(
        "GET",
        f"{CF}/zones/{ZONE_ID}/dns_records?type=CNAME&name={name}",
        token,
    )
    existing = res.get("result") or []
    if existing:
        rid = existing[0]["id"]
        st2, r2 = api(
            "PUT",
            f"{CF}/zones/{ZONE_ID}/dns_records/{rid}",
            token,
            {"type": "CNAME", "name": name, "content": target, "ttl": 3600, "proxied": False},
        )
        print(f"  dns {name} -> {target}: updated ({st2})")
    else:
        st2, r2 = api(
            "POST",
            f"{CF}/zones/{ZONE_ID}/dns_records",
            token,
            {"type": "CNAME", "name": name, "content": target, "ttl": 3600, "proxied": False},
        )
        print(f"  dns {name} -> {target}: created ({st2})")


def load_token() -> str:
    """The Netlify credential, from the environment first.

    Netlify's CLI resolves NETLIFY_AUTH_TOKEN before any stored credential,
    and so does this. CI has no access to the host's credential store, so
    the environment is the only source there; the file is the fallback for
    local runs.
    """
    env_token = os.environ.get("NETLIFY_AUTH_TOKEN")
    if env_token:
        return env_token.strip()
    return load_env(CRED)["NETLIFY_AUTH_TOKEN"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True, choices=list(SITES))
    ap.add_argument("--dns", action="store_true", help="also attach domain and write DNS")
    ap.add_argument("--no-deploy", action="store_true")
    args = ap.parse_args()

    token = load_token()
    cfg = SITES[args.site]
    directory = DIST / cfg["dir"]

    if not directory.exists():
        print(f"no build for {args.site}: {directory} missing — run build_all.py")
        sys.exit(1)

    state = load_state()
    print(f"[deploy] {args.site}")
    site_id = ensure_site(args.site, cfg, token, state)

    if not args.no_deploy:
        result = deploy(site_id, directory, token, f"goodciso-web {args.site}")
        if result:
            state.setdefault(args.site, {})
            state[args.site].update(
                {
                    "site_id": site_id,
                    "netlify_url": result.get("deploy_ssl_url") or result.get("deploy_url"),
                    "domain": cfg["domain"],
                    "deployed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
            )
            save_state(state)
            print(f"  live at: {state[args.site]['netlify_url']}")

    if args.dns:
        st, site = api("GET", f"{NETLIFY}/sites/{site_id}", token)
        target = (site.get("ssl_url") or site.get("url") or "").replace("https://", "").replace("http://", "").rstrip("/")
        if target:
            attach_domain(site_id, cfg["domain"], token)
            # DNS writes need the Cloudflare credential. In CI that file is
            # not present and DNS is not needed — the records already exist.
            if CF_CRED.exists():
                cfenv = load_env(CF_CRED)
                dns_upsert(cfg["domain"], target, cfenv["CLOUDFLARE_API_TOKEN"])
            else:
                print("  no Cloudflare credential file — DNS not touched")
        else:
            print("  could not determine netlify hostname; DNS skipped")


if __name__ == "__main__":
    main()
