# AWARE Capability Register

**Status:** authoritative · **Version:** 1.0 · **Date:** 2026-11-16
**Subject:** `@goodciso/aware` v2.12.3, source at `/Users/alfie/src/AWARE`, public repo `github.com/GoodCISO/aware`, Apache-2.0.

## How to read this document

Every capability AWARE might advertise is classified into exactly one state:

| State | Meaning |
|---|---|
| **IMPLEMENTED** | Present in the source, reachable from a runtime path, and supported by tests or a reproducible demonstration. |
| **PARTIALLY IMPLEMENTED** | Real code exists, but an important part of the advertised behaviour is missing, unwired, or untested. |
| **DEMONSTRATION** | Illustrated in a simulation, fixture, or mock. Not connected to a production system. |
| **ROADMAP** | Planned and specified, not implemented. |
| **UNVERIFIED** | Insufficient evidence to make a public claim. |

Three independent axes are tracked, because collapsing them is how a security product ends up over-claiming:

- **Code exists** — is there source that implements the behaviour?
- **Wired into a runtime path** — does a running service actually execute it, or is it a module nothing imports?
- **Test-covered** — does an automated test assert it?

A capability is only **IMPLEMENTED** when all three hold.

This register governs every product page, diagram, document, demonstration and commercial claim. **A roadmap capability is never presented as a production feature.**

---

## 1. Capability register

### 1.1 Agent identity

| # | Capability | State | Evidence | Notes |
|---|---|---|---|---|
| 1.1.1 | Non-human agent identifier (UUID) | **IMPLEMENTED** | `src/api/models/Agent.js:80` — `crypto.randomUUID()` | Runtime path: `src/api/index.js` (`npm start` entrypoint). |
| 1.1.2 | Credential generation, 32 random bytes, hex-encoded | **IMPLEMENTED** | `src/api/models/Agent.js:104` — `crypto.randomBytes(32).toString('hex')` | Raw value returned once at provisioning only (`:115`). |
| 1.1.3 | Credential stored as a salted PBKDF2 hash, never plaintext | **IMPLEMENTED** | `src/api/models/Agent.js:25-35` — `hashCredential()`; `:109` stores the hash | Salt per credential; pepper from `AWARE_CREDENTIAL_PEPPER` or `SECRET_KEY` (`:15-19`). Boot fails if neither is set. |
| 1.1.4 | Constant-time credential comparison | **IMPLEMENTED** | `src/api/models/Agent.js:52` — `crypto.timingSafeEqual` | |
| 1.1.5 | Credential rotation | **IMPLEMENTED** | `src/api/models/Agent.js:119`, `src/agents/registry.js:269` | Audit event `CREDENTIAL_ROTATED` written on success and failure. |
| 1.1.6 | `registry.verify()` correctness fix | **IMPLEMENTED** | `CHANGELOG.md:48-59`; `src/agents/registry.js:251-257` | Fixed in 2.12.3 — it previously compared a PBKDF2 hash against a raw credential and could never succeed. 10 regression tests at `test/unit/agent-lifecycle.test.js`. |
| 1.1.7 | JWT session tokens with extended claims | **IMPLEMENTED** | `src/agents/identity-provider-v2.js:161` — `jwt.sign(...)` | Claims: `trustDomain`, `blastRadius`, `sessionId`, `executionContext` (`:123`). |
| 1.1.8 | **Cryptographic (asymmetric) agent identity — X.509, Ed25519, SPIFFE** | **UNVERIFIED** | No asymmetric key-pair or certificate code found. `src/agents/attestation-service.js` verifies JWTs; `identity-provider-v2.js:162` uses **HS256 (symmetric)**. | **This is the single most important correction.** The identity layer authenticates a holder of a shared secret. It does not bind an identity to a key the agent alone holds. Describe AWARE as *credential-based agent identity with hashed secrets and revocable sessions* — not "cryptographic identity that cannot be faked". |
| 1.1.9 | Attestation across trust domains | **PARTIALLY IMPLEMENTED** | `src/agents/attestation-service.js` (JWT verification, 15-minute cache TTL `:9`); `identity-provider-v2.js:333` `verifyAttestation()` | Cross-domain trust check exists. The underlying attestation strength inherits 1.1.8. |
| 1.1.10 | Session management and revocation cache | **IMPLEMENTED** | `src/agents/session-manager.js`, `src/agents/revocation-cache.js` | |

