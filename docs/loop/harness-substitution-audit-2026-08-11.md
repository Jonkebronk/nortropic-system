# NORTROPIC — Harness Substitution Audit 2026-08-11

**Status:** Owner-decision candidate / architecture audit. Ingen repo-mutation är gjord av detta dokument.

**Syfte:** Minimera Nortropic till en provider-neutral deterministic trust kernel runt moderna coding-agent harnesses (Codex, Claude Code/Agent SDK m.fl.) i stället för att återimplementera deras session-, context-, retry- och reasoninglager.

## 1. Sammanfattat beslut

Nortropic ska inte konkurrera med Claude Code, Codex eller framtida agentharnesses om att vara den smartaste agent-loopen.

Målformen är:

```text
AGENTIC EXECUTION LAYER
  Claude / Codex / framtida provider
  planner · builder · reviewer · remediation · context · tool loop
                |
                v
NORTROPIC TRUST KERNEL
  task contract · allowed_write · candidate identity · policy
  frozen verifier · task gate · attestation · stale/invalidation
  lease/fencing · recovery · promotion eligibility · authoritative transition
                |
                v
authoritative main
```

Designregel:

> Fri hjärna. Hårda dörrar.

Modellen får stor frihet **inom** en task. Nortropic är deterministisk **mellan** trust states.

## 2. Omvärldsbevakning — principer som återkommer

### OpenAI / Codex

OpenAI beskriver sin agent-first modell som "Humans steer. Agents execute" och lägger vikten på agentvänliga repositories, automatiserade tester, mekaniska arkitekturregler och feedback loops snarare än mänsklig mikrostyrning. I Symphony flyttas fokus från sessioner/PR:er till tasks; varje task får ett isolerat workspace, reconciliation sker före dispatch, och orchestration hålls minimal. OpenAI skriver också att agenter bör få objectives snarare än överdetaljerade state-machine transitions när modellen själv kan resonera.

### Anthropic

Anthropic rekommenderar enkla, komponerbara harnesses och varnar uttryckligen för att harness-komponenter kodar antaganden om vad modellen inte kan göra — antaganden som blir stale när modeller förbättras. Managed Agents separerar session, harness och sandbox bakom stabila interfaces. För coding evals betonar Anthropic deterministic graders, end-state i verklig miljö och isolerade testmiljöer; agentens utsaga är inte utfallet. Anthropic visar också att separat generator/evaluator hjälper mot self-evaluation bias, men evaluatorn är fortfarande en LLM och därför inte root of trust. För säkerhet betonar de containment/sandboxing framför approval-trötthet.

### Stora open-source harnesses

- SWE-agent fokuserar på Agent-Computer Interface (ACI): bra verktyg och tydliga interfaces till modellen.
- Aider använder Git som naturlig kandidat/historik och kör lint/tests automatiskt runt agentens edits.
- OpenHands separerar agent/controller/runtime/sandbox och använder event stream som kommunikationsryggrad.
- CLI-Anything bygger provider-neutrala, agent-native CLI:er med strukturerad JSON och deterministiskt beteende.

Gemensam riktning: **agenten får resonera; omgivningen gör state, verktyg, verifiering och isolation tydliga och mekaniska.**

## 3. Klassificeringsregler

- **KEEP** — deterministic trust/authority som modellen inte får själv-certifiera.
- **THIN** — behåll semantiken/interface, men ersätt egen implementation med provider-/standardprimitiv där möjligt.
- **REPLACE** — agent-harness-ansvar som Claude/Codex redan bör äga; Nortropic behåller högst en adapter/validator.
- **ABSORB** — separat komponent behövs inte som långsiktig modul; ansvaret absorberas i kernel/orchestrator/adapter.
- **DEFER** — värdefullt men ska inte byggas som egen motor innan kärnan/adaptrarna är stabila.

## 4. Audit av h-001–h-017

