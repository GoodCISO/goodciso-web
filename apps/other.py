#!/usr/bin/env python3
"""GoodCISO corporate site, AWARE docs site, and the interactive playground."""
from build import Nav, Page

# ==========================================================================
# CORPORATE — goodciso.org
# ==========================================================================
C_DOMAIN = "https://goodciso.org"

C_NAV = [
    Nav("Home", "/"),
    Nav("Services", "/services"),
    Nav("AWARE", "/aware"),
    Nav("Insights", "/insights"),
    Nav("About", "/about"),
    Nav("Pricing", "/pricing"),
    Nav("Contact", "/contact"),
]

C_FOOTER = [
    ("Services", [
        Nav("AI Security & Governance", "/services/ai-security"),
        Nav("CISO Advisory", "/services/ciso-advisory"),
        Nav("Security Architecture", "/services/security-architecture"),
        Nav("Regulatory Readiness", "/services/regulatory-readiness"),
    ]),
    ("Product", [
        Nav("AWARE", "/aware"),
        Nav("AWARE platform", "https://aware.goodciso.org", external=True),
        Nav("Documentation", "https://docs.aware.goodciso.org", external=True),
        Nav("Playground", "https://demo.aware.goodciso.org", external=True),
    ]),
    ("Company", [
        Nav("About", "/about"),
        Nav("Insights", "/insights"),
        Nav("Pricing", "/pricing"),
        Nav("Contact", "/contact"),
        Nav("Privacy", "/privacy"),
        Nav("Terms", "/terms"),
    ]),
]

C_TAGLINE = "Enterprise cybersecurity and AI governance."


def _c(slug, title, desc, body, status=""):
    return Page(
        slug=slug, title=title, description=desc, body=body,
        canonical=f"{C_DOMAIN}/{slug}" if slug != "index" else f"{C_DOMAIN}/",
        status=status,
    )


