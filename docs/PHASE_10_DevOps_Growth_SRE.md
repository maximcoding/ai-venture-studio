# docs/PHASE_10_DevOps_Growth_SRE.md

## Phase 10 — DevOps, Growth & SRE

### Objective
Launch the factory-run product safely and keep it alive:
- reproducible deploy
- observability (logs/metrics/alerts)
- runbooks + rollback
- minimal growth loop (KPIs + first experiments)

This phase produces **ops + launch readiness**, not features.

---

## Inputs
- `artifacts/<thread_id>/docs/System_Architecture.md`
- `artifacts/<thread_id>/docs/Implementation_Notes.md`
- `artifacts/<thread_id>/docs/Security_Policy.md`
- `artifacts/<thread_id>/docs/Budget_Guardrails.md`
- Current repo state:
  - `/infra` (compose, CI, scripts)
  - `.env.example`
  - current Docker images/build steps

Where `<thread_id>` = `user_<telegram_user_id>`.

---

## Primary Outputs (per-run artifacts + repo)
### Repo outputs (checked-in)
- `/infra/deploy/` (or `/infra/` updated) contains:
  - `Dockerfile` + build args (if needed)
  - deployment script(s)
  - environment templates
  - platform notes (one target chosen)
- CI workflow updated (if needed):
  - build/publish (optional)
  - deploy (manual gate)

### Per-run artifacts (run SSOT)
- `artifacts/<thread_id>/docs/Operations_Runbook.md`
- `artifacts/<thread_id>/docs/Monitoring_Plan.md`
- `artifacts/<thread_id>/docs/Launch_Checklist.md`

---

## Step 0 — Pick Deployment Target (deterministic)
Phase 10 must choose ONE primary target for v1, based on Delivery Surface:

- **web/api/automation** → `single-vps-docker` (default)
- **mobile** → `backend-on-vps-docker` + “mobile distribution” notes (manual, not automated by factory in v1)

If the run explicitly specifies another target in Phase 4 docs, use that.

Record the choice in `Operations_Runbook.md` under `## Deployment Target`.

---

## DevOps — Reproducible Deploy (Required)

### What “reproducible” means
A clean machine with Docker can deploy by following **exact commands** from the runbook.

### Minimum deploy approach (v1 default)
Target: **single VPS + Docker Compose**.

Required repo files:
- `infra/deploy/README.md` (or runbook section) with exact steps
- `infra/deploy/docker-compose.prod.yml`
- `infra/deploy/deploy.sh` (idempotent)
- `infra/deploy/backup.sh` (DB backup)
- `infra/deploy/restore.sh` (DB restore)
- `infra/deploy/rollback.sh` (revert to last good image/tag)

### Configuration rules
- No secrets in git.
- `.env.example` covers all required variables.
- Production env is injected at deploy time (server-side `.env`).

### Build strategy (choose one)
- **Option A (simple):** build on server (`docker compose build`)
- **Option B (recommended later):** build in CI + pull versioned images

If Option B is not implemented, document Option A clearly.

### Health checks (required)
- Container healthcheck(s) in prod compose.
- App health endpoint:
  - `GET /healthz` returns OK
  - optional: `GET /readyz` for DB connectivity

---

## SRE — Monitoring, Alerts, Runbooks (Required)

### Monitoring_Plan.md must define
- **Signals**
  - Logs: errors + key events
  - Metrics: request rate, error rate, latency (if web/api), queue depth (if automation/jobs)
  - Uptime check: `/healthz`
- **Critical alerts (minimum)**
  - app down (healthz fails)
  - DB connection failures
  - high error rate (5xx spike) if HTTP surface exists
  - disk nearly full (VPS)
- **Where alerts go**
  - Telegram (preferred): bot sends “SEV” message to CEO chat
  - optional: email later

### Logging rules
- Structured logs (JSON) if possible
- No secrets in logs
- Correlation id:
  - for web/api: request id
  - for bot: message id / update id
  - for runs: `thread_id`, `run_id`

### Operations_Runbook.md must include
- **Start/stop**
- **Common incidents**
  - bot not responding
  - DB down / migrations mismatch
  - high CPU / memory
  - disk full
  - webhook/polling issues (Telegram)
- **Triage checklist**
  - what to check first (one screenful)
- **Rollback**
  - exact command
  - what gets rolled back (app image), what does NOT (DB unless restore)
- **Backup/restore**
  - exact commands
  - retention policy (e.g., daily snapshots, 7–30 days)

### Rollback validation (required)
Perform at least once in a controlled way:
- deploy v1 tag
- deploy v1+1 tag
- rollback to v1 tag
Record proof in runbook:
- timestamp
- commands run
- result

---

## Growth — Launch Readiness (Minimal, Required)

### Launch_Checklist.md must contain
#### 1) Preconditions
- Phase 9 approved (guardrails + secrets + security gates)
- smoke test command passes
- monitoring enabled
- rollback tested

#### 2) Launch steps (exact)
- deploy command(s)
- verify health
- verify primary user flow (one scripted checklist)
- enable “announce” message (Telegram bot post / landing page update)

#### 3) KPIs (pick a minimal set)
For v1 choose 3–5, based on delivery surface:
- Activation rate
- Day-1 retention (or “return within 24h”)
- Conversion (free → paid) if monetized
- Error-free sessions / crash-free rate
- Time-to-value (first successful run/flow)

#### 4) First experiments (1–3 max)
- onboarding copy A/B (manual)
- pricing page copy variants
- short acquisition channels list (where to post / who to contact)

No “creative generation pipeline” in v1. Just a plan.

---

## Telegram Delivery & Control
At Phase 10 completion, bot sends:
- 10–15 line summary:
  - deployment target
  - deploy command
  - monitoring/alerts summary
  - rollback command
  - KPIs chosen
Buttons:
- [✅ GO TO DEPLOY]
- [📄 VIEW RUNBOOK]
- [📈 VIEW HEALTH] (shows last health snapshot / latest alerts)
- [🔙 TIME MACHINE]

### GO TO DEPLOY behavior (v1)
- Runs deploy script OR prints the exact commands (if no remote exec is implemented yet).
- If remote execution exists, it must be behind Phase 9 budget approval gate.

---

## DoD Checklist (Approval Gate)
- [ ] Deploy is reproducible from a clean machine (exact commands documented)
- [ ] `/healthz` exists and is used by healthchecks
- [ ] Monitoring plan exists with at least 3 critical alerts
- [ ] Operations runbook exists with triage + backup + rollback
- [ ] Rollback was executed at least once and recorded
- [ ] Launch checklist exists with KPIs + first experiments

---

## Notes / Scope Limits
- “Full SRE platform” is out of scope for v1.
- “Auto marketing” is out of scope for v1.
- Keep it small, deterministic, and operable.