| Del | Klass | Slutform | Motiv |
|---|---|---|---|
| h-001 state/eventlog | **KEEP + THIN** | Minimal authoritative coordination ledger; observability separeras | Claim/run-state behövs mekaniskt, men ska inte duplicera S5 eller provider-sessionlogg. Doneness kommer fortsatt ur attest. |
| h-002 verifier/register | **KEEP** | Trust-kernel | Hash-/path-bunden verifieraridentitet och pre-task judge är kärnan i att agenten inte dömer sig själv. |
| h-003 attestation/stale | **KEEP** | Trust-kernel | Binder verdict till candidate identity; stale/invalidation kan inte delegeras till agentprosa. |
| h-004 lease/fencing | **KEEP** | Trust-kernel | Exklusivitet, generation, fencing och clean finalization är shared-state authority. |
| h-005 workspace | **THIN** | Sandbox/workspace interface | Kräv exakt base, isolation och hygiene; låt Claude/Codex/worktree/sandbox primitives göra mer av lifecycle. |
| h-006 worker/parser | **REPLACE** | `AgentProviderResult` validator | Sluta tolka fri agentprosa. Använd provider-native structured/schema output. Candidate SHA ska komma från deterministic candidate materialization, inte från agentens claim. |
| h-007 policy | **KEEP** | Trust-kernel | `allowed_write`, budgets, protected areas och diff-policy är mekanisk trust boundary. |
| h-008 envelope | **REPLACE + THIN** | Typed TaskContract/Task IR → provider adapter | Behåll canonical task data/provenance. Låt adapter rendera prompt/context; undvik ett eget stort session-envelope som duplicerar SDK-context. |
| h-009 launch/timeout | **SPLIT** | Agent launch → provider SDK; containment/G20 → KEEP | SDK bör äga session lifecycle/timeout. OS-level Seatbelt/trust-root boundary är däremot Nortropic-kärna. |
| h-010 task selection/claim | **KEEP + THIN** | Deterministic eligibility + atomic claim | Dependency/doneness/claim ska vara mekaniskt. Prioritering/concurrency kan ligga i tunn orchestrator. |
| h-011 loop | **REPLACE + THIN** | Minimal task supervisor / provider-neutral orchestrator | Session/context/retry/tool-loop ska inte återimplementeras. Orchestratorn ska koordinera tasks och kalla kernel-transitions. |
| h-012 executor | **SPLIT** | Agent edits → provider; candidate materializer → KEEP | Agenten får editera. Nortropic ska deterministiskt stage/commit/frysa candidate SHA och kontrollera clean identity. |
| h-013 breaker | **THIN** | System-level bounded retry/no-progress | Provider SDK får äga max turns/session-budget. Nortropic behåller cross-attempt circuit/no-progress/operational cap som skydd mot obegränsad resursförbrukning. |
| h-014 notification | **THIN / DEFER** | S5-event consumer | Observerande side effect, aldrig trust path. |
| h-015 recovery | **KEEP + THIN** | Reconcile Git/attest/lease/kernel facts; provider resume är hjälpmedel | Session resume är inte recovery authority. Faktisk Git/attest/lease-state avgör vad som får återupptas. |
| h-016 wiring | **ABSORB** | Integration/regression gate, inte permanent egen motor | Den historiska wiring-semantiken ska regressionstestas, men långsiktig implementation absorberas i tunn orchestrator + adapters + kernel. |
| h-017 per-task verdict | **KEEP** | Trust-kernel | Själva trusted task-specific acceptance gate. |

### Viktig migrationregel

Ingen nuvarande green gate tas bort först. En komponent får bara tunnas/ersättas genom:

1. ny adapter/kernel-contract;
2. RED/positive/negative acceptance gate;
3. implementation;
4. full regression mot gamla gates;
5. empirical run;
6. därefter kan legacy implementation markeras deprecated eller tas bort.

## 5. Audit av S2 / S4–S13 / L

| Slice | Klass | Reviderad avsikt |
|---|---|---|
| S2 h-015 recovery | **KEEP + THIN** | Reconcile kernel facts; använd provider session resume endast som optimering. |
| S4 structured feedback | **THIN** | Minimal immutable `FailureArtifact` + provider adapter. Återimplementera inte Claude/Codex context/retry-system. |
| S5 lifecycle/events | **KEEP + THIN** | Provider-neutral typed projection/event contract. Normalisera provider events; duplicera inte deras fulla sessionlogg. Aldrig scheduler/doneness authority. |
| S6 h-014 notification | **THIN** | Consumer av S5; inga egna beslut. |
| S7 promotion | **KEEP** | Trust-kernel. Exact expected-main, candidate identity, eligibility, non-force, post-read. |
| S8 merge resolution | **SPLIT** | Konfliktresonemang → agent. Resolution workspace, ny candidate identity och full re-verification → Nortropic. |
| S9 trust transition | **KEEP** | Trust-kernel/supervisor. Ny controller får inte certifiera sin egen födelse. |
| S10 Markdown intake / Task IR | **THIN** | Planner → agent. Canonical schema, provenance, validation och READY/NEEDS_SPEC contract → Nortropic. |
| S11 verifier author + challenger | **KEEP som workflow, THIN som engine** | Agentroller skriver/angriper gaten; Nortropic äger freeze, hash, registry, solvability/RED/positive/negative evidence och builder-separation. |
| S12 evaluator | **THIN + DEFER egen motor** | Använd fresh Claude/Codex reviewer/rubric adapter. Advisory blocker; aldrig root of trust. Ingen ny stor evaluatorplattform. |
| S13 read/command | **KEEP + THIN** | Typed interface/projection till kernel. Verkstadsgolvet läser härifrån; UI blir aldrig authority. |
| L empirical unattended run | **KEEP** | End-to-end falsification av hela assembled systemet i disposable state. |