CORPORATE = [
    _c(
        "index",
        "Securing the enterprise in the age of autonomous AI",
        "GoodCISO combines cybersecurity leadership, security engineering and AI governance to help organisations navigate increasingly autonomous digital environments.",
        """
<section class="gc-hero">
  <div class="gc-container">
    <span class="gc-eyebrow">GoodCISO</span>
    <h1>Securing the enterprise in the age of autonomous AI.</h1>
    <p class="gc-hero-sub">We combine cybersecurity leadership, security engineering and AI governance so organisations can act on their own information without losing control of it.</p>
    <div class="gc-hero-actions">
      <a class="gc-btn gc-btn-primary gc-btn-lg" href="/services">Explore our services</a>
      <a class="gc-btn gc-btn-secondary gc-btn-lg" href="/aware">Meet AWARE</a>
    </div>
  </div>
</section>

<section class="gc-section">
  <div class="gc-container">
    <div class="gc-grid gc-grid-2">
      <div>
        <span class="gc-eyebrow">The challenge</span>
        <h2>Autonomy changes the threat model</h2>
        <p>Security programmes are built around human actors making deliberate mistakes. Autonomous agents are different: they act at machine speed, hold service credentials, and multiply. One compromised agent can reach every system that credential touches, in seconds, without anyone deciding to do it.</p>
        <p>Traditional controls answer the question <em>who logged in</em>. Agentic systems need controls that answer <em>who is acting, under what authority, and can that authority be withdrawn</em>.</p>
        <p>That is the problem GoodCISO works on, and the reason we built AWARE rather than writing another policy document.</p>
      </div>
      <div>
        <span class="gc-eyebrow">What we do</span>
        <h2>Three disciplines, one practice</h2>
        <ul class="gc-list">
          <li><strong>Cybersecurity leadership</strong> &mdash; strategy, operating models, risk, and board-level governance of security.</li>
          <li><strong>Security engineering</strong> &mdash; architecture, identity, infrastructure and the technical controls that hold under pressure.</li>
          <li><strong>AI governance</strong> &mdash; making autonomous agents accountable, bounded and auditable.</li>
        </ul>
        <p>Most engagements start in one and end up needing all three. We would rather tell you that on day one.</p>
      </div>
    </div>
  </div>
</section>

<section class="gc-section-tight" style="background:var(--gc-surface)">
  <div class="gc-container">
    <div class="gc-grid gc-grid-2" style="align-items:center">
      <div>
        <span class="gc-eyebrow">Flagship product</span>
        <h2>AWARE</h2>
        <p class="gc-measure">AWARE is an open-source security control plane for autonomous AI agents. It gives every agent a non-human identity, evaluates every tool call against policy before it runs, and records each decision in a hash chain a third party can independently recompute.</p>
        <p class="gc-measure">It is the product we wanted when we were advising clients on agent governance, and we would rather publish its limits than let you discover them.</p>
        <div class="gc-flex gc-mt-6">
          <a class="gc-btn gc-btn-primary" href="/aware">About AWARE</a>
          <a class="gc-btn gc-btn-secondary" href="https://aware.goodciso.org">Visit the product site</a>
        </div>
      </div>
      <div class="gc-card">
        <h3>What is implemented today</h3>
        <ul class="gc-checklist">
          <li>Agent identity with hashed, rotatable, revocable credentials</li>
          <li>Deny-by-default policy engine with ALLOW / DENY / AUDIT decisions</li>
          <li>Revocation that invalidates a credential immediately</li>
          <li>Hash-chained audit trail with an independent verifier</li>
          <li>Seven compliance framework mappings, 184 AICM v1 controls</li>
        </ul>
        <p class="gc-muted gc-mt-4 gc-mb-0" style="font-size:var(--gc-text-sm)">Execution assurance &mdash; atomic commit and independent verification &mdash; is roadmap, and is labelled as such on the product site.</p>
      </div>
    </div>
  </div>
</section>

<section class="gc-section">
  <div class="gc-container">
    <span class="gc-eyebrow">Services</span>
    <h2>Where we help</h2>
    <div class="gc-grid gc-grid-2">
      <div class="gc-card"><h3><a href="/services/ai-security">AI Security &amp; Governance</a></h3><p class="gc-muted">Agentic risk, autonomous system governance, identity, delegated authority, risk management and the operational controls that make autonomy defensible.</p></div>
      <div class="gc-card"><h3><a href="/services/ciso-advisory">CISO Advisory</a></h3><p class="gc-muted">Security leadership and strategy: operating models, risk management, and governance a board can actually use.</p></div>
      <div class="gc-card"><h3><a href="/services/security-architecture">Security Architecture</a></h3><p class="gc-muted">Zero trust, cloud security, identity, infrastructure and the technical assurance that shows the design holds.</p></div>
      <div class="gc-card"><h3><a href="/services/regulatory-readiness">Regulatory Readiness</a></h3><p class="gc-muted">Preparing for ISO 27001, SOC 2, NIST AI RMF and ISO 42001. Assistance with preparation, never a guarantee of an independent body&rsquo;s decision.</p></div>
    </div>
  </div>
</section>

<section class="gc-section-tight" style="background:var(--gc-surface)">
  <div class="gc-container gc-center">
    <span class="gc-eyebrow">Get in touch</span>
    <h2>Start a conversation</h2>
    <p class="gc-muted gc-measure" style="margin-inline:auto">Tell us what you are trying to secure and we will tell you, plainly, whether we are the right people for it.</p>
    <div class="gc-flex gc-mt-6" style="justify-content:center">
      <a class="gc-btn gc-btn-primary gc-btn-lg" href="/contact">Contact us</a>
      <a class="gc-btn gc-btn-secondary gc-btn-lg" href="/services">Our services</a>
    </div>
  </div>
</section>
""",
    ),
    _c(
        "services",
        "Services",
        "GoodCISO provides AI security and governance, CISO advisory, enterprise security architecture, and regulatory readiness services.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Services</span><h1>Four practices, one standard</h1>
  <p class="gc-hero-sub">We do not sell tool deployment. We design the control environment that a tool, a team or an auditor can rely on.</p>
</div></section>
<section class="gc-section"><div class="gc-container"><div class="gc-grid gc-grid-2">
  <div class="gc-card"><h2><a href="/services/ai-security">AI Security &amp; Governance</a></h2><p class="gc-muted">Agentic AI risk, autonomous system governance, identity, delegated authority, risk management and operational controls.</p><a href="/services/ai-security">Read more &rarr;</a></div>
  <div class="gc-card"><h2><a href="/services/ciso-advisory">CISO Advisory</a></h2><p class="gc-muted">Security leadership, strategy, operating models, risk management and board-level security governance.</p><a href="/services/ciso-advisory">Read more &rarr;</a></div>
  <div class="gc-card"><h2><a href="/services/security-architecture">Security Architecture</a></h2><p class="gc-muted">Enterprise security architecture, zero trust, cloud security, identity, infrastructure and technical assurance.</p><a href="/services/security-architecture">Read more &rarr;</a></div>
  <div class="gc-card"><h2><a href="/services/regulatory-readiness">Regulatory Readiness</a></h2><p class="gc-muted">Evidence and control readiness for ISO 27001, SOC 2, NIST AI RMF and ISO 42001.</p><a href="/services/regulatory-readiness">Read more &rarr;</a></div>
</div></div></section>
""",
    ),
    _c(
        "services/ai-security",
        "AI Security and Governance",
        "Agentic AI risk assessment, autonomous system governance, agent identity, delegated authority, and the operational controls that make autonomous agents accountable.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Services</span><h1>AI security &amp; governance</h1>
  <p class="gc-hero-sub">An autonomous agent is a privileged actor with a machine-speed decision loop. Most of the controls that protect an organisation assume the actor is a person who can be asked why.</p>
</div></section>
<section class="gc-section"><div class="gc-container gc-grid gc-grid-2">
  <div>
    <h2>What we address</h2>
    <h3>Identity for non-human actors</h3>
    <p>Agents that inherit a human or service identity cannot be scoped, attributed or revoked independently. We design identity models that give each agent its own authority boundary.</p>
    <h3>Delegated authority</h3>
    <p>Where agents spawn agents, authority must narrow, never widen. We specify the inheritance rules, the revocation semantics and the evidence that proves them.</p>
    <h3>Risk and blast radius</h3>
    <p>Which tools, which data tiers, which blast radius an agent is permitted to carry &mdash; and how you find out when an agent exceeds it.</p>
    <h3>Operational controls</h3>
    <p>Approval gates, rate limits, kill switches, and the runbooks that get used at 03:00 during an incident rather than in a design document.</p>
  </div>
  <div>
    <div class="gc-callout">
      <strong>Practically, this means</strong>
      You get a control model that maps to what you already run, an architecture for agent governance, and evidence you can hand to an auditor. Where open-source tooling fits the problem, we point you at it &mdash; including our own.
    </div>
    <h3 class="gc-mt-8">Related</h3>
    <ul class="gc-list">
      <li><a href="/aware">AWARE, the control plane we built for this</a></li>
      <li><a href="/services/security-architecture">Security Architecture</a></li>
      <li><a href="/services/regulatory-readiness">Regulatory Readiness</a></li>
    </ul>
  </div>
</div></section>
""",
    ),
    _c(
        "services/ciso-advisory",
        "CISO Advisory",
        "Security leadership and strategy: operating models, risk management, board-level security governance and the reporting that makes it usable.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Services</span><h1>CISO advisory</h1>
  <p class="gc-hero-sub">A security function that cannot explain its risk to a board in plain language will not get the budget or the mandate it needs.</p>
</div></section>
<section class="gc-section"><div class="gc-container gc-grid gc-grid-2">
  <div>
    <h2>What we do</h2>
    <ul class="gc-list">
      <li><strong>Security strategy and operating model</strong> &mdash; what the function owns, what it buys, what it declines.</li>
      <li><strong>Risk management</strong> &mdash; a register that reflects how the business actually operates, and a method for prioritising under constraint.</li>
      <li><strong>Board-level governance</strong> &mdash; reporting that gives a non-technical director enough to make a decision.</li>
      <li><strong>Capability building</strong> &mdash; the team, the tooling and the runbooks needed to sustain the position.</li>
    </ul>
  </div>
  <div>
    <div class="gc-callout">
      <strong>How we work</strong>
      We start with the decisions you need to be able to defend, not a catalogue of controls. That means less documentation and more of the evidence that a decision was reasonable.
    </div>
    <h3 class="gc-mt-8">Related</h3>
    <ul class="gc-list">
      <li><a href="/services/regulatory-readiness">Regulatory Readiness</a></li>
      <li><a href="/services/security-architecture">Security Architecture</a></li>
    </ul>
  </div>
</div></section>
""",
    ),
    _c(
        "services/security-architecture",
        "Security Architecture",
        "Enterprise security architecture: zero trust, cloud security, identity, infrastructure hardening and technical assurance that demonstrates the design holds.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Services</span><h1>Security architecture</h1>
  <p class="gc-hero-sub">Architecture is only worth what it survives. We design for the threat you actually have, then test the design against it.</p>
</div></section>
<section class="gc-section"><div class="gc-container gc-grid gc-grid-2">
  <div>
    <h2>What we do</h2>
    <ul class="gc-list">
      <li><strong>Zero-trust architecture</strong> &mdash; identity-first design, segmentation and the verification points that make a claim meaningful.</li>
      <li><strong>Cloud and infrastructure security</strong> &mdash; account structure, network boundaries, workload identity and the configuration that actually holds.</li>
      <li><strong>Identity architecture</strong> &mdash; human and machine identity on one coherent model, including the agents we increasingly have to govern.</li>
      <li><strong>Technical assurance</strong> &mdash; reviewing a design against its own failure modes, and reporting what would break it.</li>
    </ul>
  </div>
  <div>
    <div class="gc-callout">
      <strong>Deliverables</strong>
      A target architecture with the decisions and their rationale, an implementation plan sequenced by risk reduction rather than convenience, and an assurance view that says plainly where the design is untested.
    </div>
    <h3 class="gc-mt-8">Related</h3>
    <ul class="gc-list">
      <li><a href="/services/ai-security">AI Security &amp; Governance</a></li>
      <li><a href="/services/ciso-advisory">CISO Advisory</a></li>
    </ul>
  </div>
</div></section>
""",
    ),
    _c(
        "services/regulatory-readiness",
        "Regulatory readiness",
        "Evidence and control readiness for ISO 27001, SOC 2, NIST AI RMF and ISO 42001. Preparation support, never a guarantee of an independent certification body's decision.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Services</span><h1>Regulatory readiness</h1>
  <p class="gc-hero-sub">We help you get ready for an audit. We do not perform the audit, and no software can decide the outcome for you.</p>
</div></section>
<section class="gc-section"><div class="gc-container gc-grid gc-grid-2">
  <div>
    <h2>Frameworks we work against</h2>
    <div class="gc-table-wrap"><table class="gc-table">
      <thead><tr><th>Framework</th><th>What we help with</th></tr></thead>
      <tbody>
        <tr><td>ISO/IEC 27001</td><td>Annex A control readiness, evidence collection, Statement of Applicability work</td></tr>
        <tr><td>SOC 2</td><td>Trust Services Criteria mapping, control design, evidence pipeline for the observation period</td></tr>
        <tr><td>NIST AI RMF</td><td>Govern, Map, Measure, Manage applied to your agent estate</td></tr>
        <tr><td>ISO/IEC 42001</td><td>AI management system readiness for organisations deploying AI systems</td></tr>
        <tr><td>DORA</td><td>ICT risk and operational resilience where in scope</td></tr>
      </tbody>
    </table></div>
  </div>
  <div>
    <div class="gc-callout gc-callout-warn">
      <strong>An honest distinction</strong>
      We assist with <em>preparation</em>. We are not a certification body, we do not issue certificates, and we cannot guarantee an independent auditor&rsquo;s decision. Anyone who promises you a certification outcome is promising something they do not control.
    </div>
    <h3 class="gc-mt-8">Related</h3>
    <ul class="gc-list">
      <li><a href="/services/ciso-advisory">CISO Advisory</a></li>
      <li><a href="/aware">AWARE &mdash; automated evidence for AI agent controls</a></li>
    </ul>
  </div>
</div></section>
""",
    ),
    _c(
        "aware",
        "AWARE",
        "AWARE is GoodCISO's open-source security control plane for autonomous AI agents: identity, policy enforcement, revocation and verifiable audit evidence.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Product</span><h1>AWARE</h1>
  <p class="gc-hero-sub">The security control plane for autonomous AI agents. Establish agent identity, enforce policy on every tool call, revoke authority when it must end, and keep evidence a third party can check.</p>
  <div class="gc-hero-actions">
    <a class="gc-btn gc-btn-primary gc-btn-lg" href="https://aware.goodciso.org">Visit the AWARE site</a>
    <a class="gc-btn gc-btn-secondary gc-btn-lg" href="https://github.com/GoodCISO/aware">Source on GitHub</a>
  </div>
</div></section>
<section class="gc-section"><div class="gc-container">
  <h2>Five capabilities</h2>
  <div class="gc-grid gc-grid-3">
    <div class="gc-card"><h3>Identity</h3><p class="gc-muted">A non-human identity per agent, with a credential stored only as a salted, peppered hash and compared in constant time.</p></div>
    <div class="gc-card"><h3>Governance</h3><p class="gc-muted">Policy enforcement on every tool call, deny by default, evaluated against tool risk and data classification tier.</p></div>
    <div class="gc-card"><h3>Delegation</h3><p class="gc-muted">The intended model bounds a child&rsquo;s authority by its parent&rsquo;s. The delegation graph that would carry this is roadmap.</p></div>
    <div class="gc-card"><h3>Revocation</h3><p class="gc-muted">Revoking an agent invalidates its credential immediately and records the decision. Cascade to derived agents is roadmap.</p></div>
    <div class="gc-card"><h3>Assurance</h3><p class="gc-muted">Auditability and evidence are implemented. Independent <em>execution</em> verification is roadmap, and labelled so.</p></div>
    <div class="gc-card"><h3>Compliance</h3><p class="gc-muted">Seven frameworks mapped, 184 of 243 CSA AICM v1 controls, MITRE ATLAS technique mapping. A mapping is not a certification.</p></div>
  </div>
  <div class="gc-callout gc-callout-warn gc-mt-8">
    <strong>We publish our own limits</strong>
    AWARE&rsquo;s product site labels every capability with its implementation state, and publishes a capability register that governs the marketing copy. If a capability is not shipped, the site says so. That register is the reason you can trust the rest of the claims.
  </div>
</div></section>
""",
    ),
    _c(
        "insights",
        "Insights",
        "Technical analysis on cybersecurity, AI agent governance and the controls that make autonomous systems accountable.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Insights</span><h1>Thinking, written down</h1>
  <p class="gc-hero-sub">Analysis of the problems we work on. Published when they are useful, not on a schedule.</p>
</div></section>
<section class="gc-section"><div class="gc-container">
  <h2 class="gc-mt-8">From the team</h2>
  <div class="gc-grid gc-grid-2">
    <div class="gc-card"><span class="gc-mono-label" style="font-family:var(--gc-font-mono);font-size:var(--gc-text-xs);color:var(--gc-text-subtle)">AGENT SECURITY</span><h3 class="gc-mt-4">Why LLM Threat Models Fail (And How to Fix Them)</h3><p class="gc-muted">STRIDE assumes a fixed attack surface. An LLM&rsquo;s surface is its prompt space &mdash; an effectively infinite set of inputs. A practical reframing.</p><a href="/insights/why-llm-threat-models-fail">Read &rarr;</a></div>
    <div class="gc-card"><span class="gc-mono-label" style="font-family:var(--gc-font-mono);font-size:var(--gc-text-xs);color:var(--gc-text-subtle)">AGENT SECURITY</span><h3 class="gc-mt-4">What We Learned Building Agentic Security Workflows</h3><p class="gc-muted">What building AWARE taught us about governing autonomous agents, and why traditional compliance tooling could not be adapted to the problem.</p><a href="/insights/what-we-learned-building-agentic-security-workflows">Read &rarr;</a></div>
    <div class="gc-card"><span class="gc-mono-label" style="font-family:var(--gc-font-mono);font-size:var(--gc-text-xs);color:var(--gc-text-subtle)">CONTAINER SECURITY</span><h3 class="gc-mt-4">The Container Security Gap Nobody Talks About</h3><p class="gc-muted">Image scanning and admission control solve the wrong half of the problem. What actually causes catastrophic breaches.</p><a href="/insights/container-security-gap">Read &rarr;</a></div>
    <div class="gc-card"><span class="gc-mono-label" style="font-family:var(--gc-font-mono);font-size:var(--gc-text-xs);color:var(--gc-text-subtle)">DEVSECOPS</span><h3 class="gc-mt-4">DevSecOps is Dead; Long Live DevOps</h3><p class="gc-muted">Why DevSecOps was never a separate discipline, and what the next shift looks like for teams shipping at speed.</p><a href="/insights/devsecops-is-dead">Read &rarr;</a></div>
  </div>
  <h2 class="gc-mt-12">From the AWARE product team</h2>
  <div class="gc-grid gc-grid-3">
    <div class="gc-card"><span class="gc-mono-label" style="font-family:var(--gc-font-mono);font-size:var(--gc-text-xs);color:var(--gc-text-subtle)">AGENT GOVERNANCE</span><h3 class="gc-mt-4">Authorising an action is not verifying it</h3><p class="gc-muted">Five verbs &mdash; authorise, approve, revalidate, commit, verify &mdash; get collapsed into one word in agent-security marketing. Only the first is common today.</p><a href="https://aware.goodciso.org/platform/execution-assurance">Read &rarr;</a></div>
    <div class="gc-card"><span class="gc-mono-label" style="font-family:var(--gc-font-mono);font-size:var(--gc-text-xs);color:var(--gc-text-subtle)">IDENTITY</span><h3 class="gc-mt-4">Why a bearer secret is not an agent identity</h3><p class="gc-muted">Shared-secret authentication authenticates a holder, not a key. What that changes, and what closes the replay gap in the meantime.</p><a href="https://aware.goodciso.org/platform/agent-identity">Read &rarr;</a></div>
    <div class="gc-card"><span class="gc-mono-label" style="font-family:var(--gc-font-mono);font-size:var(--gc-text-xs);color:var(--gc-text-subtle)">EVIDENCE</span><h3 class="gc-mt-4">A log is not evidence</h3><p class="gc-muted">What makes an audit record independently checkable, and how a hash chain with an exportable window gets you there.</p><a href="https://aware.goodciso.org/platform/audit">Read &rarr;</a></div>
  </div>
  <div class="gc-callout gc-mt-8">
    <strong>More published articles are in progress</strong> This section is structured so that new analysis can be added without a redesign. If you want something specific covered, <a href="/contact">tell us</a>.
  </div>
</div></section>
""",
    ),
    _c(
        "about",
        "About",
        "GoodCISO is an enterprise cybersecurity and AI governance company. AWARE is its flagship open-source technology product.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">About</span><h1>GoodCISO</h1>
  <p class="gc-hero-sub">An enterprise cybersecurity and AI governance company that builds its own security infrastructure rather than only advising on other people&rsquo;s.</p>
</div></section>
<section class="gc-section"><div class="gc-container gc-grid gc-grid-2">
  <div>
    <h2>What we are</h2>
    <p>GoodCISO Limited is a security company. We provide advisory and architecture services to organisations dealing with the practical consequences of autonomous AI, and we develop the technology we believe the problem requires.</p>
    <p>AWARE is that technology. It began as the control environment we found ourselves specifying for clients and could not buy, and it is released under Apache-2.0 because the problem is general and a closed tool would only slow it down.</p>
    <h3>Our position</h3>
    <p>We think product truth outranks marketing hype, always. It is why AWARE&rsquo;s site publishes implementation state on every capability, and why this site carries no customer logos we cannot evidence.</p>
  </div>
  <div>
    <h2>Legal</h2>
    <div class="gc-table-wrap"><table class="gc-table">
      <tbody>
        <tr><th scope="row">Legal entity</th><td>Good CISO Limited</td></tr>
        <tr><th scope="row">Company number</th><td>16294946 (England &amp; Wales)</td></tr>
        <tr><th scope="row">AWARE licence</th><td>Apache-2.0, source at github.com/GoodCISO/aware</td></tr>
        <tr><th scope="row">Contact</th><td><a href="mailto:hello@goodciso.org">hello@goodciso.org</a></td></tr>
        <tr><th scope="row">Security</th><td><a href="mailto:security@goodciso.org">security@goodciso.org</a></td></tr>
      </tbody>
    </table></div>
    <div class="gc-callout gc-callout-warn gc-mt-6">
      <strong>No fabricated credentials</strong>
      We do not list certifications, partnerships, customer counts or team biographies we cannot evidence. If that makes this page look thinner than others, it is the intended effect.
    </div>
  </div>
</div></section>
""",
    ),
    _c(
        "pricing",
        "Pricing",
        "AWARE platform tiers and retained security leadership. Priced on outcomes: what is produced, what changes, and what is externally verifiable.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Pricing</span>
  <h1>Priced on outcomes, not on hours</h1>
  <p class="gc-hero-sub">Two things are sold here. AWARE is a software platform, on a subscription, and the tiers below are its licence tiers. Retained leadership is senior security cover for a business that needs a person accountable. Each is priced on what it produces.</p>
</div></section>

<section class="gc-section"><div class="gc-container">
  <span class="gc-eyebrow">AWARE platform</span>
  <h2>The platform, on a subscription</h2>
  <p class="gc-muted gc-measure">AWARE is open source. You can run it yourself today at no cost, and the tiers below are what we charge to run it for you and prove what it did. Paying for the platform buys operations and evidence, not access to the engine.</p>
  <div class="gc-grid gc-grid-4 gc-mt-8">
    <div class="gc-card">
      <h3>Open Source</h3>
      <p style="font-size:var(--gc-text-3xl);font-weight:700;color:var(--gc-text);margin:var(--gc-space-3) 0 var(--gc-space-1)">Free</p>
      <p class="gc-muted" style="font-size:var(--gc-text-sm);margin-bottom:var(--gc-space-4)">Apache-2.0, self-hosted</p>
      <ul class="gc-list gc-muted" style="font-size:var(--gc-text-sm)">
        <li>The engine itself, with no feature gates</li>
        <li>Community support</li>
        <li>Source on GitHub</li>
      </ul>
      <a class="gc-btn gc-btn-secondary gc-btn-block" href="https://github.com/GoodCISO/aware" target="_blank" rel="noopener noreferrer">Get the source</a>
    </div>
    <div class="gc-card">
      <h3>Scan</h3>
      <p style="font-size:var(--gc-text-3xl);font-weight:700;color:var(--gc-text);margin:var(--gc-space-3) 0 var(--gc-space-1)">£2,000<span style="font-size:var(--gc-text-sm);font-weight:400;color:var(--gc-text-muted)">/mo</span></p>
      <p class="gc-muted" style="font-size:var(--gc-text-sm);margin-bottom:var(--gc-space-4)">or £20,000/year</p>
      <ul class="gc-list gc-muted" style="font-size:var(--gc-text-sm)">
        <li>FCA compliance scanning (COBS, SYSC, PRIN, DISP)</li>
        <li>1,000 entries per month scanned</li>
        <li>Scheduled scan runs and alerts</li>
        <li>Email support</li>
      </ul>
      <a class="gc-btn gc-btn-secondary gc-btn-block" href="/contact">Start a conversation</a>
    </div>
    <div class="gc-card">
      <h3>Pro</h3>
      <p style="font-size:var(--gc-text-3xl);font-weight:700;color:var(--gc-text);margin:var(--gc-space-3) 0 var(--gc-space-1)">£5,000<span style="font-size:var(--gc-text-sm);font-weight:400;color:var(--gc-text-muted)">/mo</span></p>
      <p class="gc-muted" style="font-size:var(--gc-text-sm);margin-bottom:var(--gc-space-4)">or £50,000/year</p>
      <ul class="gc-list gc-muted" style="font-size:var(--gc-text-sm)">
        <li>The same engine, run for you</li>
        <li>Continuous monitoring and alerting</li>
        <li>Evidence packs an auditor can read</li>
        <li>Priority support, 4-hour SLA</li>
      </ul>
      <a class="gc-btn gc-btn-secondary gc-btn-block" href="/contact">Start a conversation</a>
    </div>
    <div class="gc-card">
      <h3>Enterprise</h3>
      <p style="font-size:var(--gc-text-3xl);font-weight:700;color:var(--gc-text);margin:var(--gc-space-3) 0 var(--gc-space-1)">Custom</p>
      <p class="gc-muted" style="font-size:var(--gc-text-sm);margin-bottom:var(--gc-space-4)">scoped to the estate</p>
      <ul class="gc-list gc-muted" style="font-size:var(--gc-text-sm)">
        <li>Everything in Pro</li>
        <li>Deployment and integration</li>
        <li>Custom policy and control packs</li>
        <li>1-hour emergency response SLA</li>
      </ul>
      <a class="gc-btn gc-btn-secondary gc-btn-block" href="/contact">Talk to us</a>
    </div>
  </div>
  <div class="gc-callout gc-mt-8">
    <strong>What the platform tiers do not include</strong>
    Sign receipts an auditor can verify independently, or produce scheduled evidence packs. That is what Pro adds, and it is operations, not engine features.
  </div>
</div></section>

<section class="gc-section gc-section-tight"><div class="gc-container">
  <span class="gc-eyebrow">Retained leadership</span>
  <h2>Senior security cover, on a retainer</h2>
  <p class="gc-muted gc-measure">A separate thing from the platform. These are for a business that needs a named senior security leader accountable to the board. Priced on what is produced, and stated in terms of what you get rather than how many hours you get.</p>
  <div class="gc-grid gc-grid-3 gc-mt-8">
    <div class="gc-card">
      <h3>Advisory</h3>
      <p style="font-size:var(--gc-text-3xl);font-weight:700;color:var(--gc-text);margin:var(--gc-space-3) 0 var(--gc-space-1)">£2,500<span style="font-size:var(--gc-text-sm);font-weight:400;color:var(--gc-text-muted)">/mo</span></p>
      <p class="gc-muted" style="font-size:var(--gc-text-sm);margin-bottom:var(--gc-space-4)">Senior guidance. You keep the decisions.</p>
      <ul class="gc-list gc-muted" style="font-size:var(--gc-text-sm)">
        <li>A monthly board-ready risk report</li>
        <li>A same-week response when a customer sends a security questionnaire</li>
        <li>Policy and control design, written for your business</li>
        <li>Risk register kept current, and owned by you</li>
      </ul>
      <div class="gc-callout gc-mt-8" style="font-size:var(--gc-text-sm)">
        <strong>Outcome credit</strong>
        £500 per month credited each quarter when the agreed outcome is met &mdash; Cyber Essentials Plus issued, or a passed customer or vendor security questionnaire. Confirmed each quarter against the agreed outcome.
      </div>
      <a class="gc-btn gc-btn-secondary gc-btn-block gc-mt-8" href="/contact">Start a conversation</a>
    </div>
    <div class="gc-card">
      <h3>Managed</h3>
      <p style="font-size:var(--gc-text-3xl);font-weight:700;color:var(--gc-text);margin:var(--gc-space-3) 0 var(--gc-space-1)">£7,500<span style="font-size:var(--gc-text-sm);font-weight:400;color:var(--gc-text-muted)">/mo</span></p>
      <p class="gc-muted" style="font-size:var(--gc-text-sm);margin-bottom:var(--gc-space-4)">We own the execution as well as the advice.</p>
      <ul class="gc-list gc-muted" style="font-size:var(--gc-text-sm)">
        <li>Everything in Advisory, plus we do the work</li>
        <li>Monthly security reviews, and the actions closed out</li>
        <li>Board reporting and material risk, produced not requested</li>
        <li>Unlimited regulatory frameworks</li>
        <li>ISO 27001 and SOC 2 support</li>
        <li>Incident response retainer with a named contact</li>
      </ul>
      <a class="gc-btn gc-btn-primary gc-btn-block gc-mt-8" href="/contact">Start a conversation</a>
    </div>
    <div class="gc-card">
      <h3>Embedded</h3>
      <p style="font-size:var(--gc-text-3xl);font-weight:700;color:var(--gc-text);margin:var(--gc-space-3) 0 var(--gc-space-1)">£12,500<span style="font-size:var(--gc-text-sm);font-weight:400;color:var(--gc-text-muted)">/mo</span></p>
      <p class="gc-muted" style="font-size:var(--gc-text-sm);margin-bottom:var(--gc-space-4)">We hold the levers, end to end.</p>
      <ul class="gc-list gc-muted" style="font-size:var(--gc-text-sm)">
        <li>Everything in Managed, with the programme owned end to end</li>
        <li>Continuous risk monitoring across your estate</li>
        <li>Control operation and evidence production, continuously</li>
        <li>Board and regulator liaison, including the hard conversations</li>
        <li>Priority response (24h) and incident response leadership</li>
      </ul>
      <a class="gc-btn gc-btn-secondary gc-btn-block gc-mt-8" href="/contact">Talk to us</a>
    </div>
  </div>
</div></section>

<section class="gc-section gc-section-tight"><div class="gc-container">
  <span class="gc-eyebrow">Outcome package</span>
  <h2>Certified</h2>
  <p class="gc-muted gc-measure">A fixed fee for the work, and a second tranche released only when the certificate is issued. We do not guarantee the certification. The accredited certification body audits you and makes that decision, on their own criteria and their own schedule.</p>
  <div class="gc-grid gc-grid-2 gc-mt-8">
    <div class="gc-card">
      <p class="gc-eyebrow">Base fee</p>
      <p style="font-size:var(--gc-text-4xl);font-weight:700;color:var(--gc-text)">£7,500</p>
      <p class="gc-muted" style="font-size:var(--gc-text-sm)">Fixed fee, fixed scope. Preparation, evidence and audit management, agreed in writing before we start.</p>
      <p class="gc-eyebrow gc-mt-8">Outcome tranche</p>
      <p style="font-size:var(--gc-text-4xl);font-weight:700;color:var(--gc-accent-text)">+£2,500</p>
      <p class="gc-muted" style="font-size:var(--gc-text-sm)">Released only when the certificate is issued.</p>
      <p class="gc-eyebrow gc-mt-8">Total</p>
      <p style="font-size:var(--gc-text-4xl);font-weight:700;color:var(--gc-text)">£10,000</p>
      <p class="gc-muted" style="font-size:var(--gc-text-sm)">Total, if the certificate is issued.</p>
    </div>
    <div class="gc-card">
      <span class="gc-eyebrow">How it works</span>
      <ol class="gc-list" style="font-size:var(--gc-text-sm);margin-top:var(--gc-space-2)">
        <li><strong>We do the work.</strong> Fixed scope, fixed fee, agreed in writing before we start.</li>
        <li><strong>The certification body decides.</strong> They audit you and issue the certificate. Their decision, their schedule, their fee.</li>
        <li><strong>The £2,500 releases</strong> when the certificate is issued. It is contingent on the outcome, not on our opinion of it.</li>
        <li><strong>If we do not do the work as scoped, you do not pay the tranche.</strong> That is the point of splitting it this way.</li>
      </ol>
      <div class="gc-callout gc-callout-warn gc-mt-8" style="font-size:var(--gc-text-sm)">
        <strong>Not included</strong>
        The certification body's own audit fee. You pay that directly to them. We guarantee the work, not the certification.
      </div>
    </div>
  </div>
</div></section>

<section class="gc-section gc-section-tight"><div class="gc-container">
  <span class="gc-eyebrow">Coaching</span>
  <h2>Coaching, in a fixed block</h2>
  <p class="gc-muted gc-measure">For an in-house team that has the capability but not the confidence. Three sessions, written feedback and a review call. Booked in blocks of three.</p>
  <div class="gc-card gc-mt-8" style="max-width:var(--gc-container-narrow)">
    <h3>Coaching block</h3>
    <p style="font-size:var(--gc-text-3xl);font-weight:700;color:var(--gc-text);margin:var(--gc-space-3) 0 var(--gc-space-1)">£1,500</p>
    <p class="gc-muted" style="font-size:var(--gc-text-sm);margin-bottom:var(--gc-space-4)">Per block of three sessions</p>
    <ul class="gc-list gc-muted" style="font-size:var(--gc-text-sm)">
      <li>Three sessions with a senior security practitioner</li>
      <li>Written feedback after each one</li>
      <li>One review call at the end of the block</li>
      <li>Architecture review, control design and evidence-pack review</li>
    </ul>
    <a class="gc-btn gc-btn-secondary gc-btn-block gc-mt-8" href="/contact">Start a conversation</a>
  </div>
</div></section>

<section class="gc-section gc-section-tight"><div class="gc-container">
  <div class="gc-callout gc-callout-warn">
    <strong>What is not included in any price</strong>
    Certification and audit fees, which you pay to the certifying body. Penetration testing, which is a separate engagement with a specialist firm. Legal advice &mdash; we do not give it.
  </div>
  <p class="gc-muted" style="font-size:var(--gc-text-sm);margin-top:var(--gc-space-8)">All prices exclude VAT. Retained leadership and coaching carry a minimum three-month commitment. AWARE platform tiers are billed monthly or annually.</p>
</div></section>
""",
    ),
    _c(
        "contact",
        "Contact",
        "Contact GoodCISO about AI security and governance, CISO advisory, security architecture, regulatory readiness, or AWARE enterprise deployments.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Contact</span><h1>Tell us what you are securing</h1>
  <p class="gc-hero-sub">We will tell you plainly whether we are the right people. That answer is free and we will not chase you with a proposal afterwards.</p>
</div></section>
<section class="gc-section"><div class="gc-container gc-grid gc-grid-2">
  <div>
    <h2>Enquiry form</h2>
    <form name="contact" method="POST" data-netlify="true" netlify-honeypot="bot-field" id="contact-form">
      <input type="hidden" name="form-name" value="contact">
      <!-- Source attribution: where this enquiry came from. Filled
           client-side from ?src= or the referrer, so a conversion can be
           tied to the page and the message that produced it. Without it,
           a submission is a conversion with no attribution. -->
      <input type="hidden" name="source" id="contact-source" value="">
      <p style="display:none"><label>Do not fill this in: <input name="bot-field"></label></p>
      <div class="gc-grid" style="gap:var(--gc-space-4)">
        <div>
          <label for="f-name" style="display:block;font-weight:600;font-size:var(--gc-text-sm);margin-bottom:var(--gc-space-2)">Name</label>
          <input id="f-name" name="name" type="text" required autocomplete="name"
                 style="width:100%;padding:var(--gc-space-3);border:1px solid var(--gc-border-strong);border-radius:var(--gc-radius-md);background:var(--gc-surface);color:var(--gc-text);font:inherit;min-height:44px">
        </div>
        <div>
          <label for="f-email" style="display:block;font-weight:600;font-size:var(--gc-text-sm);margin-bottom:var(--gc-space-2)">Work email</label>
          <input id="f-email" name="email" type="email" required autocomplete="email"
                 style="width:100%;padding:var(--gc-space-3);border:1px solid var(--gc-border-strong);border-radius:var(--gc-radius-md);background:var(--gc-surface);color:var(--gc-text);font:inherit;min-height:44px">
        </div>
        <div>
          <label for="f-org" style="display:block;font-weight:600;font-size:var(--gc-text-sm);margin-bottom:var(--gc-space-2)">Organisation</label>
          <input id="f-org" name="organisation" type="text" autocomplete="organization"
                 style="width:100%;padding:var(--gc-space-3);border:1px solid var(--gc-border-strong);border-radius:var(--gc-radius-md);background:var(--gc-surface);color:var(--gc-text);font:inherit;min-height:44px">
        </div>
        <div>
          <label for="f-topic" style="display:block;font-weight:600;font-size:var(--gc-text-sm);margin-bottom:var(--gc-space-2)">How can we help?</label>
          <select id="f-topic" name="topic" required
                  style="width:100%;padding:var(--gc-space-3);border:1px solid var(--gc-border-strong);border-radius:var(--gc-radius-md);background:var(--gc-surface);color:var(--gc-text);font:inherit;min-height:44px">
            <option value="">Please choose&hellip;</option>
            <option value="ai-governance">AI security &amp; governance</option>
            <option value="ciso-advisory">CISO advisory</option>
            <option value="security-architecture">Security architecture</option>
            <option value="regulatory">Regulatory readiness</option>
            <option value="aware-enterprise">AWARE enterprise enquiry</option>
            <option value="general">General enquiry</option>
          </select>
        </div>
        <div>
          <label for="f-msg" style="display:block;font-weight:600;font-size:var(--gc-text-sm);margin-bottom:var(--gc-space-2)">Message</label>
          <textarea id="f-msg" name="message" rows="6" required
                    style="width:100%;padding:var(--gc-space-3);border:1px solid var(--gc-border-strong);border-radius:var(--gc-radius-md);background:var(--gc-surface);color:var(--gc-text);font:inherit"></textarea>
        </div>
        <div>
          <button class="gc-btn gc-btn-primary gc-btn-lg" type="submit">Send enquiry</button>
        </div>
      </div>
    </form>
  </div>
  <div>
    <h2>Direct</h2>
    <p><strong>General:</strong> <a href="mailto:hello@goodciso.org">hello@goodciso.org</a></p>
    <p><strong>Security disclosures:</strong> <a href="mailto:security@goodciso.org">security@goodciso.org</a></p>
    <div class="gc-callout">
      <strong>How we handle your enquiry</strong>
      We use your details to respond to the enquiry and for nothing else. We do not sell, share or add you to a marketing list without asking. See the <a href="/privacy">privacy notice</a> for the detail.
    </div>
    <h3 class="gc-mt-8">Response time</h3>
    <p class="gc-muted">We aim to reply within one working day. If it is urgent, say so in the subject line and it will come to us marked.</p>
  </div>
</div></section>
""",
    ),
    _c(
        "privacy",
        "Privacy notice",
        "How Good CISO Limited collects, uses and protects personal data, including the controller and processor roles for enquiries and website hosting.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Legal</span><h1>Privacy notice</h1>
</div></section>
<section class="gc-section"><div class="gc-container gc-container-narrow gc-prose">
  <p>Good CISO Limited (&ldquo;we&rdquo;) is the controller for personal data you give us directly through an enquiry, and for personal data collected through this website.</p>
  <h2>What we collect</h2>
  <ul class="gc-list">
    <li><strong>Enquiries:</strong> your name, work email, organisation and the content of your message.</li>
    <li><strong>Website:</strong> technical data such as IP address, user agent and requested URL, retained in server logs for security and reliability.</li>
  </ul>
  <h2>Why</h2>
  <p>To respond to your enquiry, to provide and secure this website, and to meet our legal obligations. We do not use your data for marketing without a separate, specific consent, and we do not sell it.</p>
  <h2>Processors and recipients</h2>
  <p>This website is hosted by Netlify, which processes server logs on our behalf. Email is delivered through Google Workspace. Where you submit an enquiry, the details you provide are visible to the GoodCISO team members who handle it. We do not disclose enquiry details to third parties for their own purposes.</p>
  <h2>Retention</h2>
  <p>Enquiry records are kept for as long as needed to deal with the matter and to meet legal obligations, and then deleted or anonymised. Server logs are retained on a short rolling window.</p>
  <h2>Your rights</h2>
  <p>You may request access to, correction of, or deletion of your personal data, and you may object to or restrict processing. Write to <a href="mailto:hello@goodciso.org">hello@goodciso.org</a>. You also have the right to complain to the UK Information Commissioner&rsquo;s Office.</p>
  <h2>International transfers</h2>
  <p>Some of our processors operate outside the UK. Where they do, transfers are covered by the UK International Data Transfer Addendum or an adequacy decision.</p>
  <h2>Contact</h2>
  <p>Good CISO Limited, company no. 16294946, registered in England &amp; Wales. Email <a href="mailto:hello@goodciso.org">hello@goodciso.org</a>.</p>
  <p class="gc-muted gc-mt-8">Last updated: 16 November 2026.</p>
</div></section>
""",
    ),
    _c(
        "terms",
        "Terms of service",
        "The terms governing use of the GoodCISO website and GoodCISO advisory services.",
        """
<section class="gc-hero gc-hero-sm"><div class="gc-container">
  <span class="gc-eyebrow">Legal</span><h1>Terms of service</h1>
</div></section>
<section class="gc-section"><div class="gc-container gc-container-narrow gc-prose">
  <h2>Scope</h2>
  <p>These terms govern use of this website. Advisory and consulting services are governed by the engagement letter or statement of work agreed with you, which takes precedence over these terms.</p>
  <h2>Information on this site</h2>
  <p>We take care to keep the information here accurate, but it is provided for general information and does not constitute advice on your circumstances. Where a page describes an AWARE capability, its implementation state is stated on that page and in the published capability register.</p>
  <h2>No warranty on outcomes</h2>
  <p>We do not warrant that using this site, our services, or AWARE will produce a particular regulatory, audit or certification outcome. Independent certification bodies make their own decisions. Nothing on this site guarantees the decision of an independent auditor or assessor.</p>
  <h2>Intellectual property</h2>
  <p>Good CISO Limited owns the content and design of this website and the AWARE name and marks. AWARE itself is licensed separately under the Apache License 2.0; the source is at <a href="https://github.com/GoodCISO/aware">github.com/GoodCISO/aware</a>.</p>
  <h2>Liability</h2>
  <p>To the extent permitted by law, we are not liable for indirect or consequential loss arising from use of this website. Nothing in these terms limits liability for fraud, death or personal injury caused by negligence, or any liability that cannot lawfully be limited.</p>
  <h2>Governing law</h2>
  <p>These terms are governed by the law of England and Wales, and the courts of England and Wales have exclusive jurisdiction.</p>
  <h2>Contact</h2>
  <p>Good CISO Limited, company no. 16294946. <a href="mailto:hello@goodciso.org">hello@goodciso.org</a></p>
  <p class="gc-muted gc-mt-8">Last updated: 16 November 2026.</p>
</div></section>
""",
    ),
]

# ==========================================================================
# DOCS — docs.aware.goodciso.org
# ==========================================================================
D_DOMAIN = "https://docs.aware.goodciso.org"
D_NAV = [
    Nav("Docs", "/"),
    Nav("AWARE", "https://aware.goodciso.org", external=True),
    Nav("Playground", "https://demo.aware.goodciso.org", external=True),
    Nav("GitHub", "https://github.com/GoodCISO/aware", external=True),
]
D_FOOTER = [
    ("Documentation", [
        Nav("Quick start", "/quick-start"),
        Nav("Installation", "/installation"),
        Nav("Architecture", "/architecture"),
        Nav("API reference", "/api-reference"),
        Nav("Configuration", "/configuration"),
        Nav("Deployment", "/deployment"),
    ]),
    ("Reference", [
        Nav("Security model", "/security-model"),
        Nav("Compliance", "/compliance"),
        Nav("Troubleshooting", "/troubleshooting"),
        Nav("Contributing", "/contributing"),
    ]),
    ("Project", [
        Nav("Product site", "https://aware.goodciso.org", external=True),
        Nav("GitHub", "https://github.com/GoodCISO/aware", external=True),
        Nav("npm", "https://www.npmjs.com/package/@goodciso/aware", external=True),
        Nav("Trust Centre", "https://aware.goodciso.org/trust-centre", external=True),
    ]),
]
D_TAGLINE = "AWARE documentation."

DOC_SECTIONS = [
    ("Getting started", [
        ("Introduction", "/"),
        ("What is AWARE?", "/what-is-aware"),
        ("Quick start", "/quick-start"),
        ("Installation", "/installation"),
    ]),
    ("Concepts", [
        ("Architecture", "/architecture"),
        ("Agent identity", "/agent-identity"),
        ("T0-T4 constraints", "/t0-t4"),
        ("Policy engine", "/policy-engine"),
        ("Delegation", "/delegation"),
        ("Revocation", "/revocation"),
        ("Audit & evidence", "/audit"),
        ("Execution assurance", "/execution-assurance"),
    ]),
    ("Operate", [
        ("Configuration", "/configuration"),
        ("Deployment", "/deployment"),
        ("Security model", "/security-model"),
        ("Compliance", "/compliance"),
        ("API reference", "/api-reference"),
        ("Troubleshooting", "/troubleshooting"),
        ("Contributing", "/contributing"),
    ]),
]


def _d(slug, title, desc, body):
    return Page(slug=slug, title=title, description=desc, body=body,
                canonical=f"{D_DOMAIN}/{slug}" if slug != "index" else f"{D_DOMAIN}/")


def _docs_layout(title, body):
    nav = []
    for group, items in DOC_SECTIONS:
        links = "".join(f'<li><a href="{l}">{t}</a></li>' for t, l in items)
        nav.append(f'<p class="gc-nav-group">{group}</p><ul>{links}</ul>')
    return f"""
<section class="gc-section-tight">
  <div class="gc-container gc-docs-layout">
    <nav class="gc-docs-nav" aria-label="Documentation">{''.join(nav)}</nav>
    <article class="gc-docs-body">
      {body}
    </article>
  </div>
</section>
"""


DOCS = [
    _d("index", "Introduction", "Documentation for AWARE, the open-source security control plane for autonomous AI agents.",
       _docs_layout("Introduction", """
<h1>AWARE documentation</h1>
<p class="gc-muted gc-text-lg">The security control plane for autonomous AI agents.</p>
<p>AWARE gives every agent a non-human identity, evaluates every tool call against policy <em>before</em> it runs, revokes credentials when authority must end, and records each decision in a hash chain that a third party can independently recompute.</p>
<div class="gc-callout">
  <strong>Version</strong>
  These docs describe <code>@goodciso/aware</code> <strong>2.12.3</strong>, Apache-2.0. The install command below installs exactly that version.
</div>
<h2>Where to start</h2>
<ul class="gc-list">
  <li><a href="/what-is-aware">What is AWARE?</a> &mdash; the model, in plain terms.</li>
  <li><a href="/quick-start">Quick start</a> &mdash; a running instance and a first evaluated tool call.</li>
  <li><a href="/architecture">Architecture</a> &mdash; the components and the request path.</li>
  <li><a href="/execution-assurance">Execution assurance</a> &mdash; what AWARE guarantees, and what it does not.</li>
</ul>
<h2>Two things worth knowing before you start</h2>
<div class="gc-callout gc-callout-warn">
  <strong>1. AWARE authorises; it does not verify execution.</strong>
  The policy engine decides whether an action is permitted. Nothing in the current design observes the target afterwards to confirm the action happened as authorised. See <a href="/execution-assurance">Execution assurance</a>.
</div>
<div class="gc-callout gc-callout-warn">
  <strong>2. Revocation is per-agent.</strong>
  Revoking an agent invalidates that agent&rsquo;s credential. Cascade to derived agents is not implemented. See <a href="/revocation">Revocation</a>.
</div>
""")),
    _d("what-is-aware", "What is AWARE?", "AWARE's model: identity, policy, constraints, revocation, audit, compliance.",
       _docs_layout("What is AWARE?", """
<h1>What is AWARE?</h1>
<p>AWARE is infrastructure for governing autonomous AI agents. It sits between an agent and the tools that agent calls, and it answers five questions on every call:</p>
<ol class="gc-list">
  <li><strong>Who</strong> is calling? A non-human identity with a credential that is stored only as a hash.</li>
  <li><strong>Is the tool known</strong>, and how risky is it?</li>
  <li><strong>What data tier</strong> is involved &mdash; PUBLIC, INTERNAL, CONFIDENTIAL or RESTRICTED?</li>
  <li><strong>Does a policy</strong> govern this agent and this tool?</li>
  <li><strong>What was decided</strong>, and can that decision be checked later?</li>
</ol>
<h2>The five layers</h2>
<div class="gc-table-wrap"><table class="gc-table">
  <thead><tr><th>Layer</th><th>Responsibility</th><th>State</th></tr></thead>
  <tbody>
    <tr><td>Identity</td><td>Non-human identity, hashed credentials, sessions, revocation</td><td><span class="gc-status gc-status-allow">implemented</span></td></tr>
    <tr><td>Policy engine</td><td>Deny-by-default evaluation of every tool call</td><td><span class="gc-status gc-status-allow">implemented</span></td></tr>
    <tr><td>T0-T4</td><td>Declared autonomy posture and promotion record</td><td><span class="gc-status gc-status-audit">partial</span></td></tr>
    <tr><td>Revocation</td><td>Immediate credential invalidation and audit</td><td><span class="gc-status gc-status-allow">implemented</span></td></tr>
    <tr><td>Audit &amp; evidence</td><td>Hash chain, independent verifier, exportable windows</td><td><span class="gc-status gc-status-allow">implemented</span></td></tr>
    <tr><td>Compliance mapping</td><td>Seven frameworks, control-to-control mapping</td><td><span class="gc-status gc-status-allow">implemented</span></td></tr>
    <tr><td>Delegation</td><td>Hierarchical authority and cascade</td><td><span class="gc-status gc-status-none">roadmap</span></td></tr>
    <tr><td>Execution assurance</td><td>Atomic commit, target-side enforcement, verification</td><td><span class="gc-status gc-status-none">roadmap</span></td></tr>
  </tbody>
</table></div>
""")),
    _d("quick-start", "Quick start", "Install AWARE, start the service, and evaluate your first tool call against the real policy engine.",
       _docs_layout("Quick start", """
<h1>Quick start</h1>
<p>Get a running instance and evaluate a tool call. About five minutes.</p>
<h2>1. Install</h2>
<pre class="gc-code"><code>npm install @goodciso/aware</code></pre>
<p>That installs version <code>2.12.3</code> &mdash; the version these docs describe.</p>
<h2>2. Set the credential pepper</h2>
<p>AWARE stores credentials as salted, peppered hashes. The service <strong>refuses to start</strong> without a pepper, which is the correct behaviour for a system that holds credentials.</p>
<pre class="gc-code"><code>export AWARE_CREDENTIAL_PEPPER="a-long-random-string"
# or, equivalently:
export SECRET_KEY="a-long-random-string"</code></pre>
<h2>3. Start the service</h2>
<pre class="gc-code"><code>npm start</code></pre>
<p>The entrypoint is <code>src/api/index.js</code>. The v2 gateway, coordinator and training components are separate processes with their own Dockerfiles.</p>
<h2>4. Confirm it is alive</h2>
<pre class="gc-code"><code>curl -s localhost:3000/api/health</code></pre>
<h2>5. Evaluate a tool call</h2>
<pre class="gc-code"><code>const { getPolicyEngine } = require('@goodciso/aware/policies');

const engine = getPolicyEngine();

const decision = engine.evaluate({
  agentId: 'agent-001',
  tool: 'read_customer_record',
  context: { dataTier: 'CONFIDENTIAL' }
});

console.log(decision.decision);  // ALLOW | DENY | AUDIT | NO_POLICY
console.log(decision.reason);</code></pre>
<p>With no matching policy, a tool whose risk is <code>HIGH</code> or <code>CRITICAL</code> is denied. That is the default-deny posture, and it is the behaviour you want.</p>
<h2>Next</h2>
<ul class="gc-list">
  <li><a href="/installation">Installation options</a></li>
  <li><a href="/policy-engine">Policy engine</a></li>
  <li><a href="https://demo.aware.goodciso.org">Playground</a> &mdash; the same decisions, interactively.</li>
</ul>
""")),
    _d("installation", "Installation", "Install AWARE from npm, or build the container images for the service, gateway, coordinator and training components.",
       _docs_layout("Installation", """
<h1>Installation</h1>
<h2>From npm</h2>
<pre class="gc-code"><code>npm install @goodciso/aware@2.12.3</code></pre>
<p>The package is Apache-2.0 and ships the service, the policy engine, the compliance mapper and the disclosure tooling. The React operator UI is built separately.</p>
<h2>With Docker</h2>
<p>Four images ship in the repository:</p>
<div class="gc-table-wrap"><table class="gc-table">
  <thead><tr><th>File</th><th>Component</th></tr></thead>
  <tbody>
    <tr><td><code>Dockerfile</code></td><td>The service</td></tr>
    <tr><td><code>Dockerfile.gateway</code></td><td>The v2 gateway, a thin BFF in front of the coordinator</td></tr>
    <tr><td><code>Dockerfile.coordinator</code></td><td>The coordinator and decision routing</td></tr>
    <tr><td><code>Dockerfile.training</code></td><td>The training components</td></tr>
  </tbody>
</table></div>
<pre class="gc-code"><code>docker compose up -d          # full stack
docker compose -f docker-compose.coordinator.yml up -d   # coordinator only</code></pre>
<h2>Environment</h2>
<div class="gc-table-wrap"><table class="gc-table">
  <thead><tr><th>Variable</th><th>Purpose</th></tr></thead>
  <tbody>
    <tr><td><code>AWARE_CREDENTIAL_PEPPER</code></td><td>Pepper for credential hashing. Required (or <code>SECRET_KEY</code>).</td></tr>
    <tr><td><code>AWARE_GATEWAY_KILL_SWITCH</code></td><td>Set to <code>1</code> to make the gateway return 503 immediately.</td></tr>
    <tr><td><code>AWARE_GATEWAY_MAX_BODY_BYTES</code></td><td>Request body limit enforced before the proxy fires.</td></tr>
  </tbody>
</table></div>
""")),
    _d("architecture", "Architecture", "AWARE's components and the request path, derived from the shipped source.",
       _docs_layout("Architecture", """
<h1>Architecture</h1>
<p>AWARE&rsquo;s request path, from the agent to the recorded decision.</p>
<ol class="gc-list">
  <li>The agent presents its credential and requests a tool call.</li>
  <li>The <strong>gateway</strong> validates the request, enforces the body-size limit, and proxies to the coordinator. It is deliberately a thin BFF.</li>
  <li>The <strong>coordinator</strong> resolves the agent&rsquo;s identity and asks the <strong>policy engine</strong> to evaluate the call.</li>
  <li>The engine checks tool known-ness and risk level, the data tier, and any matching policy in the <strong>policy store</strong>. The <strong>tool catalogue</strong> supplies risk levels and data-tier permissions.</li>
  <li>The decision &mdash; <code>ALLOW</code>, <code>DENY</code>, <code>AUDIT</code> or <code>NO_POLICY</code>, with a reason &mdash; is written to the <strong>audit chain</strong>.</li>
</ol>
<h2>Components</h2>
<div class="gc-table-wrap"><table class="gc-table">
  <thead><tr><th>Module</th><th>Path</th><th>Responsibility</th></tr></thead>
  <tbody>
    <tr><td>Policy engine</td><td><code>src/policies/engine.js</code></td><td>Decision logic. Default deny.</td></tr>
    <tr><td>Tool catalogue</td><td><code>src/policies/tool-catalog.js</code></td><td>Risk levels, approval requirements, data-tier permissions.</td></tr>
    <tr><td>Policy store</td><td><code>src/policies/store.js</code></td><td>Policy persistence and hot reload.</td></tr>
    <tr><td>Identity</td><td><code>src/api/models/Agent.js</code>, <code>src/agents/registry.js</code></td><td>Credentials, hashing, rotation, state.</td></tr>
    <tr><td>Sessions</td><td><code>src/agents/identity-provider-v2.js</code></td><td>JWT sessions with trust-domain claims.</td></tr>
    <tr><td>Revocation</td><td><code>src/kill-switch/revocation-service.js</code></td><td>Revoke an agent; apply blast radius.</td></tr>
    <tr><td>Emergency</td><td><code>src/emergency/</code></td><td>Kill-signal propagation, shutdown control.</td></tr>
    <tr><td>Audit</td><td><code>src/audit/</code>, <code>src/disclosure/</code></td><td>Hash chain, verifier, exportable windows.</td></tr>
    <tr><td>Compliance</td><td><code>src/compliance/framework-mapper.js</code></td><td>Framework and control mapping.</td></tr>
    <tr><td>Gateway</td><td><code>src/gateway/server.js</code></td><td>Thin BFF, kill switch, body limit.</td></tr>
  </tbody>
</table></div>
""")),
    _d("agent-identity", "Agent identity", "How AWARE mints, hashes, rotates and revokes agent credentials, and what session tokens carry.",
       _docs_layout("Agent identity", """
<h1>Agent identity</h1>
<h2>The credential lifecycle</h2>
<ol class="gc-list">
  <li><strong>Register</strong> &mdash; the agent is assigned a UUID.</li>
  <li><strong>Provision</strong> &mdash; 32 random bytes, hex-encoded. The raw value is returned <strong>once</strong>, at provisioning only.</li>
  <li><strong>Store</strong> &mdash; what is persisted is a salted PBKDF2 hash with a server-side pepper. The raw secret is never stored.</li>
  <li><strong>Verify</strong> &mdash; a constant-time comparison. A rejected credential leaks no timing information.</li>
  <li><strong>Rotate</strong> &mdash; the stored hash is replaced immediately. Rotation is a cutover, not a grace period: the previous credential is not retained for parallel validation.</li>
  <li><strong>Revoke</strong> &mdash; the agent&rsquo;s state flips, so its credential stops verifying.</li>
</ol>
<h2>Sessions</h2>
<p>Session tokens are JWTs signed with HS256, carrying extended claims:</p>
<div class="gc-table-wrap"><table class="gc-table">
  <thead><tr><th>Claim</th><th>Purpose</th></tr></thead>
  <tbody>
    <tr><td><code>trustDomain</code></td><td>The boundary the session is valid in</td></tr>
    <tr><td><code>blastRadius</code></td><td>How far the session&rsquo;s authority extends</td></tr>
    <tr><td><code>sessionId</code></td><td>Server-side session handle</td></tr>
    <tr><td><code>executionContext</code></td><td>The context the call is made in</td></tr>
  </tbody>
</table></div>
<h2>What this is not</h2>
<div class="gc-callout gc-callout-danger">
  <strong>Not key-bound identity</strong>
  AWARE authenticates the holder of a shared secret. There is no asymmetric key pair, no X.509 certificate and no SPIFFE identifier. A bearer secret is replayable by anything that obtains it; short-lived sessions, revocation and blast-radius scoring reduce that exposure, but they do not eliminate it.
</div>
""")),
    _d("t0-t4", "T0-T4 constraints", "The five autonomy tiers, what they mean, and how promotions are recorded.",
       _docs_layout("T0-T4 constraints", """
<h1>T0-T4 constraints</h1>
<div class="gc-grid gc-grid-5">
  <div class="gc-card"><span class="gc-term">T0</span><h3 class="gc-mt-4">Audit Trail</h3><p class="gc-muted">Every action is logged. Foundational, always on.</p></div>
  <div class="gc-card"><span class="gc-term">T1</span><h3 class="gc-mt-4">Crypto Identity</h3><p class="gc-muted">A non-human identity for every agent. Foundational, always on.</p></div>
  <div class="gc-card"><span class="gc-term">T2</span><h3 class="gc-mt-4">Guardrailed</h3><p class="gc-muted">Operational policies constrain what the agent can do.</p></div>
  <div class="gc-card"><span class="gc-term">T3</span><h3 class="gc-mt-4">Policy-Driven</h3><p class="gc-muted">Advanced governance: rate limits, decision routing.</p></div>
  <div class="gc-card"><span class="gc-term">T4</span><h3 class="gc-mt-4">Autonomous</h3><p class="gc-muted">Full self-operation under declared constraints.</p></div>
</div>
<h2>Promotions</h2>
<p>Tier promotions are validated events. The accepted set is exactly <code>T0</code>&hellip;<code>T4</code>, and each payload is checked against the published OpenAPI schema before it is recorded. A promotion therefore leaves a reconstructible history of an agent&rsquo;s changing autonomy posture.</p>
<h2>What the tier does and does not control</h2>
<div class="gc-callout gc-callout-warn">
  <strong>The tier is a posture record, not an enforcement switch</strong>
  The policy engine evaluates by tool risk level and data classification tier. It does <em>not</em> read the agent&rsquo;s T-tier. A T2 agent and a T4 agent calling an unmatched high-risk tool are both denied. The tier records the governance posture and the promotion path; the engine enforces independently of it.
</div>
""")),
    _d("policy-engine", "Policy engine", "AWARE's policy evaluation: decisions, inputs, hot reload and the extension contract.",
       _docs_layout("Policy engine", """
<h1>Policy engine</h1>
<h2>Decisions</h2>
<p><code>evaluate(request)</code> returns one of four decisions.</p>
<div class="gc-grid gc-grid-4">
  <div class="gc-card"><span class="gc-status gc-status-allow">ALLOW</span><p class="gc-mt-4 gc-mb-0">A matching policy permits it.</p></div>
  <div class="gc-card"><span class="gc-status gc-status-deny">DENY</span><p class="gc-mt-4 gc-mb-0">Refused. The default for risky unmatched tools.</p></div>
  <div class="gc-card"><span class="gc-status gc-status-audit">AUDIT</span><p class="gc-mt-4 gc-mb-0">Permitted, recorded for review.</p></div>
  <div class="gc-card"><span class="gc-status gc-status-none">NO_POLICY</span><p class="gc-mt-4 gc-mb-0">Nothing governs this tool at this tier.</p></div>
</div>
<h2>Inputs</h2>
<div class="gc-table-wrap"><table class="gc-table">
  <thead><tr><th>Signal</th><th>Effect</th></tr></thead>
  <tbody>
    <tr><td>Tool known</td><td>Unknown tools are denied outright.</td></tr>
    <tr><td>Risk level</td><td><code>HIGH</code> and <code>CRITICAL</code> are denied with no policy present.</td></tr>
    <tr><td>Data tier</td><td>PUBLIC &lt; INTERNAL &lt; CONFIDENTIAL &lt; RESTRICTED.</td></tr>
    <tr><td>Matching policy</td><td>Conditions on agent, tool, targets and windows.</td></tr>
    <tr><td>Approval</td><td>Some tools require approval.</td></tr>
    <tr><td>Rate limits</td><td>Windowed call frequency and volume limits.</td></tr>
  </tbody>
</table></div>
<h2>Hot reload</h2>
<p>Policies reload without a restart via <code>/api/policies/hot</code>. The routes live in <code>src/api/routes/hot-reload-policies.js</code>.</p>
<h2>The extension contract</h2>
<p>The extension point is an observer, not a participant. An extension receives a deep copy of the request and the decision. It cannot rewrite the verdict in place, and a throwing extension is recorded rather than propagated. A contract test asserts that an extension cannot change the decision &mdash; if it could, it would be a policy bypass.</p>
""")),
    _d("delegation", "Delegation", "AWARE's delegated authority model: the design, the current state, and what is missing.",
       _docs_layout("Delegation", """
<h1>Delegation</h1>
<h2>The intended model</h2>
<ol class="gc-list">
  <li>A parent agent holds a set of authorities.</li>
  <li>It delegates a named subset to a child, recorded as a signed decision.</li>
  <li>The child&rsquo;s authority is bounded by the parent&rsquo;s &mdash; always.</li>
  <li>Revoking the parent invalidates the child&rsquo;s derived authority.</li>
  <li>The chain is reconstructible for audit.</li>
</ol>
<h2>Current status</h2>
<div class="gc-callout gc-callout-danger">
  <strong>Roadmap</strong>
  There is no delegation graph in the shipped implementation. The coordinator that would manage one exists; the graph, the inheritance invariant and the cascade that walks it do not. The IETF decoupled-authorisation ADR explicitly defers the &ldquo;sub-agent permissions &isin; parent&rdquo; invariant.
</div>
<p>If you are designing for delegated authority, plan for the model above and treat the enforcement as future work. AWARE&rsquo;s revocation research reached the same conclusion independently &mdash; you cannot revoke over a delegation graph you do not have.</p>
""")),
    _d("revocation", "Revocation", "Revoking an AWARE agent: what happens, what is recorded, and what cascade does not do.",
       _docs_layout("Revocation", """
<h1>Revocation</h1>
<h2>What happens</h2>
<ol class="gc-list">
  <li>The agent&rsquo;s state flips, so its credential no longer verifies.</li>
  <li>A blast-radius penalty is applied to its trail.</li>
  <li>The decision is written to the audit trail.</li>
</ol>
<h2>Cascade</h2>
<div class="gc-callout gc-callout-danger">
  <strong>Not implemented</strong>
  Revoking a parent does not revoke its children. The revocation service applies to exactly one agent, and the blast-radius logic applies a penalty to that same agent rather than traversing to derived agents. An earlier README stated otherwise and was corrected in release 2.12.2 because the source did not support it.
</div>
<h2>Whole-service stop</h2>
<pre class="gc-code"><code>export AWARE_GATEWAY_KILL_SWITCH=1</code></pre>
<p>The gateway then returns 503 immediately, before any upstream work.</p>
<h2>Distributed propagation</h2>
<p>AWARE ships Raft-based kill-signal propagation and leader-election components, with a leader-only guard on propagation. Treat these as components you would integrate, not a distributed guarantee you switch on: the running service constructs the revocation service marked <em>pending Raft setup</em>.</p>
""")),
    _d("audit", "Audit and evidence", "AWARE's hash-chained audit trail, the independent verifier, exportable windows and recorded failure outcomes.",
       _docs_layout("Audit and evidence", """
<h1>Audit &amp; evidence</h1>
<h2>The chain</h2>
<p>Each record&rsquo;s hash is computed over the record&rsquo;s canonical serialisation plus the previous record&rsquo;s hash. Altering any earlier record breaks every hash that follows it.</p>
<h2>The independent verifier</h2>
<p>The verifier is decoupled from the writer and uses only the standard library, so verification does not require trusting the code that produced the records. It ships with a 1,000-record fixture.</p>
<h2>Exportable windows</h2>
<p>An exported window carries its own <code>prevHash</code> and <code>hash</code>, so a third party can recompute the chain over that slice without access to your database.</p>
<div class="gc-callout gc-callout-warn">
  <strong>The anchor is declared, not verified</strong>
  The window&rsquo;s first record points outside the window, so it can only be proven to be a chain root when its hash matches the genesis value. Full-chain verification is the stronger check. The export reports <code>anchorVerified</code> accordingly rather than implying more than it establishes.
</div>
<h2>Completeness</h2>
<p>Failure outcomes &mdash; timeouts, backend errors, internal errors, cost caps, and <code>ok:false</code> responses &mdash; are written to the chain as well as successes. The chain evidences what the system did, not only what worked.</p>
""")),
    _d("execution-assurance", "Execution assurance", "Authorise, approve, revalidate, commit, verify: what AWARE does and what remains roadmap.",
       _docs_layout("Execution assurance", """
<h1>Execution assurance</h1>
<div class="gc-table-wrap"><table class="gc-table">
  <thead><tr><th>Stage</th><th>Question</th><th>AWARE today</th></tr></thead>
  <tbody>
    <tr><td>Authorise</td><td>Is this agent permitted to attempt this?</td><td><span class="gc-status gc-status-allow">implemented</span></td></tr>
    <tr><td>Approve</td><td>Has a human approved this instance?</td><td><span class="gc-status gc-status-allow">implemented</span> approval requirement</td></tr>
    <tr><td>Revalidate</td><td>Is the authority still valid at the moment of action?</td><td><span class="gc-status gc-status-audit">partial</span> session and revocation checks</td></tr>
    <tr><td>Commit</td><td>Did the change land atomically?</td><td><span class="gc-status gc-status-none">roadmap</span> Commit Guard</td></tr>
    <tr><td>Verify</td><td>Did the target do what was authorised?</td><td><span class="gc-status gc-status-none">roadmap</span> no execution receipt</td></tr>
  </tbody>
</table></div>
<div class="gc-callout gc-callout-danger">
  <strong>State it accurately</strong>
  AWARE authorises and records. It does not verify that an authorised action was carried out as intended, because nothing in the current design observes the target afterwards. If you need that guarantee, you need to build it &mdash; that is what the Commit Guard and target-side enforcement work is for.
</div>
""")),
    _d("configuration", "Configuration", "AWARE configuration: environment variables, policy hot reload and the tool catalogue.",
       _docs_layout("Configuration", """
<h1>Configuration</h1>
<div class="gc-table-wrap"><table class="gc-table">
  <thead><tr><th>Variable</th><th>Default</th><th>Purpose</th></tr></thead>
  <tbody>
    <tr><td><code>AWARE_CREDENTIAL_PEPPER</code></td><td>none</td><td>Pepper for credential hashing. Required, or <code>SECRET_KEY</code>.</td></tr>
    <tr><td><code>SECRET_KEY</code></td><td>none</td><td>Alternative source for the pepper.</td></tr>
    <tr><td><code>AWARE_GATEWAY_KILL_SWITCH</code></td><td>unset</td><td><code>1</code> makes the gateway return 503.</td></tr>
    <tr><td><code>AWARE_GATEWAY_MAX_BODY_BYTES</code></td><td>set by deployment</td><td>Request body limit, enforced before the proxy.</td></tr>
  </tbody>
</table></div>
<h2>Policy hot reload</h2>
<pre class="gc-code"><code>PUT /api/policies/:category/:name</code></pre>
<p>Updating a policy through this route triggers a reload without restarting the service.</p>
""")),
    _d("deployment", "Deployment", "Deploy AWARE with Docker, Kubernetes, or the compose topologies.",
       _docs_layout("Deployment", """
<h1>Deployment</h1>
<h2>Compose</h2>
<pre class="gc-code"><code>docker compose up -d
docker compose -f docker-compose.coordinator.yml up -d</code></pre>
<p>The gateway sits behind <code>profiles: ["full"]</code> in compose so it can be started selectively.</p>
<h2>Kubernetes</h2>
<p><code>k8s-deployment.yaml</code> in the repository root is a working starting point. Adjust the secret references for the credential pepper before applying it &mdash; a manifest that references a real secret by name is not a secret.</p>
<h2>The operator UI</h2>
<p>The React UI is served by nginx, proxying <code>/api</code> to the v2 gateway. <code>nginx.conf</code> in the repository root is the reference configuration.</p>
<h2>Before you go live</h2>
<ul class="gc-list">
  <li>Set the credential pepper from a secret manager, not a file in the image.</li>
  <li>Confirm <code>AWARE_GATEWAY_KILL_SWITCH</code> works in your environment.</li>
  <li>Decide your audit retention period &mdash; the product does not impose one.</li>
  <li>Read <a href="/security-model">the security model</a> so you know where the trust boundaries are.</li>
</ul>
""")),
    _d("security-model", "Security model", "AWARE's trust boundaries, cryptographic mechanisms, identity model and what it does not protect against.",
       _docs_layout("Security model", """
<h1>Security model</h1>
<h2>Trust boundaries</h2>
<div class="gc-table-wrap"><table class="gc-table">
  <thead><tr><th>Boundary</th><th>Trust posture</th></tr></thead>
  <tbody>
    <tr><td>Agent</td><td>Untrusted. Presents a credential; never authorises itself.</td></tr>
    <tr><td>Gateway, coordinator, identity registry, policy engine</td><td>Trusted. Decisions are made here.</td></tr>
    <tr><td>Target system</td><td>Not observed by AWARE today. No execution verification.</td></tr>
  </tbody>
</table></div>
<h2>Mechanisms</h2>
<div class="gc-table-wrap"><table class="gc-table">
  <thead><tr><th>Mechanism</th><th>Algorithm</th></tr></thead>
  <tbody>
    <tr><td>Credential storage</td><td>PBKDF2, per-credential salt, server-side pepper</td></tr>
    <tr><td>Credential comparison</td><td>Constant-time</td></tr>
    <tr><td>Credential generation</td><td>32 bytes CSPRNG</td></tr>
    <tr><td>Session token</td><td>JWT, HS256</td></tr>
    <tr><td>Audit chain</td><td>SHA-256 over canonical serialisation plus previous hash</td></tr>
  </tbody>
</table></div>
<h2>Threats AWARE addresses</h2>
<ul class="gc-list">
  <li>An agent calling a tool it has no policy for &mdash; denied by default.</li>
  <li>A revoked agent continuing to act &mdash; its credential stops verifying.</li>
  <li>Silent failure inside the decision path &mdash; failure outcomes are written to the chain.</li>
  <li>Evidence that cannot be independently checked &mdash; the verifier is decoupled from the writer.</li>
</ul>
<h2>Threats AWARE does not address</h2>
<ul class="gc-list">
  <li>A compromised host running the agent.</li>
  <li>A leaked bearer credential, before revocation is triggered.</li>
  <li>An action that was authorised but carried out wrongly &mdash; no execution verification.</li>
  <li>A target system that ignores the decision it was given.</li>
</ul>
""")),
    _d("compliance", "Compliance", "The frameworks AWARE maps to, the control coverage, and what a mapping does not mean.",
       _docs_layout("Compliance", """
<h1>Compliance</h1>
<div class="gc-table-wrap"><table class="gc-table">
  <thead><tr><th>Framework</th><th>Version</th><th>Coverage</th></tr></thead>
  <tbody>
    <tr><td>CSA AI Controls Matrix</td><td>v1</td><td>184 of 243 control IDs, all 18 domains</td></tr>
    <tr><td>NIST AI RMF</td><td>1.0</td><td>Govern, Map, Measure, Manage</td></tr>
    <tr><td>ISO/IEC 27001</td><td>2022</td><td>Annex A</td></tr>
    <tr><td>ISO/IEC 42001</td><td>v1.0-2026-07-28</td><td>AI management system</td></tr>
    <tr><td>OWASP Agentic Skills Top 10</td><td>v1.0-2026</td><td>Full catalogue</td></tr>
    <tr><td>OWASP Top 10 for MCP</td><td>2025</td><td>10 of 10</td></tr>
    <tr><td>DORA</td><td>2022</td><td>Operational resilience</td></tr>
    <tr><td>MITRE ATLAS</td><td>v2026.06</td><td>Technique mapping</td></tr>
  </tbody>
</table></div>
<h2>What the AICM subset means</h2>
<p>CSA AICM v1 contains 243 controls across 18 domains. AWARE ships a verified subset of <strong>184</strong> control IDs, covering every domain. The remaining controls are unmapped pending an updated public source. Say &ldquo;184 of 243&rdquo;, not &ldquo;full coverage&rdquo;.</p>
<div class="gc-callout gc-callout-warn">
  <strong>A mapping is not a certification</strong>
  Mapping a control supports preparation and evidence collection. It is not an audit opinion, not a certificate, and not a guarantee that a requirement is met. The certification body decides.
</div>
""")),
    _d("api-reference", "API reference", "AWARE's HTTP API: health, policies, hot reload and agent lifecycle routes.",
       _docs_layout("API reference", """
<h1>API reference</h1>
<p>The full OpenAPI specification ships in the package at <code>docs/openapi.yaml</code>. The routes below are the ones most used.</p>
<div class="gc-table-wrap"><table class="gc-table">
  <thead><tr><th>Route</th><th>Method</th><th>Purpose</th></tr></thead>
  <tbody>
    <tr><td><code>/api/health</code></td><td>GET</td><td>Liveness and version.</td></tr>
    <tr><td><code>/api/policies</code></td><td>GET</td><td>List policies.</td></tr>
    <tr><td><code>/api/policies/hot</code></td><td>PUT</td><td>Update a policy and reload it without a restart.</td></tr>
    <tr><td><code>/api/policies/:category/:name</code></td><td>PUT</td><td>Hot-reload a single policy.</td></tr>
    <tr><td><code>/registry/agent/:agentId/heartbeat</code></td><td>PUT</td><td>Agent heartbeat, with ownership verification.</td></tr>
  </tbody>
</table></div>
<h2>Tier promotions</h2>
<p>Promotions are validated against the <code>TierPromotion</code> schema in <code>docs/openapi.yaml</code>. The accepted tier set is <code>T0</code> through <code>T4</code>.</p>
""")),
    _d("troubleshooting", "Troubleshooting", "Common AWARE startup and runtime failures, and what they mean.",
       _docs_layout("Troubleshooting", """
<h1>Troubleshooting</h1>
<h2>The service exits immediately</h2>
<p>Neither <code>AWARE_CREDENTIAL_PEPPER</code> nor <code>SECRET_KEY</code> is set. The service fails fast on purpose: it will not start a credential store it cannot hash safely.</p>
<h2>The gateway returns 503</h2>
<p>Check <code>AWARE_GATEWAY_KILL_SWITCH</code>. If it is <code>1</code>, the gateway is in its emergency state and returns 503 before any upstream work.</p>
<h2>A tool is denied and I expected ALLOW</h2>
<p>This is the default-deny posture working. A tool that is unknown, or whose risk is <code>HIGH</code> or <code>CRITICAL</code>, is denied when no policy matches. Add a policy, or check the risk level in the tool catalogue.</p>
<h2>A credential will not verify</h2>
<p>Verify the pepper the credential was hashed with matches the pepper the service is running with. Credentials hashed under a different pepper cannot verify, and that is correct behaviour.</p>
<h2>Unit tests fail on a fresh checkout</h2>
<p>At the time of writing, the unit suite has known failures traced to two modules absent from the source tree (<code>src/compliance/aidefend-mapper.js</code> and <code>src/compliance/memory-component-failure-annotator.js</code>) and one unimplemented outcome-filter rule. This is recorded in the capability register.</p>
""")),
    _d("contributing", "Contributing", "How to contribute to AWARE, and the conventions the project follows.",
       _docs_layout("Contributing", """
<h1>Contributing</h1>
<p>AWARE is Apache-2.0 and accepts contributions. The repository is <a href="https://github.com/GoodCISO/aware">github.com/GoodCISO/aware</a>.</p>
<h2>Getting set up</h2>
<pre class="gc-code"><code>git clone https://github.com/GoodCISO/aware
cd aware
npm install
npm test</code></pre>
<h2>Conventions</h2>
<ul class="gc-list">
  <li>Tests use the Node built-in test runner: <code>node --test</code>.</li>
  <li>Standards suites are separated per compliance framework under <code>test/standards/</code>.</li>
  <li>Browser behaviour is covered by Playwright.</li>
  <li>Architecture decisions are recorded as ADRs under <code>docs/adr/</code>.</li>
</ul>
<h2>Claim discipline</h2>
<div class="gc-callout">
  <strong>The project&rsquo;s rule</strong>
  A capability is only described as implemented when the code exists, is reachable from a runtime path, and is covered by tests. The capability register that governs the AWARE website is maintained from the same standard, and it records what is <em>not</em> implemented as carefully as what is.
</div>
""")),
]

# ==========================================================================
# DEMO — demo.aware.goodciso.org
# ==========================================================================
M_DOMAIN = "https://demo.aware.goodciso.org"
M_NAV = [
    Nav("Playground", "/"),
    Nav("Docs", "https://docs.aware.goodciso.org", external=True),
    Nav("AWARE", "https://aware.goodciso.org", external=True),
    Nav("GitHub", "https://github.com/GoodCISO/aware", external=True),
]
M_FOOTER = [
    ("Explore", [
        Nav("Playground", "/"),
        Nav("T0-T4 model", "https://aware.goodciso.org/platform/t0-t4", external=True),
        Nav("Execution assurance", "https://aware.goodciso.org/platform/execution-assurance", external=True),
    ]),
    ("Project", [
        Nav("Product site", "https://aware.goodciso.org", external=True),
        Nav("Documentation", "https://docs.aware.goodciso.org", external=True),
        Nav("GitHub", "https://github.com/GoodCISO/aware", external=True),
        Nav("npm", "https://www.npmjs.com/package/@goodciso/aware", external=True),
    ]),
]
M_TAGLINE = "An interactive model of AWARE's decision semantics."

DEMO = [
    Page(
        slug="index", title="Interactive playground", status="simulated",
        description="Seven scenarios running AWARE's real policy decision vocabulary: PII access, delegated authority, revocation, unauthorised change and expired approval. Every decision is simulated.",
        canonical=f"{M_DOMAIN}/",
        body="""
<section class="gc-section-tight">
  <div class="gc-container">
    <div class="gc-callout gc-callout-warn">
      <strong>This is a simulation</strong>
      Every decision below is computed by a model of AWARE&rsquo;s policy semantics, not by a running AWARE instance and not by any customer environment. The decision vocabulary, the reasons and the evaluation order match the shipped engine. Nothing here is connected to a live system, and no decision shown here describes anything that actually happened.
    </div>
    <h1 class="gc-mt-8">Policy playground</h1>
    <p class="gc-muted gc-measure">Pick a scenario. The panel shows the agent identity, the requested action, the applicable constraints, the evaluation, the decision and the evidence that would be written.</p>
    <div class="gc-play gc-mt-8">
      <div class="gc-play-side" role="group" aria-label="Scenarios" id="scenarios"></div>
      <div class="gc-card" id="readout" aria-live="polite"></div>
    </div>
  </div>
</section>
""",
        extra_head='<script src="/assets/playground.js" defer></script>',
    ),
]