### 1.2 T0–T4 constraint model

| # | Capability | State | Evidence | Notes |
|---|---|---|---|---|
| 1.2.1 | Five named tiers T0–T4 with descriptions | **IMPLEMENTED** | `src/ui/src/components/ConstraintEnforcementView.js:7-13` — `CONSTRAINT_LEVELS` | T0 Audit Trail · T1 Crypto Identity · T2 Guardrailed · T3 Policy-Driven · T4 Autonomous. |
| 1.2.2 | Tier enum accepted by the v2 API | **IMPLEMENTED** | `src/v2/tier_promotions_handler.js:39` — `VALID_TIERS = ['T0'…'T4']` | Validated against `docs/openapi.yaml` (`:10`). |
| 1.2.3 | Tier promotion events recorded | **IMPLEMENTED** | `src/v2/tier_promotions_handler.js`, `src/db/tier-promotions.js` | Router wired at `src/api/index.js`. |
| 1.2.4 | **Per-tier differentiated enforcement behaviour** | **PARTIALLY IMPLEMENTED** | `src/policies/engine.js` — `evaluate()` branches on tool known-ness, risk level (`HIGH`/`CRITICAL`), data tier (`PUBLIC`/`INTERNAL`/`CONFIDENTIAL`/`RESTRICTED`, `:265-270`), policy conditions and approval. It does **not** read a tier. | The policy engine enforces *by tool risk and data classification*. The T0–T4 ladder is a **declared classification and promotion model**, not five distinct enforcement regimes. The tier is stored and promoted; the engine does not branch on it. State this plainly. |
| 1.2.5 | Tier shown with enforcement rate in the UI | **DEMONSTRATION** | `src/ui/src/containers/ConstraintEnforcementContainer.js:10,19` — hardcoded mock agents (`agent-003`, `c4`) with `status: 'enforced'` literals | Displayed in the shipped UI as though real. Not backed by a live enforcement feed. |
| 1.2.6 | Tier definitions sourced from `src/server.js` | **DEMONSTRATION — do not use** | `src/server.js` injects `mockAgents` and hardcodes the tier table with `enforced: true` | `src/server.js` is **not** the `npm start` entrypoint (`node src/api/index.js`). `CHANGELOG.md:89` explicitly corrects an earlier README that pointed readers here. Never cite `src/server.js` as evidence of a tier capability. |

### 1.3 Policy engine

| # | Capability | State | Evidence | Notes |
|---|---|---|---|---|
| 1.3.1 | Per-tool-call policy evaluation with `ALLOW` / `DENY` / `AUDIT` / `NO_POLICY` | **IMPLEMENTED** | `src/policies/engine.js:12-17` (`Decision`), `:88` (`evaluate()`) | Real runtime path. |
| 1.3.2 | Default-deny posture | **IMPLEMENTED** | `src/policies/engine.js:22` — `DEFAULT_DECISION = DENY`; unknown or `HIGH`/`CRITICAL` risk tools are denied even with no matching policy (`:100-110`) | This is the product's strongest single property. Lead with it. |
| 1.3.3 | Data-tier classification and enforcement | **IMPLEMENTED** | `src/policies/engine.js:186-192`, `:263-270`; `src/policies/model.js:64` | Ordered hierarchy PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED. |
| 1.3.4 | Tool risk classification and approval requirement | **IMPLEMENTED** | `src/policies/tool-catalog.js:214` (default risk for unknown tools), `:282` `getRiskLevel()`, `:302` `isAllowedForDataTier()` | |
| 1.3.5 | Hot reload of policies without restart | **IMPLEMENTED** | `src/api/routes/hot-reload-policies.js`; mounted at `src/api/index.js:298-306` (`/api/policies/hot`) | Six route handlers exported. |
| 1.3.6 | Credential classification | **IMPLEMENTED** | `src/policies/credential-classifier.js` | |
| 1.3.7 | Parameter validation | **IMPLEMENTED** | `src/policies/parameter-validator.js` | |
| 1.3.8 | Shadow-tool detection (unauthorised tool use observed at the gateway) | **IMPLEMENTED** | `src/policies/shadow-detector.js`; `src/policies/tool-observation-proxy.js` | |
| 1.3.9 | Extension point: observers cannot alter a decision | **IMPLEMENTED** | `src/policies/engine.js:39-77` | Extensions receive a deep copy; a throwing extension is recorded, never propagated (`:50-58`). Enforced by `test/unit/extension/extension-contract.test.js`. |
| 1.3.10 | Per-agent sandbox policies | **PARTIALLY IMPLEMENTED** | `src/policies/permission-model.js`, `sandbox-decision-emitter.js` | Decision is emitted; end-to-end sandbox enforcement depends on the host runtime. |