## 6. Ny målarkitektur

```text
                         VERKSTADSGOLVET
                         read-only projection
                                |
                       typed read/event API
                                |
       +------------------------+-------------------------+
       |                                                  |
       v                                                  v
AGENT ORCHESTRATION / PROVIDERS                     NORTROPIC TRUST KERNEL

CodexProvider                                       TaskContract validation
ClaudeProvider                                      deterministic eligibility/claim
future providers                                    workspace/sandbox requirements
                                                    protected diff policy
planner                                             candidate materialization + SHA
builder                                             verifier registry + identity
reviewer                                            deterministic task gate
remediation                                         attestation/stale/invalidation
session/context                                     lease/fencing
provider retries                                    recovery reconciliation
                                                    promotion eligibility
                                                    guarded authoritative transition
```

### Stable provider interface

Nortropic bör introducera ungefär:

```text
AgentProvider.start(task, workspace, policy) -> session_id
AgentProvider.resume(session_id, context) -> session_id
AgentProvider.run(role, objective, schema) -> structured_result
AgentProvider.cancel(session_id)
AgentProvider.events(session_id) -> normalized references
```

Providerresultat är **evidence/input**, aldrig verdict authority.

### Stable kernel interface

```text
kernel.claim(task)
kernel.prepare_workspace(task, base)
kernel.validate_diff(task, candidate)
kernel.materialize_candidate(workspace) -> candidate_sha
kernel.verify(task, candidate_sha) -> deterministic verdict
kernel.attest(...)
kernel.invalidate(...)
kernel.reconcile(...)
kernel.promote(expected_main, candidate_sha, evidence)
```

## 7. Vad vi INTE ska göra

- Inte bygga en egen generell LLM session manager om Claude/Codex SDK redan gör det.
- Inte bygga en egen context-compaction/resume-motor.
- Inte parse:a prosa för verdict eller candidate identity.
- Inte låta tre LLM-roller räknas som tre security boundaries.
- Inte låta Verkstadsgolvet bli scheduler/doneness/trust authority.
- Inte låta provider-specific tool semantics läcka in i kernel.
- Inte ta bort gamla gates innan substitutionen är empiriskt bevisad.

## 8. Reviderad roadmap

Den gamla S2→S13-ordningen kan behållas som **capability order**, men implementationen ändras:

```text
S3/h-004  finish current authority/fencing bootstrap
  ↓
SUB-0     freeze Harness Substitution Contract (detta beslut)
  ↓
SUB-1     AgentProvider interface + Codex adapter (mot nuvarande v3)
  ↓
SUB-2     split h-009: provider launch vs G20 containment
  ↓
SUB-3     replace h-006/h-008 with structured provider result + TaskContract projection
  ↓
SUB-4     thin h-011/h-013 into task supervisor + bounded retries
  ↓
S2        recovery against kernel facts/provider session optional
  ↓
S4        minimal FailureArtifact
  ↓
S5        normalized typed events/projection
  ↓
S6        notification consumer
  ↓
S7        trusted promotion
  ↓
S8        agent reasoning + full re-verification kernel
  ↓
S9        trust transition
  ↓
S10       Task IR validator + agent planner
  ↓
S11       agent verifier author/challenger + kernel freeze
  ↓
S12       evaluator adapter, no custom evaluator engine
  ↓
S13       typed read/command projection
  ↓
L         empirical unattended run
```

## 9. Gate för varje substitution

Varje substitution måste svara på fem frågor:

1. **Vilket antagande i gamla harnessen ersätts?**
2. **Vilken providerprimitive ersätter det?**
3. **Vilken trustfunktion får absolut inte flytta till providern?**
4. **Vilken konkret felaktig implementation ska den nya gaten fälla?**
5. **Vilken legitim alternativ implementation måste också passera?**

Det sista är viktigt: en gate får inte bara passa en referensimplementation.

## 10. Beslut för den nuvarande Codex Autopilot v3

Remote main var vid auditens början fortfarande `44d525a5dd60f92fa374f18e2430ba509d4df4d0`, operating model v3-installationen. Det finns därför ett säkert fönster att lägga in substitution-authority **innan** v3 fortsätter bygga den äldre, bredare S2/S4–S13-planen.

### Rekommenderad owner transition

**Resumera inte v3 oförändrad.**

Nästa owner-pass bör:

1. lägga in detta dokument i repot som frozen owner architecture amendment;
2. deklarera att det superseder implementation-shape i `autonomous-loop-plan-v1` där planen skulle återimplementera provider-harness-funktioner;
3. bevara planens trust/effect-krav, migration dependencies och negative controls;
4. lägga in SUB-0…SUB-4 före S2/S4;
5. ändra v3 architect-instruktionen så varje framtida slice först kör substitution-testet;
6. bevara `FROZEN_OWNER_GATES_REMAIN_TRUST_AUTHORITY=YES` och no-force semantics;
7. först därefter `resume`.

## 11. Praktisk konsekvens för Verkstadsgolvet

Verkstadsgolvet ska senare visa **den verkliga Nortropic-loopen** genom S5/S13-projektionen:

```text
run → task → agent/provider → candidate → policy → gate → attestation → promotion → main
```

Dashboarden kan även visa provider-native sessionstatus (Claude/Codex) som observability, men dessa signaler får inte ersätta kernel-state.

Exempel:

```text
Codex: BUILDER running      (observability)
Candidate: abc123           (Git identity)
Policy: PASS                (kernel)
Task gate: PASS             (kernel)
Attestation: VALID          (kernel)
Promotion: pending          (kernel)
```

## 12. Källor / omvärldsbevakning

Primära källor använda i analysen:

- OpenAI — Harness engineering: leveraging Codex in an agent-first world (2026-02-11)
  https://openai.com/index/harness-engineering/
- OpenAI — An open-source spec for Codex orchestration: Symphony (2026-04-27)
  https://openai.com/index/open-source-codex-orchestration-symphony/
- Anthropic — Harness design for long-running application development (2026-03-24)
  https://www.anthropic.com/engineering/harness-design-long-running-apps
- Anthropic — Scaling Managed Agents: Decoupling the brain from the hands (2026-04-08)
  https://www.anthropic.com/engineering/managed-agents
- Anthropic — Demystifying evals for AI agents (2026-01-09)
  https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Anthropic — How we contain Claude across products (2026-05-25)
  https://www.anthropic.com/engineering/how-we-contain-claude
- SWE-agent — Agent-Computer Interface docs
  https://github.com/SWE-agent/SWE-agent/blob/main/docs/background/aci.md
- Aider — repository / Git + lint/test workflow
  https://github.com/Aider-AI/aider
- OpenHands — agent/runtime/sandbox/event-stream architecture
  https://github.com/OpenHands/OpenHands
- CLI-Anything — provider-neutral agent-native deterministic CLI methodology
  https://github.com/HKUDS/CLI-Anything

## 13. Owner-decision candidate

```text
NORTROPIC_ARCHITECTURE=PROVIDER_NEUTRAL_TRUST_KERNEL
AGENT_REASONING_OWNER=PROVIDER_HARNESS
TRUST_TRANSITION_OWNER=NORTROPIC
MODEL_OUTPUT_IS_TRUST_AUTHORITY=NO
FROZEN_OWNER_GATES_REMAIN_TRUST_AUTHORITY=YES
DETERMINISTIC_GRADERS_FIRST=YES
LLM_EVALUATOR_IS_ROOT_OF_TRUST=NO
PROVIDER_SESSION_STATE_IS_DONENESS_AUTHORITY=NO
VERKSTADSGOLVET_IS_TRUST_AUTHORITY=NO
SUBSTITUTION_BEFORE_NEW_HARNESS_COMPONENT=REQUIRED
NO_FORCE_SEMANTICS=YES
```
