---
name: nortropic-retro
description: Runs the Nortropic steward — system health audit (doctor), project retrospective, or the v15 trappan modes (vaktmastare/nattskift, gated by AUTOPILOT + docs/07-konstitution.md). Proposals land in ~/Workflow/steward-proposals/ for human approval. User-triggered only.
argument-hint: "[project-path | system | vaktmastare | nattskift]"
disable-model-invocation: true
context: fork
agent: nortropic-steward
---

Steward run requested with scope: **$ARGUMENTS**

- If the scope is `system` (or empty): run **doctor mode** on the full system, plus a cross-project retro pass over your user-scope memories and the other agents' memories for recurring patterns. When `AUTOPILOT` is `n1` or `on`, doctor closes with the vaktmastare pass.
- If the scope is `vaktmastare` or `nattskift`: run the corresponding trappan MODE from your agent body. Their own pre-checks (AUTOPILOT gate, incident file, and for nattskift the RETRO-1/verify-suite/checkpoint gates) always run first and may refuse the run — honor the refusal.
- If the scope is a project path: run **retro mode** on that project (its reports, HANDOVER.md, brief, **EVAL-RESULT.md**, git log) — compare its rubric scores against previous clients — AND a quick doctor pass (checks 1–3 only) so retros always catch mechanical breakage too.

Every retro (and system scope) includes the **mandatory Minneskuratering step** — classify each agent's memory entries and report them under the "Minneshälsa" heading in STEWARD-REPORT.md, even when memory is healthy — **and the "Obligatoriska retrosteg"** from your agent body (Bibliotekarien skill-&-MCP-inventeringen, usage-loggen, aktiva engångssteg, and retrosteg 4 **"Trappan & måtten"**: mandatory reading of `~/Workflow/AUTO-DIGEST.md` + the explicit Goodhart question about the measures themselves — docs/07-konstitution.md §B8; the human acks with a CHECKPOINT row in docs/05). STEWARD-REPORT.md ends with the mandatory **"Största hävstången"** section: the ONE change that pays most right now.

Follow your output contract exactly: STEWARD-REPORT.md + one proposal file per change in `~/Workflow/steward-proposals/<dagens datum>/`, then return the summary (proposal count, highest-risk first, healthy-is-healthy honesty). Remind the user at the end: review proposals, then tell the MAIN session which to apply — e.g. "applicera förslag 1 och 3" — and it will apply + commit them to the nortropic-system repo.

Appliceringsregeln (för huvudsessionen som applicerar): ett förslag vars **Docs-påverkan** inte är `"ingen"` appliceras alltid tillsammans med sin docs-uppdatering i SAMMA commit — aldrig separat. Varje applicerat förslag läggs dessutom som en rad i `docs/05-beslutslogg.md` (datum · beslut · motiv · commit), och `Senast verifierad mot systemet:`-raden uppdateras i varje berörd docs-fil.