### 1.4 Revocation and emergency control

| # | Capability | State | Evidence | Notes |
|---|---|---|---|---|
| 1.4.1 | Revoke an agent; credentials stop verifying | **IMPLEMENTED** | `src/kill-switch/revocation-service.js`; agent state flips, `checkCredential()` fails | `CHANGELOG.md:88` confirms revocation invalidates the credential. |
| 1.4.2 | Revocation written to the audit trail | **IMPLEMENTED** | `src/agents/registry.js:272,283` — `CREDENTIAL_ROTATED` audit calls on revoke/rotate paths | |
| 1.4.3 | Blast-radius penalty applied to a revoked agent | **IMPLEMENTED** | `src/agents/revocation-cache.js` `_applyBlastRadius()` | Applies a penalty factor to **the revoked agent itself**. |
| 1.4.4 | **Hierarchical / cascading revocation to derived agents** | **ROADMAP** | `CHANGELOG.md:88` — "Cascade to derived agents is **specified, not implemented**". `revocation-service.js:168` revokes exactly one agent. A search of `src/` for "cascade" returns one unrelated comment in `src/policies/tool-observation-proxy.js`. | **Never claim cascade.** "Kill the parent, the children go too" was explicitly retracted in 2.12.2. |
| 1.4.5 | Raft-based kill-signal propagation between nodes | **IMPLEMENTED (component)** | `src/emergency/kill-switch-propagator.js:8-9` — "broadcasts kill signals via Raft consensus"; `:44` `propagate()`; `:45-52` leader-only guard | Component is implemented and tested. See 1.4.7 for what it is *not* wired into. |
| 1.4.6 | Leader election | **IMPLEMENTED (component)** | `src/election/index.js:2` — "Raft-inspired algorithm"; `:125` vote request, `:136` RPC note | `:5` — "For simulation, nodes call each other directly." Treat as a simulation-grade component. |
| 1.4.7 | `RevocationService` constructed in the running service | **PARTIALLY IMPLEMENTED** | `src/api/index.js:48` — constructed with the comment "pending Raft setup" | The propagation path exists in code but is not fully wired into the running server. State it as *component-level implementation, not a distributed guarantee*. |
| 1.4.8 | Emergency shutdown controller, kill-signal entry | **IMPLEMENTED (component)** | `src/emergency/shutdown-controller.js`, `src/emergency/kill-signal-entry.js` | |
| 1.4.9 | Gateway kill switch (`AWARE_GATEWAY_KILL_SWITCH=1` → 503) | **IMPLEMENTED** | `src/gateway/server.js:13` | Immediate, whole-service. |

### 1.5 Delegation and hierarchy

