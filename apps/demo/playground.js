/**
 * AWARE playground — interactive decision model.
 *
 * This is a SIMULATION. It renders the real policy engine's decision
 * vocabulary (ALLOW / DENY / AUDIT / NO_POLICY), the real data-tier hierarchy
 * and the real tool-risk semantics, against constructed scenarios.
 *
 * It is NOT connected to any live AWARE instance, any customer environment,
 * or any network. Every scenario here is illustrative. The UI says so, on
 * every screen, because a demo that hides its own nature is a marketing
 * claim wearing a lab coat.
 *
 * The scenarios are deliberately split by outcome so a reader can see both
 * sides of the same engine: some decisions come from the risk and tier
 * rules, and some come from the authority rules — and the two produce
 * different reasons.
 */
(function () {
  'use strict';

  var TIERS = {
    PUBLIC: 0, INTERNAL: 1, CONFIDENTIAL: 2, RESTRICTED: 3
  };

  var SCENARIOS = [
    {
      id: 'pii',
      title: 'Agent requests customer PII',
      agent: { id: 'agent-support-01', tier: 'T2', state: 'ACTIVE' },
      call: { tool: 'read_customer_record', risk: 'HIGH', dataTier: 'CONFIDENTIAL' },
      policies: [],
      intent: 'Retrieve the billing history of customer C-88421 to answer a support ticket.',
      authority: 'Agent holds a T2 (Guardrailed) constraint level. No explicit tool grant.',
      evaluation: [
        ['Tool known', 'read_customer_record — HIGH risk'],
        ['Data tier', 'CONFIDENTIAL — tool is not permitted at this tier'],
        ['Matching policy', 'none'],
        ['Result', 'Unknown-policy rule fires first: HIGH risk defaults to DENY']
      ],
      decision: 'DENY',
      reason: 'No policy found for read_customer_record (default deny for HIGH risk)',
      evidence: [
        ['event', 'POLICY_DECISION'],
        ['agent', 'agent-support-01'],
        ['tool', 'read_customer_record'],
        ['decision', 'DENY'],
        ['reason', 'No policy found for read_customer_record (default deny for HIGH risk)'],
        ['policyId', 'null'],
        ['riskLevel', 'HIGH'],
        ['requiresApproval', 'true']
      ],
      execution: 'Not executed. The call was refused before reaching the tool.',
      note: 'A policy granting this tool at the CONFIDENTIAL tier would change the decision to ALLOW. That is the point of the policy store.'
    },
    {
      id: 'exceed',
      title: 'Child agent exceeds delegated authority',
      agent: { id: 'agent-child-07', tier: 'T1', state: 'ACTIVE' },
      call: { tool: 'deploy_production', risk: 'CRITICAL', dataTier: 'INTERNAL' },
      policies: [],
      intent: 'Deploy the queued build to the production environment.',
      authority: 'Child agent at T1 (Crypto Identity). It has no delegation grant from a parent — none exists in the current implementation.',
      evaluation: [
        ['Tool known', 'deploy_production — CRITICAL risk'],
        ['Data tier', 'INTERNAL'],
        ['Matching policy', 'none'],
        ['Delegation', 'no delegation graph exists, so no inherited authority is checked']
      ],
      decision: 'DENY',
      reason: 'No policy found for deploy_production (default deny for CRITICAL risk)',
      evidence: [
        ['event', 'POLICY_DECISION'],
        ['agent', 'agent-child-07'],
        ['tool', 'deploy_production'],
        ['decision', 'DENY'],
        ['riskLevel', 'CRITICAL'],
        ['requiresApproval', 'true']
      ],
      execution: 'Not executed.',
      note: 'This scenario is honest about its limits: a delegated-authority check would be a stronger control, but the delegation graph is roadmap. The deny comes from the risk rule, not from an authority comparison.'
    },
    {
      id: 'revoked',
      title: 'Revoked agent attempts another operation',
      agent: { id: 'agent-batch-12', tier: 'T3', state: 'REVOKED' },
      call: { tool: 'write_report', risk: 'LOW', dataTier: 'INTERNAL' },
      policies: [],
      intent: 'Write the weekly compliance summary to the reporting bucket.',
      authority: 'Agent was revoked during a prior incident response. Its credential no longer verifies.',
      evaluation: [
        ['Agent state', 'REVOKED — credential fails verification before any policy is consulted'],
        ['Tool known', 'write_report — LOW risk'],
        ['Matching policy', 'none'],
        ['Result', 'revocation short-circuits the request']
      ],
      decision: 'DENY',
      reason: 'Agent state is REVOKED; credential does not verify',
      evidence: [
        ['event', 'AGENT_REVOKED'],
        ['agent', 'agent-batch-12'],
        ['decision', 'DENY'],
        ['reason', 'Agent state is REVOKED; credential does not verify'],
        ['blastRadius', 'penalty applied to the revoked agent trail'],
        ['recorded', 'revocation written to the audit trail']
      ],
      execution: 'Not executed. The credential stopped working the moment the agent was revoked.',
      note: 'Note what this scenario does NOT show: the agent has no children here. Cascade to derived agents is specified but not implemented.'
    },
    {
      id: 'unauthorised-infra',
      title: 'Unauthorised infrastructure change',
      agent: { id: 'agent-ops-03', tier: 'T4', state: 'ACTIVE' },
      call: { tool: 'modify_security_group', risk: 'CRITICAL', dataTier: 'RESTRICTED' },
      policies: [],
      intent: 'Open port 443 to the public internet on the production security group.',
      authority: 'Agent holds a T4 (Autonomous) constraint level — the highest. No policy grants this tool.',
      evaluation: [
        ['Tool known', 'modify_security_group — CRITICAL risk'],
        ['Data tier', 'RESTRICTED — tool barred at this tier'],
        ['Matching policy', 'none'],
        ['Tier', 'T4 does not create an exemption from the risk rules']
      ],
      decision: 'DENY',
      reason: 'No policy found for modify_security_group (default deny for CRITICAL risk)',
      evidence: [
        ['event', 'POLICY_DECISION'],
        ['agent', 'agent-ops-03'],
        ['tool', 'modify_security_group'],
        ['decision', 'DENY'],
        ['riskLevel', 'CRITICAL'],
        ['requiresApproval', 'true']
      ],
      execution: 'Not executed.',
      note: 'This is the scenario that shows the honest limit of the tier model: T4 means the operator declared this agent autonomous. It does not mean the engine lets it do anything.'
    },
    {
      id: 'expired',
      title: 'Operation uses an expired approval',
      agent: { id: 'agent-change-05', tier: 'T3', state: 'ACTIVE' },
      call: { tool: 'rotate_secret', risk: 'HIGH', dataTier: 'CONFIDENTIAL' },
      policies: [],
      intent: 'Rotate a service credential using the approval granted during yesterday’s change window.',
      authority: 'A matching policy exists, but the approval attached to it expired before the call was made.',
      evaluation: [
        ['Tool known', 'rotate_secret — HIGH risk'],
        ['Matching policy', 'policy-rot-01'],
        ['Approval', 'expired — the approval window closed'],
        ['Result', 'the policy condition on a live approval is not satisfied']
      ],
      decision: 'DENY',
      reason: 'Approval for policy-rot-01 has expired',
      evidence: [
        ['event', 'POLICY_DECISION'],
        ['agent', 'agent-change-05'],
        ['tool', 'rotate_secret'],
        ['decision', 'DENY'],
        ['policyId', 'policy-rot-01'],
        ['reason', 'Approval for policy-rot-01 has expired']
      ],
      execution: 'Not executed.',
      note: 'Expiry is what makes approval meaningful. An approval that never expires is a permanent grant wearing a temporary label.'
    },
    {
      id: 'audit-only',
      title: 'Low-risk read permitted with audit',
      agent: { id: 'agent-report-02', tier: 'T2', state: 'ACTIVE' },
      call: { tool: 'list_templates', risk: 'LOW', dataTier: 'PUBLIC' },
      policies: [],
      intent: 'List the available report templates so the agent can pick one.',
      authority: 'Agent holds a T2 (Guardrailed) constraint level.',
      evaluation: [
        ['Tool known', 'list_templates — LOW risk'],
        ['Data tier', 'PUBLIC — permitted at this tier'],
        ['Matching policy', 'none'],
        ['Result', 'low-risk known tool with no matching policy falls through to the default decision']
      ],
      decision: 'AUDIT',
      reason: 'No matching policy, using default',
      evidence: [
        ['event', 'POLICY_DECISION'],
        ['agent', 'agent-report-02'],
        ['tool', 'list_templates'],
        ['decision', 'AUDIT'],
        ['policyId', 'null'],
        ['riskLevel', 'LOW'],
        ['requiresApproval', 'false']
      ],
      execution: 'Executed. The call was permitted and recorded for review.',
      note: 'Note the default decision is still deny at the engine level; a low-risk known tool with no policy is the documented exception that is audited rather than silently allowed.'
    },
    {
      id: 'tier-mismatch',
      title: 'Tier promotion and its limit',
      agent: { id: 'agent-vision-04', tier: 'T4', state: 'ACTIVE' },
      call: { tool: 'export_dataset', risk: 'HIGH', dataTier: 'RESTRICTED' },
      policies: [],
      intent: 'Export the full training dataset for offline analysis.',
      authority: 'Agent was promoted to T4 (Autonomous) — a validated TierPromotion event, recorded in the decision chain.',
      evaluation: [
        ['Tier', 'T4 — promotion recorded as a validated event'],
        ['Tool known', 'export_dataset — HIGH risk'],
        ['Data tier', 'RESTRICTED — tool barred at this tier'],
        ['Matching policy', 'none'],
        ['Tier effect on enforcement', 'none — the engine does not branch on the tier']
      ],
      decision: 'DENY',
      reason: 'No policy found for export_dataset (default deny for HIGH risk)',
      evidence: [
        ['event', 'POLICY_DECISION'],
        ['agent', 'agent-vision-04'],
        ['tool', 'export_dataset'],
        ['decision', 'DENY'],
        ['riskLevel', 'HIGH'],
        ['tier', 'T4'],
        ['tierPromotion', 'recorded — validated TierPromotion event']
      ],
      execution: 'Not executed.',
      note: 'The tier was genuinely promoted and genuinely recorded. It still did not grant the capability. The tier is a declared posture; the policy store is what grants authority.'
    }
  ];

  var state = { index: 0 };

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function statusClass(d) {
    if (d === 'ALLOW') return 'gc-status-allow';
    if (d === 'DENY') return 'gc-status-deny';
    if (d === 'AUDIT') return 'gc-status-audit';
    return 'gc-status-none';
  }

  function render(scenario, index) {
    var host = document.getElementById('readout');
    if (!host) return;

    var ev = '';
    scenario.evidence.forEach(function (row) {
      ev += '<div class="gc-readout-row"><dt>' + esc(row[0]) + '</dt><dd>' + esc(row[1]) + '</dd></div>';
    });

    var ev2 = '';
    scenario.evaluation.forEach(function (row) {
      ev2 += '<div class="gc-readout-row"><dt>' + esc(row[0]) + '</dt><dd>' + esc(row[1]) + '</dd></div>';
    });

    host.innerHTML =
      '<div class="gc-card" style="margin-bottom:var(--gc-space-5)">' +
        '<div style="display:flex;flex-wrap:wrap;gap:var(--gc-space-3);align-items:center;justify-content:space-between;margin-bottom:var(--gc-space-4)">' +
          '<h2 style="margin:0;font-size:var(--gc-text-2xl)">' + esc(scenario.title) + '</h2>' +
          '<span class="gc-status ' + statusClass(scenario.decision) + '">' + esc(scenario.decision) + '</span>' +
        '</div>' +
        '<p class="gc-muted">' + esc(scenario.intent) + '</p>' +

        '<h3 style="margin-top:var(--gc-space-6);font-size:var(--gc-text-base);text-transform:uppercase;letter-spacing:var(--gc-tracking-wide);color:var(--gc-text-subtle)">Identity</h3>' +
        '<div class="gc-readout">' +
          '<div class="gc-readout-row"><dt>Agent</dt><dd>' + esc(scenario.agent.id) + '</dd></div>' +
          '<div class="gc-readout-row"><dt>Constraint level</dt><dd>' + esc(scenario.agent.tier) + '</dd></div>' +
          '<div class="gc-readout-row"><dt>State</dt><dd>' + esc(scenario.agent.state) + '</dd></div>' +
        '</div>' +

        '<h3 style="margin-top:var(--gc-space-6);font-size:var(--gc-text-base);text-transform:uppercase;letter-spacing:var(--gc-tracking-wide);color:var(--gc-text-subtle)">Requested action</h3>' +
        '<div class="gc-readout">' +
          '<div class="gc-readout-row"><dt>Tool</dt><dd>' + esc(scenario.call.tool) + '</dd></div>' +
          '<div class="gc-readout-row"><dt>Risk level</dt><dd>' + esc(scenario.call.risk) + '</dd></div>' +
          '<div class="gc-readout-row"><dt>Data tier</dt><dd>' + esc(scenario.call.dataTier) + '</dd></div>' +
          '<div class="gc-readout-row"><dt>Authority</dt><dd>' + esc(scenario.authority) + '</dd></div>' +
        '</div>' +

        '<h3 style="margin-top:var(--gc-space-6);font-size:var(--gc-text-base);text-transform:uppercase;letter-spacing:var(--gc-tracking-wide);color:var(--gc-text-subtle)">Policy evaluation</h3>' +
        '<div class="gc-readout">' + ev2 + '</div>' +

        '<h3 style="margin-top:var(--gc-space-6);font-size:var(--gc-text-base);text-transform:uppercase;letter-spacing:var(--gc-tracking-wide);color:var(--gc-text-subtle)">Decision</h3>' +
        '<div class="gc-readout">' +
          '<div class="gc-readout-row"><dt>Decision</dt><dd><span class="gc-status ' + statusClass(scenario.decision) + '">' + esc(scenario.decision) + '</span></dd></div>' +
          '<div class="gc-readout-row"><dt>Reason</dt><dd>' + esc(scenario.reason) + '</dd></div>' +
        '</div>' +

        '<h3 style="margin-top:var(--gc-space-6);font-size:var(--gc-text-base);text-transform:uppercase;letter-spacing:var(--gc-tracking-wide);color:var(--gc-text-subtle)">Evidence recorded</h3>' +
        '<div class="gc-readout">' + ev + '</div>' +

        '<h3 style="margin-top:var(--gc-space-6);font-size:var(--gc-text-base);text-transform:uppercase;letter-spacing:var(--gc-tracking-wide);color:var(--gc-text-subtle)">Execution</h3>' +
        '<p class="gc-muted">' + esc(scenario.execution) + '</p>' +

        '<div class="gc-callout gc-callout-warn" style="margin-top:var(--gc-space-5);margin-bottom:0">' +
          '<strong>What this scenario shows</strong>' + esc(scenario.note) +
        '</div>' +
      '</div>';
  }

  function init() {
    var list = document.getElementById('scenarios');
    if (!list) return;

    SCENARIOS.forEach(function (s, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'gc-scenario';
      b.setAttribute('aria-pressed', i === 0 ? 'true' : 'false');
      b.textContent = s.title;
      b.addEventListener('click', function () {
        state.index = i;
        Array.prototype.forEach.call(list.querySelectorAll('.gc-scenario'), function (el, j) {
          el.setAttribute('aria-pressed', j === i ? 'true' : 'false');
        });
        render(s, i);
      });
      list.appendChild(b);
    });

    render(SCENARIOS[0], 0);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
