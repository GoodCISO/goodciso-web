#!/usr/bin/env python3
"""AWARE product site — aware.goodciso.org.

Every capability claim on this site is governed by
docs/capability-register.md. Status badges are not decoration: they are the
register rendered.
"""
from build import Nav, Page

DOMAIN = "https://aware.goodciso.org"

NAV = [
    Nav("Platform", "/platform"),
    Nav("Architecture", "/architecture"),
    Nav("Developers", "/developers"),
    Nav("Use Cases", "/use-cases"),
    Nav("Trust Centre", "/trust-centre"),
    Nav("Enterprise", "/enterprise"),
    Nav("GitHub", "https://github.com/GoodCISO/aware", external=True),
    Nav("Get Started", "/get-started"),
]

FOOTER = [
    ("Platform", [
        Nav("Overview", "/platform"),
        Nav("Agent identity", "/platform/agent-identity"),
        Nav("Policy engine", "/platform/policy-engine"),
        Nav("T0-T4 constraints", "/platform/t0-t4"),
        Nav("Delegation", "/platform/delegation"),
        Nav("Revocation", "/platform/revocation"),
        Nav("Audit & evidence", "/platform/audit"),
        Nav("Execution assurance", "/platform/execution-assurance"),
    ]),
    ("Resources", [
        Nav("Documentation", "https://docs.aware.goodciso.org", external=True),
        Nav("Playground", "https://demo.aware.goodciso.org", external=True),
        Nav("Architecture", "/architecture"),
        Nav("Trust Centre", "/trust-centre"),
        Nav("GitHub", "https://github.com/GoodCISO/aware", external=True),
        Nav("npm", "https://www.npmjs.com/package/@goodciso/aware", external=True),
    ]),
    ("Company", [
        Nav("GoodCISO", "https://goodciso.org", external=True),
        Nav("Use cases", "/use-cases"),
        Nav("Enterprise", "/enterprise"),
        Nav("Contact", "https://goodciso.org/contact", external=True),
    ]),
]

TAGLINE = "The security control plane for autonomous AI agents."


def _p(slug, title, desc, body, status=""):
    return Page(
        slug=slug,
        title=title,
        description=desc,
        body=body,
        canonical=f"{DOMAIN}/{slug}" if slug != "index" else f"{DOMAIN}/",
        status=status,
    )