| # | Capability | State | Evidence | Notes |
|---|---|---|---|---|
| 1.5.1 | **Delegation graph — parent/child agent relationships with authority inheritance** | **ROADMAP** | `docs/adr/ADR-078-aware-arxiv-2608-30091-vera-edge-revocation-monitor.md:80-81` — a search for `parentAgent`, `parentId`, `delegatedBy`, `grantedBy`, `ancestors`, `child_agents`, `childAgents` returns **five hits, all unrelated**. `ADR-065:66` defers the "sub-agent permissions ⊆ parent" invariant. | **No delegation graph exists.** ADR-078 reduces the revocation question to "does AWARE have a delegation graph to revoke over?" and answers no. This is the largest gap between the product's stated story and its source. |
| 1.5.2 | Sub-agent permissions ⊆ parent permissions | **ROADMAP** | `docs/adr/ADR-065-aware-ietf-decoupled-agent-authorization.md:66` — explicitly deferred | |
| 1.5.3 | Coordinator with sub-agent handling | **PARTIALLY IMPLEMENTED** | `src/coordinator/index.js`, `src/coordinator/http-server.js` | Coordinator exists; the delegation *model* it would manage does not. |
| 1.5.4 | Model routing / heuristic routing | **IMPLEMENTED** | `src/routing/heuristic-calculator.js`, `src/coordinator/model-router.js` | |
| 1.5.5 | **Pheromone-based routing / path selection** | **ROADMAP** | `src/routing/pheromone-router.js` exists and initialises an evaporation job (`:44-47`) but is **not wired into a runtime path**. `CHANGELOG.md:90` — "the router that would steer work by trail strength is built but is not wired into a runtime path." `README.md:301` — "AWARE does not implement pheromone-based path selection." | The *trail* (blast-radius penalty on revocation) is implemented; the *router* is not. Also note `README.md:296-297` bullets belong to the AMRO-S paper, not AWARE (`CHANGELOG.md:91`). |

### 1.6 Audit, evidence and disclosure

| # | Capability | State | Evidence | Notes |
|---|---|---|---|---|
| 1.6.1 | Hash-chained audit trail | **IMPLEMENTED** | `src/disclosure/disclosure-record.js:132` — `computeWindowRecordHash()` = sha256(canonicalSerialize(record) + prevHash) | Chain structure with `prevHash` links (`:105`, `:129`). |
| 1.6.2 | Independent stdlib chain verifier | **IMPLEMENTED** | `CHANGELOG.md:192,215` — "Independent stdlib chain verifier — decoupled verifier with 1k fixture" | Verifier is decoupled from the writer by design. |
| 1.6.3 | Exportable disclosure records (third-party verifiable window) | **IMPLEMENTED** | `src/disclosure/disclosure-record.js:331,406-411` | A window can be exported with its `prevHash`/`hash` so a third party can recompute it. |
| 1.6.4 | Anchor verification | **PARTIALLY IMPLEMENTED** | `src/disclosure/disclosure-record.js:411` — `anchorVerified: chain[0].prevHash === GENESIS_HASH` | The anchor is **declared, not verified** (`CHANGELOG.md:22-23`): the first record's `prevHash` points outside the window and is verifiable only when it is the genesis hash. `verifyFullChain()` covers the full chain. |
| 1.6.5 | Failure outcomes written to the chain (not only successes) | **IMPLEMENTED** | `CHANGELOG.md:138` | Timeout, backend error, internal error, cost-cap and `ok:false` are now recorded — the chain evidences completeness, not just success. |
| 1.6.6 | Decision chain with depth metric | **IMPLEMENTED** | `docs/adr/ADR-080-aware-decision-chain-depth-metric.md` | |
| 1.6.7 | Audit module | **IMPLEMENTED** | `src/audit/` | |

### 1.7 Execution assurance — **read this before writing any copy**

