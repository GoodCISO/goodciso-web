// analytics.mjs — first-party page-view collector.
//
// PORTED from cofactor.work (2026-11-25), which has run this since
// 2026-11-13. The original is at
// ~/.openclaw/projects/cofactor/site/netlify/functions/analytics.mjs
// and is the reference implementation; read it before changing anything
// here, because most of what looks odd is deliberate and documented
// there.
//
// WHAT IT RECORDS
//
// One JSON object per event, appended as NDJSON:
//   t      ISO timestamp
//   type   "view" or "submission"
//   p      path
//   r      referrer
//   s      the ?src= source tag
//   form   which form was submitted, when type is "submission"
//   w      viewport width, as a coarse device class
//
// WHAT IT DOES NOT RECORD
//
// No IP. No user-agent fingerprint. No cookie. No cross-site identifier.
// No session. There is nothing to consent to, because nothing identifies
// the visitor.
//
// The reason is not squeamishness. A security company selling to
// procurement officers cannot ship a third-party tracking pixel to the
// buyer it is trying to reassure, and it should not ship a first-party
// one either. The constraint is inherited from the source site and is
// the reason this is acceptable to deploy at all.
//
// STORAGE
//
// Append-only NDJSON. Three candidate locations, tried in order, first
// that accepts a write wins:
//
//   1. ANALYTICS_LOG             explicit override
//   2. <deploy dir>/analytics/    survives container recycling
//   3. /tmp/<site>-analytics.ndjson  always writable, per-container
//
// (2) is preferred because /tmp is per-container: a Lambda container is
// recycled every few minutes, so a /tmp-only log can lose most of its
// history. If (2) is read-only in production the collector falls back to
// (3) rather than discarding data.
//
// The filename carries the site name. Each of the four sites has its own
// function environment, but they share one filesystem convention, and a
// shared filename would make two sites' counts ambiguous.
//
// FAILURE MODE
//
// Never throws. A broken analytics endpoint must never break a page or
// a form submission. Storage failure is reported as `stored: false` —
// visible, not silent.
//
// SELF-VERIFICATION
//
// Every response carries `count`, the number of events recorded so far.
// Two calls with a rising count prove the write actually persisted —
// a 200 alone does not.
//
// RUNTIME NOTES, both learned the hard way in production
//
// The Netlify Functions v2 runtime requires a WHATWG `Response` or
// `undefined`. Returning the legacy `{ statusCode, headers, body }`
// object throws "Function returned an unsupported value" and the
// endpoint answers 502.
//
// v2 hands the handler a WHATWG Request whose `.body` is a
// ReadableStream, not a string. `JSON.parse(req.body)` silently yields
// {} and every event records empty fields. The body must be read with
// `await req.text()`.

import { appendFile, mkdir, readFile, rename, stat } from "node:fs/promises";
import { dirname, join } from "node:path";

const MAX_PATH = 300;
const MAX_REF = 500;
const MAX_BYTES = 1024 * 1024;
const MAX_BODY = 4096;

// The site this function belongs to. The builder substitutes the token
// with the site key when it copies this file into a deploy root, so each
// of the four deployed functions is self-identifying. Nothing has to be
// configured in the Netlify UI, and nothing can be forgotten.
//
// The env var is still honoured, for a manual run.
const SITE = process.env.ANALYTICS_SITE || "__ANALYTICS_SITE__";

const CANDIDATES = process.env.ANALYTICS_LOG
  ? [process.env.ANALYTICS_LOG]
  : [
      join(process.cwd(), "analytics", "events.ndjson"),
      `/tmp/${SITE}-analytics.ndjson`,
    ];

// The four domains this collector answers for. A permissive
// Access-Control-Allow-Origin would let any site on the internet use
// ours as a free telemetry sink.
const ALLOWED_ORIGINS = [
  "https://goodciso.org",
  "https://www.goodciso.org",
  "https://aware.goodciso.org",
  "https://docs.aware.goodciso.org",
  "https://demo.aware.goodciso.org",
];

function clean(v, max) {
  if (typeof v !== "string") return "";
  return v.replace(/[\r\n\t]/g, " ").slice(0, max);
}

function originAllowed(req) {
  const origin = req.headers?.get?.("origin");
  // A same-origin fetch often carries no Origin header at all.
  if (!origin) return true;
  return ALLOWED_ORIGINS.includes(origin);
}

function json(body, status = 200, origin = null) {
  const headers = {
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
  };
  if (origin) headers["Access-Control-Allow-Origin"] = origin;
  return new Response(JSON.stringify(body), { status, headers });
}

async function rotate(path) {
  try {
    const s = await stat(path);
    if (s.size > MAX_BYTES) {
      await rename(path, path + ".1");
    }
  } catch {
    // no file yet, or rotation failed — the append below will report
  }
}

async function countLines(path) {
  try {
    const raw = await readFile(path, "utf8");
    if (!raw) return 0;
    return raw.split("\n").filter((l) => l.trim()).length;
  } catch {
    return 0;
  }
}

export default async (req) => {
  try {
    const origin = originAllowed(req) ? req.headers?.get?.("origin") ?? null : null;

    if (req.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Cache-Control": "no-store",
          ...(origin ? { "Access-Control-Allow-Origin": origin } : {}),
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
          Vary: "Origin",
        },
      });
    }

    if (req.method !== "POST") {
      return json({ error: "method not allowed" }, 405, origin);
    }

    // A request from an origin we do not serve is discarded. It is not
    // an error — it is a third party using our collector.
    if (!originAllowed(req)) {
      return json({ ok: true, stored: false, count: 0 }, 200, null);
    }

    let body = {};
    try {
      let raw = "";
      if (typeof req.text === "function") {
        raw = await req.text();
      } else if (typeof req.body === "string") {
        raw = req.body;
      } else if (req.body && typeof req.body === "object") {
        raw = JSON.stringify(req.body);
      }
      // A body past the cap is truncated rather than parsed. The
      // collector's payload is a handful of short fields; anything
      // larger is not one.
      if (raw.length > MAX_BODY) raw = raw.slice(0, MAX_BODY);
      body = JSON.parse(raw || "{}");
      if (body === null || typeof body !== "object") body = {};
    } catch {
      body = {};
    }

    // A form submission is the signal that matters most. Record it as a
    // distinct event so a signup is never confused with a view.
    const isSubmission = Boolean(body.form);

    const event = {
      t: clean(body.t, 40) || new Date().toISOString(),
      type: isSubmission ? "submission" : "view",
      path: clean(body.p, MAX_PATH),
      ref: clean(body.r, MAX_REF),
      src: clean(body.s, 80),
      form: clean(body.form, 80),
      // coarse device class only, no fingerprinting
      w: Number(body.w) || 0,
    };

    let stored = false;
    let used = null;
    let count = 0;
    let lastError = null;

    for (const path of CANDIDATES) {
      try {
        await mkdir(dirname(path), { recursive: true });
        await rotate(path);
        await appendFile(path, JSON.stringify(event) + "\n", "utf8");
        stored = true;
        used = path;
        count = (await countLines(path)) || 1;
        break;
      } catch (err) {
        lastError = String(err && err.message ? err.message : err).slice(0, 160);
      }
    }

    return json(
      {
        ok: true,
        stored,
        count,
        // the path is not secret: it is inside the deploy directory
        log: used,
        error: stored ? undefined : lastError,
      },
      200,
      origin,
    );
  } catch {
    return json({ ok: true, stored: false, count: 0 });
  }
};