PAGES = [
    # ---------------------------------------------------------------- HOME
    _p(
        "index",
        "Security control plane for autonomous AI agents",
        "AWARE gives AI agents a non-human identity, evaluates every tool call against policy before it runs, and records decisions in a verifiable audit chain. Open source, Apache-2.0.",
        """
<section class="gc-hero">
  <div class="gc-container">
    <span class="gc-eyebrow">AWARE &mdash; by GoodCISO</span>
    <h1>Autonomous agents need more than guardrails. They need governance.</h1>
    <p class="gc-hero-sub">A security control plane for agent identity, delegated authority, policy enforcement and accountable execution.</p>
    <div class="gc-hero-actions">
      <a class="gc-btn gc-btn-primary gc-btn-lg" href="/platform">Explore AWARE</a>
      <a class="gc-btn gc-btn-secondary gc-btn-lg" href="https://github.com/GoodCISO/aware">View on GitHub</a>
      <a class="gc-btn gc-btn-ghost gc-btn-lg" href="https://docs.aware.goodciso.org">Documentation</a>
    </div>
    <div class="gc-grid gc-grid-4">
      <div class="gc-card">
        <span class="gc-badge gc-badge-shipped">Implemented</span>
        <h3 class="gc-mt-4">Deny by default</h3>
        <p class="gc-muted gc-mb-0">Every tool call is evaluated. Unknown and high-risk tools are denied even when no policy matches.</p>
      </div>
      <div class="gc-card">
        <span class="gc-badge gc-badge-shipped">Implemented</span>
        <h3 class="gc-mt-4">Agent identity</h3>
        <p class="gc-muted gc-mb-0">Every agent gets a non-human identity with a hashed, rotatable, revocable credential.</p>
      </div>
      <div class="gc-card">
        <span class="gc-badge gc-badge-shipped">Implemented</span>
        <h3 class="gc-mt-4">Verifiable evidence</h3>
        <p class="gc-muted gc-mb-0">Decisions land in a hash chain you can export so a third party can recompute them.</p>
      </div>
      <div class="gc-card">
        <span class="gc-badge gc-badge-roadmap">Roadmap</span>
        <h3 class="gc-mt-4">Execution assurance</h3>
        <p class="gc-muted gc-mb-0">Commit Guard and independent execution verification are specified, not yet shipped.</p>
      </div>
    </div>
  </div>
</section>

<section class="gc-section">
  <div class="gc-container">
    <div class="gc-grid gc-grid-2">
      <div>
        <span class="gc-eyebrow">The problem</span>
        <h2>Guardrails are not governance.</h2>
        <p>A guardrail stops one thing. Governance answers the questions an auditor asks:</p>
        <ul class="gc-list">
          <li><strong>Who</strong> is acting? Not a service account shared by three workflows.</li>
          <li><strong>Under what authority</strong> did it act, and was that authority still valid at the moment of the call?</li>
          <li><strong>What did it decide</strong>, and on what basis?</li>
          <li><strong>Can a third party</strong> independently recompute that decision six months later?</li>
        </ul>
        <p>Most agent frameworks answer the first question badly and the last three not at all. AWARE exists to answer all four, in that order.</p>
      </div>
      <div class="gc-card">
        <h3>The chain of authority</h3>
        <p class="gc-muted">Each stage is a place where an agent&rsquo;s authority can be checked, narrowed or cut. AWARE implements the highlighted stages today.</p>
        <div class="gc-readout gc-mt-4">
          <div class="gc-readout-row"><dt>Intent</dt><dd>declared by the operator</dd></div>
          <div class="gc-readout-row"><dt>Identity</dt><dd><span class="gc-status gc-status-allow">implemented</span> non-human identity, revocable credential</dd></div>
          <div class="gc-readout-row"><dt>Delegated authority</dt><dd><span class="gc-status gc-status-none">roadmap</span> no delegation graph yet</dd></div>
          <div class="gc-readout-row"><dt>Policy</dt><dd><span class="gc-status gc-status-allow">implemented</span> deny-by-default evaluation</dd></div>
          <div class="gc-readout-row"><dt>Commit Guard</dt><dd><span class="gc-status gc-status-none">roadmap</span> atomic commit not implemented</dd></div>
          <div class="gc-readout-row"><dt>Verified execution</dt><dd><span class="gc-status gc-status-none">roadmap</span> no target-side receipt</dd></div>
          <div class="gc-readout-row"><dt>Evidence</dt><dd><span class="gc-status gc-status-allow">implemented</span> hash-chained, exportable</dd></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="gc-section-tight" style="background:var(--gc-surface)">
  <div class="gc-container">
    <span class="gc-eyebrow">What ships</span>
    <h2>The control plane, component by component</h2>
    <p class="gc-muted gc-measure">Each capability below is labelled with its implementation state, taken from the AWARE capability register. Where something is not shipped, this site says so.</p>
    <div class="gc-grid gc-grid-3 gc-mt-8">
      <div class="gc-card"><h3>Agent identity</h3><p class="gc-muted">UUID identity, PBKDF2-hashed credentials, timing-safe comparison, rotation, and session tokens with trust-domain claims.</p><a href="/platform/agent-identity">Read more &rarr;</a></div>
      <div class="gc-card"><h3>Policy engine</h3><p class="gc-muted">ALLOW, DENY, AUDIT or NO_POLICY for every tool call, evaluated against tool risk, data tier and the policy store. Hot reload, no restart.</p><a href="/platform/policy-engine">Read more &rarr;</a></div>
      <div class="gc-card"><h3>Revocation</h3><p class="gc-muted">Revoking an agent invalidates its credential immediately and writes the decision to the audit trail.</p><a href="/platform/revocation">Read more &rarr;</a></div>
      <div class="gc-card"><h3>Audit &amp; evidence</h3><p class="gc-muted">A hash chain with an independent verifier, exportable windows a third party can recompute, and failure outcomes recorded.</p><a href="/platform/audit">Read more &rarr;</a></div>
      <div class="gc-card"><h3>Compliance mapping</h3><p class="gc-muted">Seven frameworks, 184 of 243 CSA AICM v1 controls across all 18 domains, and MITRE ATLAS technique mapping.</p><a href="/trust-centre#compliance">Read more &rarr;</a></div>
      <div class="gc-card"><h3>T0-T4 model</h3><p class="gc-muted">Five tiers that classify and promote an agent&rsquo;s autonomy posture, with validated promotion events.</p><a href="/platform/t0-t4">Read more &rarr;</a></div>
    </div>
  </div>
</section>

<section class="gc-section">
  <div class="gc-container gc-center">
    <h2>Read the source, not the pitch</h2>
    <p class="gc-muted gc-measure" style="margin-inline:auto">AWARE is Apache-2.0 and the capability register that governs this site is public. If we claim something, there is a file and line number behind it.</p>
    <div class="gc-hero-actions" style="justify-content:center">
      <a class="gc-btn gc-btn-primary" href="https://github.com/GoodCISO/aware">Browse the source</a>
      <a class="gc-btn gc-btn-secondary" href="/trust-centre">Trust Centre</a>
    </div>
  </div>
</section>
""",
    ),
    # ------------------------------------------------------------ PLATFORM
    _p(
        "platform",
        "Platform overview",
        "AWARE's control plane: identity, policy, constraints, revocation, audit and evidence. What each layer does today and where it stops.",
        """
<section class="gc-hero gc-hero-sm">
  <div class="gc-container">
    <span class="gc-eyebrow">Platform</span>
    <h1>The control plane</h1>
    <p class="gc-hero-sub">AWARE is a set of enforcement layers that sit between an autonomous agent and the tools it calls. Each layer narrows what the agent can do, and each layer records what it decided.</p>
  </div>
</section>
<section class="gc-section">
  <div class="gc-container">
    <div class="gc-grid gc-grid-2">
      <div class="gc-card">
        <span class="gc-badge gc-badge-shipped">Implemented</span>
        <h3 class="gc-mt-4">Agent identity</h3>
        <p>A non-human identity per agent, with a credential that is stored only as a salted hash, compared in constant time, rotatable, and revocable. Session tokens carry trust domain, blast radius and execution context.</p>
        <p class="gc-muted gc-mb-0"><a href="/platform/agent-identity">Agent identity &rarr;</a></p>
      </div>
      <div class="gc-card">
        <span class="gc-badge gc-badge-shipped">Implemented</span>
        <h3 class="gc-mt-4">Policy engine</h3>
        <p>Every tool call is evaluated before it runs. Unknown tools and high-risk tools are denied even with no matching policy. Decisions are ALLOW, DENY, AUDIT or NO_POLICY, with a stated reason.</p>
        <p class="gc-muted gc-mb-0"><a href="/platform/policy-engine">Policy engine &rarr;</a></p>
      </div>
      <div class="gc-card">
        <span class="gc-badge gc-badge-shipped">Implemented</span>
        <h3 class="gc-mt-4">T0-T4 constraints</h3>
        <p>Five tiers classify an agent&rsquo;s autonomy posture and are promoted through validated events. The engine enforces by tool risk and data classification; the tiers record the posture.</p>
        <p class="gc-muted gc-mb-0"><a href="/platform/t0-t4">T0-T4 model &rarr;</a></p>
      </div>
      <div class="gc-card">
        <span class="gc-badge gc-badge-shipped">Implemented</span>
        <h3 class="gc-mt-4">Revocation</h3>
        <p>Revoking an agent flips its state so its credentials stop verifying, applies a blast-radius penalty to its trail, and writes the decision to the audit trail.</p>
        <p class="gc-muted gc-mb-0"><a href="/platform/revocation">Revocation &rarr;</a></p>
      </div>
      <div class="gc-card">
        <span class="gc-badge gc-badge-shipped">Implemented</span>
        <h3 class="gc-mt-4">Audit &amp; evidence</h3>
        <p>Decisions are written to a hash chain. An independent verifier can recompute it, and an exportable window lets a third party verify a slice without access to your database.</p>
        <p class="gc-muted gc-mb-0"><a href="/platform/audit">Audit &amp; evidence &rarr;</a></p>
      </div>
      <div class="gc-card">
        <span class="gc-badge gc-badge-roadmap">Roadmap</span>
        <h3 class="gc-mt-4">Execution assurance</h3>
        <p>Authorising an action and verifying it happened are different things. AWARE does the first. The second &mdash; atomic commit, target-side enforcement and independent execution verification &mdash; is specified but not built.</p>
        <p class="gc-muted gc-mb-0"><a href="/platform/execution-assurance">Execution assurance &rarr;</a></p>
      </div>
    </div>
  </div>
</section>
""",
    ),
    _p(
        "platform/agent-identity",
        "Agent identity",
        "AWARE gives every agent a non-human identity with a hashed, rotatable, revocable credential and a session token carrying trust domain and blast radius.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Platform</span><h1>Agent identity</h1>
  <p class="gc-hero-sub">An agent is not a user and not a service account. It needs an identity of its own that can be scoped, rotated and revoked without touching the systems it acts on.</p>
</div></section>
<section class="gc-section"><div class="gc-container gc-grid gc-grid-2">
  <div>
    <h2>How identity works</h2>
    <ul class="gc-list">
      <li>A UUID identifies the agent, minted at registration.</li>
      <li>Provisioning generates 32 random bytes, hex-encoded, and returns the raw value <strong>once</strong>.</li>
      <li>What is stored is a salted PBKDF2 hash with a pepper, never the secret itself.</li>
      <li>Verification uses a constant-time comparison, so a rejected credential leaks no timing information.</li>
      <li>Rotation replaces the stored hash immediately.</li>
      <li>Revocation flips the agent&rsquo;s state so the credential stops verifying.</li>
    </ul>
    <p>Session tokens carry extended claims &mdash; trust domain, blast radius, session id and execution context &mdash; so a downstream service can decide whether to honour a call without re-reading the registry.</p>
  </div>
  <div>
    <div class="gc-callout gc-callout-warn">
      <strong>What identity is not, yet</strong>
      AWARE&rsquo;s identity layer authenticates the holder of a shared secret. It does not bind an identity to a key that only the agent holds. There is no X.509 certificate, no Ed25519 key pair and no SPIFFE identifier in the current implementation. Describing it as &ldquo;cryptographic identity that cannot be faked&rdquo; would overstate it.
    </div>
    <div class="gc-callout">
      <strong>Why the difference matters</strong>
      A bearer secret can be replayed by anything that obtains it. A key-bound identity cannot. AWARE closes the replay gap with short-lived sessions, revocation and blast-radius scoring today; key binding is the natural next step.
    </div>
    <h3 class="gc-mt-8">Attestation</h3>
    <p class="gc-muted">Agents present a signed session token. The attestation service verifies it, checks that the session is live, that the agent is still active, and that the trust domain matches the target&rsquo;s.</p>
  </div>
</div></section>
""",
    ),
    _p(
        "platform/policy-engine",
        "Policy engine",
        "AWARE evaluates every tool call against policy before it executes, returning ALLOW, DENY, AUDIT or NO_POLICY with a stated reason. Deny by default.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Platform</span><h1>The policy engine</h1>
  <p class="gc-hero-sub">One function decides whether a tool call proceeds: <code>evaluate()</code>. It is fast, deterministic, explainable, and it defaults to deny.</p>
</div></section>
<section class="gc-section"><div class="gc-container">
  <h2>Decisions</h2>
  <div class="gc-grid gc-grid-4">
    <div class="gc-card"><span class="gc-status gc-status-allow">ALLOW</span><p class="gc-mt-4 gc-mb-0">A matching policy permits the call.</p></div>
    <div class="gc-card"><span class="gc-status gc-status-deny">DENY</span><p class="gc-mt-4 gc-mb-0">The call is refused. This is the default when nothing matches a risky tool.</p></div>
    <div class="gc-card"><span class="gc-status gc-status-audit">AUDIT</span><p class="gc-mt-4 gc-mb-0">The call is permitted but recorded for review.</p></div>
    <div class="gc-card"><span class="gc-status gc-status-none">NO_POLICY</span><p class="gc-mt-4 gc-mb-0">No policy governs this tool at this tier.</p></div>
  </div>
  <h2 class="gc-mt-12">What the engine looks at</h2>
  <div class="gc-table-wrap"><table class="gc-table">
    <thead><tr><th>Signal</th><th>Source</th><th>Effect</th></tr></thead>
    <tbody>
      <tr><td>Tool known?</td><td>Tool catalogue</td><td>Unknown tools are denied outright.</td></tr>
      <tr><td>Risk level</td><td>Tool catalogue</td><td><code>HIGH</code> and <code>CRITICAL</code> tools are denied with no policy present.</td></tr>
      <tr><td>Data tier</td><td>Request context</td><td>PUBLIC &lt; INTERNAL &lt; CONFIDENTIAL &lt; RESTRICTED. A tool may be barred from a higher tier.</td></tr>
      <tr><td>Matching policy</td><td>Policy store</td><td>Conditions on agent, tool, targets and time windows.</td></tr>
      <tr><td>Approval</td><td>Tool catalogue</td><td>Some tools require an approval before the call proceeds.</td></tr>
      <tr><td>Rate and frequency</td><td>Engine counters</td><td>Windowed limits on call frequency and volume.</td></tr>
    </tbody>
  </table></div>
  <div class="gc-callout">
    <strong>Hot reload</strong>
    Policies reload without a restart through <code>/api/policies/hot</code>, so an operator can tighten a rule in response to something they have just seen.
  </div>
  <div class="gc-callout gc-callout-danger">
    <strong>Extensions cannot change a verdict</strong>
    The extension point hands observers a deep copy of the request and the decision. An extension that throws is recorded, never propagated. This is deliberate: an extension that could flip a decision would be a policy bypass, so the contract test asserts it cannot.
  </div>
</div></section>
""",
    ),
    _p(
        "platform/t0-t4",
        "T0-T4 constraint model",
        "AWARE's five autonomy tiers: what each level means, what the engine enforces, and where the tier model stops short of enforcement.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Platform</span><h1>The T0-T4 constraint model</h1>
  <p class="gc-hero-sub">Five levels classify how much autonomy an agent is granted. Every agent is assigned a level before it acts, and promotions are recorded as validated events.</p>
</div></section>
<section class="gc-section"><div class="gc-container">
  <div class="gc-grid gc-grid-5">
    <div class="gc-card"><span class="gc-term">T0</span><h3 class="gc-mt-4">Audit Trail</h3><p class="gc-muted">Every action is logged. Foundational, always on.</p></div>
    <div class="gc-card"><span class="gc-term">T1</span><h3 class="gc-mt-4">Crypto Identity</h3><p class="gc-muted">Every agent gets a non-human identity. Foundational, always on.</p></div>
    <div class="gc-card"><span class="gc-term">T2</span><h3 class="gc-mt-4">Guardrailed</h3><p class="gc-muted">Operational policies constrain what the agent can do.</p></div>
    <div class="gc-card"><span class="gc-term">T3</span><h3 class="gc-mt-4">Policy-Driven</h3><p class="gc-muted">Advanced governance: rate limits and decision routing.</p></div>
    <div class="gc-card"><span class="gc-term">T4</span><h3 class="gc-mt-4">Autonomous</h3><p class="gc-muted">Full self-operation under declared constraints.</p></div>
  </div>
  <div class="gc-callout gc-callout-warn gc-mt-8">
    <strong>Read this before you rely on the tiers</strong>
    The tier is a <em>declared posture and promotion record</em>. The policy engine enforces by tool risk and data classification &mdash; it does not branch on the tier. A T2 agent calling a high-risk tool with no matching policy is denied; a T4 agent calling the same tool is also denied. What the tier changes today is the governance posture recorded against the agent and the promotions it can move through.
  </div>
  <h2 class="gc-mt-12">Promotions</h2>
  <p>Tier promotions are a first-class event. Each one is validated against the published OpenAPI schema, and the valid set is exactly <code>T0</code> through <code>T4</code>. A promotion records who moved the agent and why, so the history of an agent&rsquo;s autonomy is reconstructible.</p>
  <div class="gc-callout gc-callout-danger">
    <strong>Not a guarantee of bounded autonomy</strong>
    &ldquo;T4 agents act autonomously&rdquo; is a description of intent, not a claim that the engine constrains them differently from T2. We would rather say that plainly than let a tier diagram imply enforcement that does not exist.
  </div>
</div></section>
""",
    ),
    _p(
        "platform/delegation",
        "Delegation and hierarchy",
        "AWARE's delegated authority model: the intended design, the current implementation state, and what is missing.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Platform</span><h1>Delegation &amp; hierarchy</h1>
  <p class="gc-hero-sub">The intended model is that a parent agent delegates a bounded subset of its authority to a child, and that the child can never hold more than the parent holds.</p>
</div></section>
<section class="gc-section"><div class="gc-container gc-grid gc-grid-2">
  <div>
    <h2>The intended model</h2>
    <ul class="gc-list">
      <li>A parent agent holds a set of authorities.</li>
      <li>It delegates a named subset to a child, recorded as a signed decision.</li>
      <li>The child&rsquo;s authority is bounded by the parent&rsquo;s, always.</li>
      <li>Revoking the parent invalidates the child&rsquo;s derived authority.</li>
      <li>The chain of delegation is reconstructible for audit.</li>
    </ul>
    <p>This is the design that makes hierarchical revocation possible, and it is the design AWARE&rsquo;s ADRs work towards.</p>
  </div>
  <div>
    <div class="gc-callout gc-callout-danger">
      <strong>Current status: roadmap</strong>
      There is no delegation graph in the shipped implementation. Searching the source for the fields that would carry one &mdash; parent agent, delegating agent, ancestors, child agents &mdash; returns no production match. The sub-agent permission invariant is explicitly deferred in the IETF authorisation ADR.
    </div>
    <p class="gc-mt-6">What exists today: the coordinator that would manage such a graph, and the revocation primitives that would act on one. What does not exist: the graph itself, and the cascade that walks it.</p>
    <p>AWARE&rsquo;s own revocation research reached the same conclusion independently: before you can revoke over a delegation graph, you need a delegation graph.</p>
  </div>
</div></section>
""",
    ),
    _p(
        "platform/revocation",
        "Revocation",
        "Revoking an AWARE agent invalidates its credential immediately, applies a blast-radius penalty and writes the decision to the audit trail. Cascade to derived agents is not yet implemented.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Platform</span><h1>Revocation</h1>
  <p class="gc-hero-sub">The moment an agent is compromised, the credential it holds must stop working. Not eventually, and not after a cache expiry window you forgot to set.</p>
</div></section>
<section class="gc-section"><div class="gc-container gc-grid gc-grid-2">
  <div>
    <h2>What happens on revoke</h2>
    <ol class="gc-list">
      <li>The agent&rsquo;s state flips, so its credential no longer verifies.</li>
      <li>A blast-radius penalty is applied to its trail, so it is deprioritised in scoring.</li>
      <li>The decision is written to the audit trail.</li>
    </ol>
    <h3 class="gc-mt-8">Emergency control</h3>
    <p>For a whole-service stop, the gateway honours <code>AWARE_GATEWAY_KILL_SWITCH=1</code> and returns 503 immediately. For a coordinated stop across nodes, AWARE ships Raft-based kill-signal propagation and leader-election components, with a leader-only guard on propagation.</p>
  </div>
  <div>
    <div class="gc-callout gc-callout-danger">
      <strong>Cascade is not implemented</strong>
      Revoking a parent does <em>not</em> currently revoke its children. The revocation service applies to exactly one agent. The blast-radius logic applies a penalty to that same agent rather than traversing to derived agents. An earlier version of the AWARE README said otherwise; it was corrected in release 2.12.2 because the source did not support it.
    </div>
    <div class="gc-callout gc-callout-warn">
      <strong>Component, not distributed guarantee</strong>
      The Raft propagation and election code is implemented and tested as components, but the running service constructs the revocation service marked <em>pending Raft setup</em>. Treat multi-node propagation as an integration you would complete, not a property you switch on.
    </div>
  </div>
</div></section>
""",
    ),
    _p(
        "platform/audit",
        "Audit and evidence",
        "AWARE writes every decision to a hash chain with an independent verifier, exportable windows a third party can recompute, and recorded failure outcomes.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Platform</span><h1>Audit &amp; evidence</h1>
  <p class="gc-hero-sub">Evidence is the point of the whole system. If the record cannot be independently checked, it is a log, not evidence.</p>
</div></section>
<section class="gc-section"><div class="gc-container gc-grid gc-grid-2">
  <div>
    <h2>How the chain works</h2>
    <p>Each record&rsquo;s hash is computed over the record&rsquo;s canonical serialisation plus the previous record&rsquo;s hash. Altering any earlier record breaks every hash after it.</p>
    <ul class="gc-list">
      <li>An <strong>independent verifier</strong> recomputes the chain using only the standard library, so verification does not require trusting the writer&rsquo;s code.</li>
      <li><strong>Exportable windows</strong> carry their own <code>prevHash</code> and <code>hash</code>, so a third party can verify a slice without access to your database.</li>
      <li><strong>Failure outcomes are recorded</strong> &mdash; timeouts, backend errors, cost caps. The chain evidences completeness, not just success.</li>
    </ul>
  </div>
  <div>
    <div class="gc-callout gc-callout-warn">
      <strong>What the anchor does and does not prove</strong>
      An exported window&rsquo;s anchor is <em>declared, not verified</em>. The first record points outside the window, so it can only be proven to be a chain root when its hash matches the genesis value. Full-chain verification is the stronger check, and it needs the whole chain. We state this rather than letting &ldquo;exportable and verifiable&rdquo; imply more than it does.
    </div>
    <h3 class="gc-mt-8">Where it runs</h3>
    <p class="gc-muted">Decisions, context access and escalations are written through the audit module. A decision chain with a depth metric accompanies the record, so you can see how a conclusion was reached, not only what it was.</p>
  </div>
</div></section>
""",
    ),
    _p(
        "platform/execution-assurance",
        "Execution assurance",
        "The difference between authorising an action, approving it, revalidating it, committing it and verifying it. Which of those AWARE does today, and which are roadmap.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Platform</span><h1>Execution assurance</h1>
  <p class="gc-hero-sub">Five verbs get collapsed into one word in most agent-security marketing. They are not the same guarantee, and the difference is where audits bite.</p>
</div></section>
<section class="gc-section"><div class="gc-container">
  <div class="gc-table-wrap"><table class="gc-table">
    <thead><tr><th>Stage</th><th>Question it answers</th><th>Who is trusted</th><th>AWARE today</th></tr></thead>
    <tbody>
      <tr><td><strong>Authorise</strong></td><td>Is this agent permitted to attempt this at all?</td><td>AWARE</td><td><span class="gc-status gc-status-allow">implemented</span> policy engine decides</td></tr>
      <tr><td><strong>Approve</strong></td><td>Has a human signed off on this specific instance?</td><td>The approver</td><td><span class="gc-status gc-status-allow">implemented</span> approval requirement on tools</td></tr>
      <tr><td><strong>Revalidate</strong></td><td>Is the authority still valid at the moment of action, after any state change?</td><td>AWARE</td><td><span class="gc-status gc-status-none">partial</span> session and revocation checks, no general revalidation hook</td></tr>
      <tr><td><strong>Commit</strong></td><td>Did the change land atomically, or half?</td><td>The target system</td><td><span class="gc-status gc-status-none">roadmap</span> Commit Guard, not implemented</td></tr>
      <tr><td><strong>Verify</strong></td><td>Did the target actually do what was authorised?</td><td>An independent party</td><td><span class="gc-status gc-status-none">roadmap</span> no execution receipt</td></tr>
    </tbody>
  </table></div>
  <div class="gc-callout gc-callout-danger gc-mt-8">
    <strong>The honest statement</strong>
    AWARE today <em>authorises</em> and <em>records</em>. It does not verify that an authorised action was carried out as intended, because nothing in the current design observes the target after the fact. A Commit Guard that makes consequential changes atomic, target-side enforcement that makes the target verify AWARE&rsquo;s authorisation, and independent execution verification that produces a receipt &mdash; all three are specified in the roadmap architecture and <strong>none of them is implemented today</strong>.
  </div>
  <h2 class="gc-mt-12">Why we publish this page</h2>
  <p>A buyer who believes AWARE already verifies execution, and discovers otherwise during an audit, loses the account and the credibility. This page exists so that nobody has to discover it later.</p>
</div></section>
""",
    ),
    # -------------------------------------------------------- ARCHITECTURE
    _p(
        "architecture",
        "Architecture",
        "AWARE's actual components and data flows, derived from the shipped source: gateway, coordinator, policy engine, identity, revocation and the audit chain.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Architecture</span><h1>How AWARE is put together</h1>
  <p class="gc-hero-sub">This diagram is drawn from the shipped source, not from an aspiration. Where a component exists but is not wired into the running path, it is marked as such.</p>
</div></section>
<section class="gc-section"><div class="gc-container">
  <figure style="margin:0">
  <svg viewBox="0 0 900 470" role="img" aria-labelledby="arch-title arch-desc" style="width:100%;height:auto;background:var(--gc-surface);border:1px solid var(--gc-border);border-radius:var(--gc-radius-lg);padding:var(--gc-space-4)">
    <title id="arch-title">AWARE component architecture</title>
    <desc id="arch-desc">An agent issues a tool call to the gateway. The gateway proxies to the coordinator. The coordinator evaluates the call against the identity registry and the policy engine, which reads the policy store and tool catalogue. A decision is written to the audit chain, and revocation can invalidate an agent's credential. The kill switch can halt the gateway.</desc>
    <defs>
      <marker id="ar" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto">
        <path d="M0,0 L0,6 L9,3 z" fill="var(--gc-text-subtle)"/>
      </marker>
    </defs>
    <g font-family="ui-monospace,monospace" font-size="11" fill="var(--gc-text)">
      <rect x="18" y="40" width="120" height="46" rx="6" fill="var(--gc-surface-2)" stroke="var(--gc-border-strong)"/>
      <text x="78" y="62" text-anchor="middle">Agent</text><text x="78" y="76" text-anchor="middle" fill="var(--gc-text-subtle)" font-size="9">tool call</text>

      <rect x="178" y="40" width="150" height="46" rx="6" fill="var(--gc-accent-soft)" stroke="var(--gc-accent)"/>
      <text x="253" y="62" text-anchor="middle">Gateway</text><text x="253" y="76" text-anchor="middle" fill="var(--gc-text-subtle)" font-size="9">thin BFF &mdash; implemented</text>

      <rect x="368" y="40" width="150" height="46" rx="6" fill="var(--gc-accent-soft)" stroke="var(--gc-accent)"/>
      <text x="443" y="62" text-anchor="middle">Coordinator</text><text x="443" y="76" text-anchor="middle" fill="var(--gc-text-subtle)" font-size="9">decision routing</text>

      <rect x="558" y="14" width="150" height="46" rx="6" fill="var(--gc-surface-2)" stroke="var(--gc-border-strong)"/>
      <text x="633" y="36" text-anchor="middle">Identity registry</text><text x="633" y="50" text-anchor="middle" fill="var(--gc-text-subtle)" font-size="9">hash, rotate, revoke</text>

      <rect x="558" y="96" width="150" height="46" rx="6" fill="var(--gc-accent-soft)" stroke="var(--gc-accent)"/>
      <text x="633" y="118" text-anchor="middle">Policy engine</text><text x="633" y="132" text-anchor="middle" fill="var(--gc-text-subtle)" font-size="9">deny by default</text>

      <rect x="368" y="200" width="150" height="46" rx="6" fill="var(--gc-surface-2)" stroke="var(--gc-border-strong)"/>
      <text x="443" y="222" text-anchor="middle">Policy store</text><text x="443" y="236" text-anchor="middle" fill="var(--gc-text-subtle)" font-size="9">hot reload</text>

      <rect x="368" y="282" width="150" height="46" rx="6" fill="var(--gc-surface-2)" stroke="var(--gc-border-strong)"/>
      <text x="443" y="304" text-anchor="middle">Tool catalogue</text><text x="443" y="318" text-anchor="middle" fill="var(--gc-text-subtle)" font-size="9">risk &amp; data tier</text>

      <rect x="178" y="200" width="150" height="46" rx="6" fill="var(--gc-surface-2)" stroke="var(--gc-border-strong)"/>
      <text x="253" y="222" text-anchor="middle">Kill switch</text><text x="253" y="236" text-anchor="middle" fill="var(--gc-text-subtle)" font-size="9">gateway 503</text>

      <rect x="368" y="368" width="340" height="46" rx="6" fill="var(--gc-accent-soft)" stroke="var(--gc-accent)"/>
      <text x="538" y="390" text-anchor="middle">Audit chain &mdash; hash-linked, independently verifiable</text>
      <text x="538" y="404" text-anchor="middle" fill="var(--gc-text-subtle)" font-size="9">ALLOW / DENY / AUDIT recorded, failures included</text>

      <rect x="748" y="14" width="134" height="46" rx="6" fill="none" stroke="var(--gc-text-subtle)" stroke-dasharray="4 3"/>
      <text x="815" y="36" text-anchor="middle" fill="var(--gc-text-subtle)">Delegation graph</text>
      <text x="815" y="50" text-anchor="middle" fill="var(--gc-text-subtle)" font-size="9">roadmap</text>

      <rect x="748" y="96" width="134" height="46" rx="6" fill="none" stroke="var(--gc-text-subtle)" stroke-dasharray="4 3"/>
      <text x="815" y="118" text-anchor="middle" fill="var(--gc-text-subtle)">Commit Guard</text>
      <text x="815" y="132" text-anchor="middle" fill="var(--gc-text-subtle)" font-size="9">roadmap</text>

      <g stroke="var(--gc-text-subtle)" stroke-width="1.2" fill="none" marker-end="url(#ar)">
        <path d="M138 63 L172 63"/><path d="M328 63 L362 63"/>
        <path d="M518 55 L552 40"/><path d="M518 72 L552 115"/>
        <path d="M500 86 L480 194"/><path d="M420 246 L420 276"/>
        <path d="M500 86 L480 298"/>
        <path d="M328 63 L272 194"/>
        <path d="M443 328 L443 362"/>
        <path d="M710 38 L742 38" stroke-dasharray="4 3"/>
        <path d="M710 118 L742 118" stroke-dasharray="4 3"/>
      </g>
    </g>
  </svg>
  <figcaption class="gc-muted gc-mt-4" style="font-size:var(--gc-text-sm)">Solid outline and green fill mark components in the shipped runtime path. Dashed outline marks roadmap components that exist in the design but not in the code.</figcaption>
  </figure>

  <h2 class="gc-mt-12">The request path</h2>
  <ol class="gc-list">
    <li>The agent presents its credential and requests a tool call.</li>
    <li>The gateway validates the request, enforces the body-size limit, and proxies to the coordinator.</li>
    <li>The coordinator resolves the agent&rsquo;s identity and asks the policy engine to evaluate the call.</li>
    <li>The engine checks tool known-ness and risk, the data tier, and any matching policy.</li>
    <li>The decision &mdash; ALLOW, DENY, AUDIT or NO_POLICY, with a reason &mdash; is written to the audit chain.</li>
    <li>Revocation can invalidate the agent&rsquo;s credential at any point; the kill switch can halt the gateway entirely.</li>
  </ol>

  <div class="gc-callout gc-callout-warn gc-mt-8">
    <strong>Deployment shapes</strong>
    AWARE ships Dockerfiles for the service, gateway, coordinator and training components, two compose topologies, a Kubernetes manifest and an nginx configuration for the operator UI. The operator UI is a React application served behind nginx, proxying <code>/api</code> to the v2 gateway.
  </div>
</div></section>
""",
    ),
    # --------------------------------------------------------- DEVELOPERS
    _p(
        "developers",
        "Developers",
        "Install AWARE from npm, run it locally, and evaluate your first tool call against the real policy engine.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Developers</span><h1>Start in five minutes</h1>
  <p class="gc-hero-sub">Apache-2.0, published on npm, and the version on this site is the version you install. The quick start below is the one in the documentation.</p>
</div></section>
<section class="gc-section"><div class="gc-container gc-grid gc-grid-2">
  <div>
    <h2>Install</h2>
    <pre class="gc-code"><code>npm install @goodciso/aware

# or
pnpm add @goodciso/aware</code></pre>
    <h2 class="gc-mt-8">Run</h2>
    <pre class="gc-code"><code># The service entrypoint
npm start

# Confirm it is alive
curl -s localhost:3000/api/health</code></pre>
    <p class="gc-muted">The package requires a credential pepper. Without one the service refuses to start, which is the correct behaviour for a system that stores credentials.</p>
    <pre class="gc-code"><code>export AWARE_CREDENTIAL_PEPPER="<your-pepper>"
export SECRET_KEY="<your-secret>"</code></pre>
  </div>
  <div>
    <h2>Evaluate a tool call</h2>
    <p>Evaluate a request against the engine directly:</p>
    <pre class="gc-code"><code>const { getPolicyEngine } = require('@goodciso/aware/policies');

const engine = getPolicyEngine();

const decision = engine.evaluate({
  agentId: 'agent-001',
  tool: 'read_customer_record',
  context: { dataTier: 'CONFIDENTIAL' }
});

console.log(decision.decision);  // ALLOW | DENY | AUDIT | NO_POLICY
console.log(decision.reason);    // why</code></pre>
    <div class="gc-callout">
      <strong>Try it before you install it</strong>
      The <a href="https://demo.aware.goodciso.org">interactive playground</a> runs the real engine&rsquo;s decision vocabulary against seven scenarios, including a child agent exceeding its authority and a revoked agent attempting another operation. Every decision it renders is labelled as simulated.
    </div>
    <p class="gc-mt-6"><a class="gc-btn gc-btn-secondary" href="https://docs.aware.goodciso.org">Full documentation</a></p>
  </div>
</div></section>
""",
    ),
    # --------------------------------------------------------- USE CASES
    _p(
        "use-cases",
        "Use cases",
        "Where AWARE's implemented capabilities apply today: enterprise agent governance, multi-agent security, delegated authority and regulated environments.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Use cases</span><h1>Where this is useful</h1>
  <p class="gc-hero-sub">Each scenario below names the AWARE capability it relies on and states that capability&rsquo;s implementation state. Scenarios are constructed, not drawn from named customer deployments.</p>
</div></section>
<section class="gc-section"><div class="gc-container">
  <div class="gc-grid gc-grid-2">
    <div class="gc-card">
      <h3>Enterprise agent governance</h3>
      <p>An agent reads customer records on a support workflow. Without AWARE, that agent inherits the service account&rsquo;s reach. With AWARE, the agent has its own identity, the call is evaluated against a policy that binds the data tier to the tool, and the decision is written to a chain an auditor can recompute.</p>
      <p class="gc-muted gc-mb-0"><span class="gc-badge gc-badge-shipped">implemented</span> identity, policy engine, audit chain</p>
    </div>
    <div class="gc-card">
      <h3>Multi-agent security</h3>
      <p>A coordinator routes work to specialised agents. Each has its own credential and its own policies, so revoking one does not require redeploying the fleet.</p>
      <p class="gc-muted gc-mb-0"><span class="gc-badge gc-badge-shipped">implemented</span> per-agent identity, per-agent policy, revocation</p>
    </div>
    <div class="gc-card">
      <h3>Autonomous infrastructure operations</h3>
      <p>A remediation agent proposes and applies infrastructure changes. The policy engine can require approval for high-risk tools and rate-limit repeated calls, and every step lands in the audit chain.</p>
      <p class="gc-muted gc-mb-0"><span class="gc-badge gc-badge-shipped">implemented</span> approval requirement, rate limits, audit</p>
    </div>
    <div class="gc-card">
      <h3>Delegated AI authority</h3>
      <p>The end state is a parent delegating a bounded subset of its authority to a child, with revocation cascading down the chain. AWARE has the identity, policy and revocation primitives; the delegation graph that would carry the hierarchy is roadmap.</p>
      <p class="gc-muted gc-mb-0"><span class="gc-badge gc-badge-partial">partial</span> identity, policy, revocation <span class="gc-badge gc-badge-roadmap">roadmap</span> delegation graph, cascade</p>
    </div>
    <div class="gc-card">
      <h3>Regulated environments</h3>
      <p>Map controls to evidence. AWARE registers seven frameworks and 184 of 243 CSA AICM v1 controls, and can produce decision records for the auditor. It prepares the evidence; it does not grant certification.</p>
      <p class="gc-muted gc-mb-0"><span class="gc-badge gc-badge-shipped">implemented</span> framework mapping, disclosure records</p>
    </div>
    <div class="gc-card">
      <h3>Proving what happened</h3>
      <p>After an incident, export a window of the audit chain. A third party can recompute the hashes without access to your infrastructure.</p>
      <p class="gc-muted gc-mb-0"><span class="gc-badge gc-badge-shipped">implemented</span> exportable windows, independent verifier</p>
    </div>
  </div>
  <div class="gc-callout gc-callout-warn gc-mt-8">
    <strong>No named customers</strong>
    AWARE is used in production by organisations we have not named publicly, and this site does not imply otherwise. If you need a reference under NDA, contact us.
  </div>
</div></section>
""",
    ),
    # ------------------------------------------------------ TRUST CENTRE
    _p(
        "trust-centre",
        "Trust Centre",
        "AWARE's security architecture, trust boundaries, cryptographic mechanisms, audit design, testing methodology and disclosure policy. Only verified claims.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Trust Centre</span><h1>Trust Centre</h1>
  <p class="gc-hero-sub">What AWARE actually does, what it depends on, and where its limits are. Only claims with documentary evidence appear here.</p>
</div></section>
<section class="gc-section"><div class="gc-container">
  <h2>Trust boundaries</h2>
  <div class="gc-grid gc-grid-3">
    <div class="gc-card"><h3>Agent boundary</h3><p class="gc-muted">The agent is untrusted. It holds a credential and presents it. It is never trusted to authorise itself.</p></div>
    <div class="gc-card"><h3>Control plane</h3><p class="gc-muted">Gateway, coordinator, identity registry and policy engine are the trust boundary&rsquo;s inside. Decisions are made here, not by the agent.</p></div>
    <div class="gc-card"><h3>Target boundary</h3><p class="gc-muted">The system being acted on. Today AWARE does <em>not</em> verify what happens inside this boundary &mdash; see execution assurance.</p></div>
  </div>

  <h2 class="gc-mt-12">Cryptographic mechanisms</h2>
  <div class="gc-table-wrap"><table class="gc-table">
    <thead><tr><th>Mechanism</th><th>Algorithm</th><th>Purpose</th></tr></thead>
    <tbody>
      <tr><td>Credential storage</td><td>PBKDF2, per-credential salt, server-side pepper</td><td>Stored credentials are not recoverable</td></tr>
      <tr><td>Credential comparison</td><td>Constant-time</td><td>No timing oracle on verification</td></tr>
      <tr><td>Credential generation</td><td>32 bytes CSPRNG</td><td>Unguessable provisioning secrets</td></tr>
      <tr><td>Session token</td><td>JWT, HS256</td><td>Carries trust domain, blast radius, session id, execution context</td></tr>
      <tr><td>Audit chain</td><td>SHA-256 over canonical serialisation plus previous hash</td><td>Tamper-evident decision history</td></tr>
      <tr><td><strong>Key-bound identity</strong></td><td>&mdash;</td><td><strong>Not implemented.</strong> No X.509, Ed25519 or SPIFFE.</td></tr>
    </tbody>
  </table></div>

  <h2 class="gc-mt-12" id="compliance">Compliance mappings</h2>
  <p>Seven frameworks are registered in the framework mapper, with the versions below.</p>
  <div class="gc-table-wrap"><table class="gc-table">
    <thead><tr><th>Framework</th><th>Version</th><th>Coverage</th></tr></thead>
    <tbody>
      <tr><td>CSA AI Controls Matrix</td><td>v1</td><td>184 of 243 control IDs, across all 18 domains</td></tr>
      <tr><td>NIST AI Risk Management Framework</td><td>1.0</td><td>Govern, Map, Measure, Manage</td></tr>
      <tr><td>ISO/IEC 27001</td><td>2022</td><td>Annex A control mapping</td></tr>
      <tr><td>ISO/IEC 42001</td><td>v1.0-2026-07-28</td><td>AI management system controls</td></tr>
      <tr><td>OWASP Agentic Skills Top 10</td><td>v1.0-2026</td><td>Full catalogue</td></tr>
      <tr><td>OWASP Top 10 for MCP</td><td>2025</td><td>10 of 10 classes</td></tr>
      <tr><td>DORA</td><td>2022</td><td>Operational resilience mapping</td></tr>
      <tr><td>MITRE ATLAS</td><td>v2026.06</td><td>Technique mapping, 7 initial rule functions</td></tr>
    </tbody>
  </table></div>
  <div class="gc-callout gc-callout-warn">
    <strong>A mapping is not a certification</strong>
    Registering a control against a framework supports preparation. It is not an audit opinion, not a certificate, and not a guarantee that a given requirement is met. The independent certification body decides. AWARE never guarantees an auditor&rsquo;s decision.
  </div>

  <h2 class="gc-mt-12">Security testing methodology</h2>
  <ul class="gc-list">
    <li>Unit and integration suites run on the standard Node test runner, with separate standards suites per compliance framework.</li>
    <li>Playwright covers browser-level behaviour of the operator UI.</li>
    <li>Dependency and secret scanning run as part of the release process: gitleaks, npm audit and trivy reports are kept in the repository.</li>
    <li>The npm publication boundary is enforced by a publish guard that packs from a clean detached worktree at the release tag and refuses to publish a tarball that differs from it.</li>
  </ul>

  <h2 class="gc-mt-12">Vulnerability disclosure</h2>
  <p>AWARE publishes a security policy and a <code>SECURITY.md</code> with a coordinated disclosure route. Report a vulnerability rather than disclosing it publicly. Contact: <a href="mailto:security@goodciso.org">security@goodciso.org</a>. A <code>security.txt</code> is served under <code>/.well-known/</code>.</p>

  <h2 class="gc-mt-12">Data handling</h2>
  <p>AWARE stores agent identity records, policy state and audit records. Credentials are stored as salted, peppered hashes and are never recoverable. Audit records can be exported and are intended to be retained by the operator; the retention period is the operator&rsquo;s choice and is not imposed by the product.</p>

  <div class="gc-callout gc-callout-danger gc-mt-8">
    <strong>Claims we do not make</strong>
    AWARE is not SOC 2 certified. It is not ISO certified. It has not been penetration tested by an independent firm. We do not claim enterprise customer deployments we cannot evidence. The product&rsquo;s maturity is described by the capability register, and that register is public.
  </div>
</div></section>
""",
    ),
    # -------------------------------------------------------- ENTERPRISE
    _p(
        "enterprise",
        "Enterprise",
        "Deploy AWARE yourself, or work with GoodCISO on the surrounding security architecture. Open source core, no licence lock-in.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Enterprise</span><h1>Run it yourself, or bring us in</h1>
  <p class="gc-hero-sub">The AWARE core is Apache-2.0. If you want to operate it inside your own perimeter, nothing stops you. If you want help designing the security architecture around it, that is GoodCISO&rsquo;s advisory practice.</p>
</div></section>
<section class="gc-section"><div class="gc-container gc-grid gc-grid-2">
  <div>
    <h2>Self-hosted</h2>
    <ul class="gc-list">
      <li>Docker images for the service, gateway, coordinator and training components.</li>
      <li>Two compose topologies &mdash; a full stack and a coordinator-focused one.</li>
      <li>A Kubernetes manifest for production deployment.</li>
      <li>An nginx configuration for the operator UI.</li>
      <li>Your data, your database, your perimeter. Nothing phones home.</li>
    </ul>
    <p><a class="gc-btn gc-btn-secondary" href="https://docs.aware.goodciso.org/deployment">Deployment documentation</a></p>
  </div>
  <div>
    <h2>GoodCISO advisory</h2>
    <p>GoodCISO is a cybersecurity and AI governance company. We work on the architecture around the control plane:</p>
    <ul class="gc-list">
      <li>Agent identity strategy across your estate.</li>
      <li>Policy design &mdash; what should be allowed, by whom, under what conditions.</li>
      <li>Trust boundaries and data-flow design for agentic systems.</li>
      <li>Evidence pipelines that survive an audit.</li>
    </ul>
    <p><a class="gc-btn gc-btn-primary" href="https://goodciso.org/contact">Talk to GoodCISO</a></p>
  </div>
</div></section>
<section class="gc-section-tight" style="background:var(--gc-surface)"><div class="gc-container">
  <div class="gc-callout gc-callout-warn gc-mb-0">
    <strong>No hosted offering yet</strong>
    There is no managed AWARE cloud product. The npm package is the product. Anything described as a hosted tier on this site would be roadmap, and we would label it as such.
  </div>
</div></section>
""",
    ),
    _p(
        "get-started",
        "Get started",
        "Three routes into AWARE: install the package, read the documentation, or explore the interactive playground.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Get started</span><h1>Pick your entry point</h1>
</div></section>
<section class="gc-section"><div class="gc-container gc-grid gc-grid-3">
  <div class="gc-card">
    <h3>Install the package</h3>
    <p class="gc-muted">The fastest route to a running instance. Apache-2.0, self-hosted, no telemetry.</p>
    <pre class="gc-code"><code>npm install @goodciso/aware
npm start</code></pre>
    <a class="gc-btn gc-btn-primary" href="https://docs.aware.goodciso.org/quick-start">Quick start</a>
  </div>
  <div class="gc-card">
    <h3>Read the architecture</h3>
    <p class="gc-muted">How the pieces fit, and what each one does and does not guarantee.</p>
    <ul class="gc-list">
      <li><a href="/architecture">Architecture</a></li>
      <li><a href="/platform/execution-assurance">Execution assurance</a></li>
      <li><a href="/trust-centre">Trust Centre</a></li>
    </ul>
    <a class="gc-btn gc-btn-secondary" href="https://docs.aware.goodciso.org">Documentation</a>
  </div>
  <div class="gc-card">
    <h3>Try the playground</h3>
    <p class="gc-muted">Seven scenarios running the real decision vocabulary. Every decision is labelled as simulated.</p>
    <ul class="gc-list">
      <li>PII access request</li>
      <li>Child agent exceeding its authority</li>
      <li>Revoked agent attempting another operation</li>
      <li>Expired approval</li>
    </ul>
    <a class="gc-btn gc-btn-secondary" href="https://demo.aware.goodciso.org">Open the playground</a>
  </div>
</div></section>
""",
    ),
]