| # | Capability | State | Evidence | Notes |
|---|---|---|---|---|
| 1.7.1 | **Commit Guard** | **ROADMAP** | No file, symbol, route, or test matches `commit guard`, `commitGuard`, or `commit_guard` anywhere in `src/`, `backend/`, `docs/`, `test/`, `tests/`. | **Not implemented. Not a partial implementation. It does not exist.** Introduce it only as a future architecture. |
| 1.7.2 | **Atomic commit of consequential actions** | **ROADMAP** | No `atomic`, `two-phase commit`, `prepare/commit`, or transaction-rollback machinery for agent actions. The only "two-phase" hits in the tree are ADR-062/063 prose about *directory replacement* during a migration — unrelated to action commit. | Never advertise atomicity of agent actions. |
| 1.7.3 | **Target-side enforcement** (the target system independently verifies AWARE's authorisation) | **ROADMAP** | No target-side verification protocol, challenge, or attestation exchange found. `integrations/` contains only `ifandai` and `mycelium`. | Never advertise target-side enforcement. |
| 1.7.4 | **Independent execution verification** (a third party confirms the action actually happened as authorised) | **ROADMAP** | No execution receipt from a target, no post-action verification agent, no receipt verifier. | Never advertise independent execution verification. |
| 1.7.5 | Policy evaluation happens **before** the action | **IMPLEMENTED** | `src/policies/engine.js:88` `evaluate()` is consulted before a tool call proceeds | This is authorisation-before-execution. It is **not** execution verification. |
| 1.7.6 | Gateway as a thin BFF in front of the coordinator | **IMPLEMENTED** | `src/gateway/server.js:1-3` | Small dependency footprint (express + proxy). |
| 1.7.7 | Request body size limit on the gateway | **IMPLEMENTED** | `src/gateway/server.js:53-54` — `AWARE_GATEWAY_MAX_BODY_BYTES` | 413 before the proxy fires. |

**Honest framing for the website.** AWARE today provides *authorisation before execution* — a deny-by-default policy engine that evaluates a tool call against the agent's identity, the tool's risk, the data tier and the policy store, and emits `ALLOW`/`DENY`/`AUDIT` with a hashed, exportable evidence trail. It does **not** verify that an authorised action was carried out as intended, because nothing in the current design observes the target after the fact. The five-stage model — *Intent → Identity → Delegated Authority → Policy → Commit Guard → Verified Execution → Evidence* — is the **roadmap** architecture, with Identity and Policy implemented today, and Delegation, Commit Guard and Verified Execution to come.

This distinction is the site's most important editorial responsibility. A buyer who believes AWARE already verifies execution, and discovers otherwise during an audit, loses the account and the credibility.

### 1.8 Compliance mapping

| # | Capability | State | Evidence | Notes |
|---|---|---|---|---|
| 1.8.1 | Framework mapper with registered frameworks | **IMPLEMENTED** | `src/compliance/framework-mapper.js` — 7 registered: `CSA_AI_CM` (v1), `NIST_AI_RMF` (1.0), `ISO_27001` (2022), `DORA` (2022), `OWASP_AST10` (v1.0-2026), `OWASP_MCP_TOP_10` (2025), `ISO_42001` (v1.0-2026-07-28) | **7, not 8.** The README's "eight" is wrong; use seven. |
| 1.8.2 | CSA AICM v1 control catalogue | **IMPLEMENTED** | `src/compliance/aicm-v1-catalog.js` — **184 control IDs across 18 domains**, verified by count | Domain spread: AIS 11, CEK 14, DCS 13, IAM 10, DSP 19, GRC 8, UEM 11, I&S 9, STA 14, TVM 13, MDS 9, IPY 2, HRS 10, SEF 8, LOG 10, BCR 10, CCC 7, A&A 6 = 184. The source header states the same figure (`:10`). |
| 1.8.3 | AICM coverage is a **subset** | **IMPLEMENTED — must be stated** | `aicm-v1-catalog.js:4-12` — CSA AICM v1 has 243 controls; the file ships 184; the remaining ~59 are unmapped | Say "184 of 243 AICM v1 controls across all 18 domains". Never "full AICM coverage". |
| 1.8.4 | MITRE ATLAS v2026.06 technique mapper | **IMPLEMENTED** | `src/compliance/atlas-mapper.js`, `src/compliance/atlas-catalog.js` | Post-observation annotator; 7 initial rule functions. |
| 1.8.5 | OWASP Agentic Skills Top 10 (AST10) coverage | **IMPLEMENTED** | `src/compliance/ast10-catalog.js`; `CHANGELOG.md:169` | |
| 1.8.6 | OWASP MCP Top 10 coverage, 10/10 | **IMPLEMENTED** | `src/compliance/mcp-top10-catalog.js`, `mcp-governance-catalog.js`; `CHANGELOG.md:29-30` | 2.12.1 corrected an overstated 8/10 claim that missed MCP08. |
| 1.8.7 | ISO 42001 catalogue | **IMPLEMENTED** | `src/compliance/iso42001-catalog.js` | |
| 1.8.8 | Posture calculation and report generation | **IMPLEMENTED** | `src/compliance/report-generator.js:78-93` — per-framework posture and control listing | |
| 1.8.9 | **AIDEFEND mapper** (AID-D/AID-H/AID-M/AID-E rule families) | **UNVERIFIED — module missing** | `src/compliance/aidefend-mapper.js` **does not exist**, but `test/unit/compliance/aidefend-mapper.test.js` exists and expects it. 33 test failures from the missing module. | Do not advertise AIDEFEND. |
| 1.8.10 | **Memory-component failure annotator** | **UNVERIFIED — module missing** | `src/compliance/memory-component-failure-annotator.js` **does not exist**; 13 test failures. | Do not advertise. |
| 1.8.11 | A mapping is not a certification | **IMPLEMENTED (documentary)** | `src/compliance/framework-mapper.js:373,478` annotate exclusions honestly | This must be stated on every compliance surface: a control mapping supports preparation; it is not an audit opinion and not certification. |

### 1.9 Training and feedback (v2)

| # | Capability | State | Evidence | Notes |
|---|---|---|---|---|
| 1.9.1 | RL-pipeline bridge into the coordinator | **PARTIALLY IMPLEMENTED** | `src/coordinator/rl-pipeline-bridge-integration.js` — lazy-loads an external `rl-pipeline` library from `config.rlPipeline.path` | The bridge is a shim; the library is external. |
| 1.9.2 | DPO training data from preference-pair disagreement | **ROADMAP** | `README.md:11-13` — "(v2) Every preference-pair disagreement becomes DPO training data"; `README.md:12` — "The v2 pipeline (Phase 1 → 5) is in active development" | Not shipped. Present as in development, never as a feature. |
| 1.9.3 | Outcome filter with named rules | **PARTIALLY IMPLEMENTED** | `src/trainer/outcome-filter.js:168` — accepts `noop`, `min_score_gap`, `tag_match`, `azr_result`. The `security_sensitive_diff` rule is tested but not implemented (7 failures). | |
| 1.9.4 | PRM cache model labelling | **IMPLEMENTED** | `CHANGELOG.md:139` — 515,327 rows backfilled from `primary-model` | |

### 1.10 Infrastructure

| # | Capability | State | Evidence | Notes |
|---|---|---|---|---|
| 1.10.1 | REST API service | **IMPLEMENTED** | `src/api/index.js` — the `npm start` entrypoint | |
| 1.10.2 | OpenAPI specification | **IMPLEMENTED** | `docs/openapi.yaml` | Shipped in the npm tarball. |
| 1.10.3 | Docker images and compose topology | **IMPLEMENTED** | `Dockerfile`, `Dockerfile.gateway`, `Dockerfile.coordinator`, `Dockerfile.training`, `docker-compose.yml`, `docker-compose.coordinator.yml` | |
| 1.10.4 | Kubernetes manifest | **IMPLEMENTED** | `k8s-deployment.yaml` | |
| 1.10.5 | Nginx configuration | **IMPLEMENTED** | `nginx.conf` | |
| 1.10.6 | React operator UI | **IMPLEMENTED** | `src/ui/` (React + MUI) | Served by nginx in compose (`aware-2-ui`, `CHANGELOG.md:140`). |
| 1.10.7 | Threat model and disclosure records | **IMPLEMENTED** | `threats/`, `src/disclosure/` | |
| 1.10.8 | Published on npm | **IMPLEMENTED** | `@goodciso/aware@2.12.3`, `npm view` confirms `latest = 2.12.3` | Apache-2.0. Tarball hygiene was fixed in 2.12.1 (`CHANGELOG.md:23,27-28`). |
| 1.10.9 | Public GitHub repository | **IMPLEMENTED** | `github.com/GoodCISO/aware` | |
| 1.10.10 | **Production deployment evidence** | **UNVERIFIED** | No customer deployment reference, no production URL, no deployment attestation found in the repo | Do not claim enterprise deployments. |

### 1.11 Test posture

| # | Capability | State | Evidence | Notes |
|---|---|---|---|---|
| 1.11.1 | Unit suite exists and runs | **IMPLEMENTED** | `npm test` → `node --test 'test/unit/**/*.test.js'` | 121 test files. |
| 1.11.2 | Unit suite passes | **PARTIALLY IMPLEMENTED** | Measured 2026-11-16: **984 pass / 184 fail** | The 184 failures are **not** random. They collapse into 4 causes: 33 × missing `src/compliance/aidefend-mapper.js`; 13 × missing `src/compliance/memory-component-failure-annotator.js`; 7 × unimplemented `security_sensitive_diff` outcome rule; 2 × `ADMISSIBLE_SUB_CONSTRAINTS` absent from `src/server.js`; plus 1 each for a missing function and a server-not-ready integration case. **97% of the failure mass is two missing modules.** |
| 1.11.3 | Integration suite | **IMPLEMENTED** | `npm run test:integration` → `test/integration/**/*.test.js` | |
| 1.11.4 | Standards suites | **IMPLEMENTED** | `test:ast10-standards`, `test:apts-standards`, `test:donkai`, `test:llm-top-10-standards` | |
| 1.11.5 | Playwright browser tests | **IMPLEMENTED** | `playwright.config.js` | |
| 1.11.6 | Security audits on record | **IMPLEMENTED** | `security-audit-report.txt`, `security-audit-gitleaks.json`, `security-audit-npm-audit.json`, `security-audit-trivy.json` | Gitleaks history includes a prior incident where the npm tarball shipped 27 unreviewed files (`CHANGELOG.md:27`) — no credentials, but the process failed. |
| 1.11.7 | Vulnerability disclosure policy | **IMPLEMENTED** | `SECURITY.md` | |

### 1.12 Version maturity

| # | Capability | State | Evidence | Notes |
|---|---|---|---|---|
| 1.12.1 | Current published version | **IMPLEMENTED** | `@goodciso/aware@2.12.3`, published 2026-11-12 (`CHANGELOG.md:48`) | |
| 1.12.2 | v1 still maintained in parallel | **IMPLEMENTED** | `README.md:9-11` — v1.0.0 runs on its own port set (3000, 3001) | |
| 1.12.3 | **v2 is production-ready** | **PARTIALLY IMPLEMENTED** | `README.md:9-11` — "The v2 pipeline (Phase 1 → 5) is in **active development**" | v2 core (identity, policy engine, audit chain, compliance mapping) is real and running. The v2 *pipeline* (training/RL) is not finished. |

---

## 2. Claims we must not make

These are the specific claims to strike from all copy, diagrams and sales material. Each was checked against the source.

| # | Do not claim | Why | Safe alternative |
|---|---|---|---|
| 2.1 | "Commit Guard" as a product capability | Nothing matching exists in the source (1.7.1) | "A Commit Guard is on the roadmap." |
| 2.2 | "Atomic commit" / "atomically commits actions" | No atomicity machinery (1.7.2) | "Policy evaluation precedes the action." |
| 2.3 | "Target-side enforcement" | No target-side protocol (1.7.3) | "Enforced centrally at the gateway." |
| 2.4 | "Independent execution verification" | No receipt or verifier (1.7.4) | "Decisions are recorded in a verifiable audit chain." |
| 2.5 | "Revocation cascades to child agents" | Explicitly retracted in 2.12.2 (1.4.4) | "Revoking an agent invalidates its credentials immediately." |
| 2.6 | "Cryptographic identity that cannot be faked" | Identity is a shared secret + symmetric JWT (1.1.8) | "Every agent has a non-human identity with a hashed, revocable credential." |
| 2.7 | "X.509 / Ed25519 / SPIFFE agent identity" | No asymmetric crypto (1.1.8) | Omit, or state as a design goal. |
| 2.8 | "Pheromone-based routing" | Router is not wired (1.5.5) | "Blast-radius scoring on revocation." |
| 2.9 | "Eight compliance frameworks" | Seven are registered (1.8.1) | "Seven frameworks." |
| 2.10 | "Full CSA AICM coverage" | 184 of 243 (1.8.2, 1.8.3) | "184 of 243 AICM v1 controls, across all 18 domains." |
| 2.11 | "AIDEFEND coverage" | Module missing (1.8.9) | Omit. |
| 2.12 | "Hierarchical delegation" / "agent hierarchy" | No delegation graph (1.5.1) | Omit, or mark as roadmap. |
| 2.13 | "T4 agents act fully autonomously under enforcement" | The engine does not branch on tier (1.2.4) | "Tiers classify and promote an agent's autonomy posture; the engine enforces by tool risk and data tier." |
| 2.14 | "Distributed consensus" as a production guarantee | Leader election is simulation-grade (1.4.6); `RevocationService` is "pending Raft setup" (1.4.7) | "Raft-based propagation components, integrated with the running service." |
| 2.15 | "SOC 2 certified" / "ISO certified" / "penetration tested by an independent firm" | No documentary evidence in the repo | "Prepares you for audit; the auditor remains independent." |
| 2.16 | Customer names, logos, testimonials, user counts, revenue, GitHub activity | No evidence; the existing site's two testimonials are anonymous and unverifiable | Remove. |
| 2.17 | "Independent certification, without the consultant markup" (live homepage, `index.html`) | A guarantee about an independent body's decision, which no software can make | "Prepares you for the audit. The auditor stays independent." |
| 2.18 | "We went from zero documentation to ISO 27001 in 9 weeks" / "FCA review in 6 weeks → hours" (live homepage testimonials) | Unverifiable and testimonial-shaped | Remove. Replace with a capability-led section. |
| 2.19 | "£50K+ / 3–6 month consultancy → ~8 weeks" (`llms.txt:4`) | A cost-saving claim with no evidence | Omit, or mark as an estimate with stated assumptions. |
| 2.20 | "Replaces the compliance consultant" (live `h1`) | A promise about an outcome the product cannot guarantee | "Automates the evidence work an audit demands." |

---

## 3. Claims we can make with confidence

Each of these is directly supported by the evidence cited above.

1. **Deny-by-default policy engine.** Every tool call is evaluated; unknown or high-risk tools are denied even with no matching policy (`src/policies/engine.js:22,100-110`).
2. **Policy decisions are explicit.** `ALLOW`, `DENY`, `AUDIT` or `NO_POLICY`, with a reason string (`:12-17`).
3. **Policies reload without a restart** (`/api/policies/hot`).
4. **Every agent has a non-human identity with a hashed, rotatable, revocable credential** (`src/api/models/Agent.js`).
5. **Revocation takes effect on the credential, immediately**, and is recorded (`src/kill-switch/revocation-service.js`).
6. **The audit trail is a hash chain**, exportable so a third party can recompute it (`src/disclosure/disclosure-record.js`).
7. **Failure outcomes are recorded**, so the chain evidences completeness, not just successes (`CHANGELOG.md:138`).
8. **Seven compliance frameworks, 184 AICM v1 controls across all 18 domains** (`framework-mapper.js`, `aicm-v1-catalog.js`).
9. **MITRE ATLAS v2026.06 technique mapping** (`atlas-mapper.js`).
10. **A working operator UI** (React + MUI, `src/ui/`).
11. **Apache-2.0, published on npm, source on GitHub** (`@goodciso/aware@2.12.3`).
12. **Containers and Kubernetes manifests ship** (Dockerfiles, compose, `k8s-deployment.yaml`).

---

## 4. Marketing language rules derived from this register

1. Every product page states the implementation state of the capability it describes. Where a page describes a roadmap capability, it says **"Roadmap"** in the same visual treatment as the capability name — not in a footnote.
2. No page implies AWARE verifies execution. Where execution assurance is discussed, the site explains the difference between **authorising**, **approving**, **revalidating**, **committing** and **verifying**, and states which of those AWARE does today.
3. Compliance content says "mapping", never "compliance achieved" or "certified", and names the independent auditor explicitly as the one who decides.
4. No fabricated testimonials, customers, logos, metrics or team credentials.
5. The interactive playground labels every decision it renders as **simulated**, using the real engine's semantics and the real decision vocabulary, but never implying a live environment.
6. Any number on a page traces to this register or to a test run. No number is approximated for effect.

---

## 5. Open engineering debt (relevant to what we publish)

| Item | Evidence | Effect on marketing |
|---|---|---|
| `src/compliance/aidefend-mapper.js` missing | 33 test failures | AIDEFEND cannot be claimed |
| `src/compliance/memory-component-failure-annotator.js` missing | 13 test failures | Cannot be claimed |
| `security_sensitive_diff` outcome rule not implemented | 7 test failures | Cannot be claimed |
| `ADMISSIBLE_SUB_CONSTRAINTS` absent from `src/server.js` | 2 test failures | Cannot be claimed |
| Credential rotation stores `credentials.previous` but never consults it | `CHANGELOG.md:64` | Rotation is a cutover, not a grace period. Do not describe dual-valid credentials. |
| `src/coordinator/http-server.js.bak` in the working tree | `CHANGELOG.md:99` | Not published; excluded from the tarball whitelist. |
