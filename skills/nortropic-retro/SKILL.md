---
name: nortropic-retro
description: Runs the Nortropic steward — system health audit (doctor) and/or project retrospective. Proposals land in ~/Workflow/steward-proposals/ for human approval. User-triggered only.
argument-hint: "[project-path | system]"
disable-model-invocation: true
context: fork
agent: nortropic-steward
---

Steward run requested with scope: **$ARGUMENTS**

- If the scope is `system` (or empty): run **doctor mode** on the full system, plus a cross-project retro pass over your user-scope memories and the other agents' memories for recurring patterns.
- If the scope is a project path: run **retro mode** on that project (its reports, HANDOVER.md, brief, **EVAL-RESULT.md**, git log) — compare its rubric scores against previous clients — AND a quick doctor pass (checks 1–3 only) so retros always catch mechanical breakage too.

Follow your output contract exactly: STEWARD-REPORT.md + one proposal file per change in `~/Workflow/steward-proposals/<dagens datum>/`, then return the summary (proposal count, highest-risk first, healthy-is-healthy honesty). Remind the user at the end: review proposals, then tell the MAIN session which to apply — e.g. "applicera förslag 1 och 3" — and it will apply + commit them to the nortropic-system repo.
