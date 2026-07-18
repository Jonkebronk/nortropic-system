# Översikt — nodkartan, stoppen och artefaktkedjan

Senast verifierad mot systemet: 2026-07-18 · b68252e

Pipelinen är tolv noder. Kommandona är de tre pipeline-skillsen (som bara människan får trigga), de två workflowsen och två plattformskommandon; tre noder är rent mänskliga stopp. Modell och effort kommer ur respektive agents frontmatter — samma värden som MODELLKONTRAKTET i stewardens SYSTEM MAP och doctor #8 vaktar.

## Nodkartan

| Nod | Steg | Kommando | Utförare (modell · effort) | Artefakt |
|---|---|---|---|---|
| 1 | Research | inget — operatören skriver filen | människa | `research.md` (5 obligatoriska fält) |
| 2 | Plan | `/nortropic-plan <research.md>` | project-planner (fable · max) | `PROJECT-BRIEF.md` (6 sektioner + öppna frågor) |
| 3 | Briefgodkännande | **HÅRT STOPP** | människa | godkänd brief, besvarade frågor |
| 4 | Init | `/nortropic-init <PROJECT-BRIEF.md>` | stack-builder (opus · max) | GitHub-repo + Vercel-preview |
| 5 | Innehåll | inget eget kommando — huvudsessionen kör agenten | content-designer (opus · max) | copy, bilder, `TODO-COPY` fylld, Humanisera-passet |
| 6 | Review | `/nortropic-review` (kadens full → `--diff` → full) | workflow: design-reviewer (opus · max) + seo-optimizer (opus · high) + kodlins, 2 skeptiker per fynd | `REVIEW-REPORT.md` med commit-meta |
| 7 | Launch | `/nortropic-launch` | workflow: 7 linser över qa-launcher (opus · high), seo-optimizer (opus · high), design-reviewer (opus · max); fixar via stack-builder/seo-optimizer | verdikt, `EVAL-RESULT.md`, `HANDOVER.md`, `gbp-checklist-klient.md`, `gsc-steg-klient.md` |
| 8 | Juridik | **HÅRT STOPP** | människa | sign-off på Gate 6-fynden |
| 9 | Deploy | `/vercel:deploy` | människa/huvudsession | produktionssajt |
| 10 | Efterarbete | inget kommando — kör checklistorna | människa (+ klient) | GBP live, GSC verifierad, citations |
| 11 | Retro | `/nortropic-retro <projektmapp \| system>` | nortropic-steward (fable · max) | `STEWARD-REPORT.md` + förslag i `~/Workflow/steward-proposals/` |
| 12 | Godkänn förslag | **HÅRT STOPP** — "applicera förslag N" | människa → huvudsession | systemcommits i nortropic-system |

Källor: `skills/nortropic-plan/SKILL.md`, `skills/nortropic-init/SKILL.md`, `workflows/nortropic-review.js`, `workflows/nortropic-launch.js`, `skills/nortropic-retro/SKILL.md` samt agenternas frontmatter i `agents/`.

## De fyra hårda stoppen

Tre stopp ligger i pipelinen och ett i systemunderhållet. De är systemets styrningspunkter — allt annat får automatiseras, dessa får det inte.

**Nod 3 — briefgodkännandet.** `/nortropic-plan` slutar alltid med en exekutiv summering och en lista öppna frågor, och nästa steg körs först "once the brief is approved" (`skills/nortropic-plan/SKILL.md`, steg 4). Briefen är auktoritetsordningens topp; det som godkänns här styr bygge, copy och granskning.

**Nod 8 — juridiken.** Gate 6-fynd auto-fixas aldrig: prelaunch-skillen är "REPORT ONLY, human decides" (`skills/nortropic-prelaunch/SKILL.md`, Gate 6), qa-launcher får aldrig sätta PASS på juridik på egen auktoritet (`agents/qa-launcher.md`), och launch-workflowen filtrerar mekaniskt bort kategorin `legal` ur fixloopen och rapporterar alltid `⚠️ HUMAN REVIEW`/`HUMAN SIGN-OFF` (`workflows/nortropic-launch.js`).

**Nod 12 — förslagsgodkännandet.** Stewarden har en hård skrivpolicy: den får bara skriva i sitt eget minne, i `~/Workflow/steward-proposals/` och i STEWARD-REPORT.md — aldrig i agents/, skills/, workflows/ eller settings, inte ens för en bekräftad bugg (`agents/nortropic-steward.md`, HARD WRITE POLICY). Du läser förslagen och säger vilka som ska appliceras; huvudsessionen applicerar och committar.

**Bibliotekariens engångsgodkännanden.** Retrons bibliotekarie-steg inventerar installerade skills och MCP:er mot refererade och lämnar placerings- eller strykningsförslag (`agents/nortropic-steward.md`, Obligatoriska retrosteg 1). Besluten godkänns av användaren i session — som när `threejs-build` togs bort efter engångsinventeringen ("anvandaren godkande i session", commit `b68252e`).

## Artefaktkedjan

Allt börjar med `research.md` — kundens faktakälla och det enda dokument som faktapåståenden får spåras till. `/nortropic-plan` förädlar den till `PROJECT-BRIEF.md`, som efter godkännande blir auktoritet för allt nedströms. `/nortropic-init` materialiserar briefen som ett GitHub-repo med Vercel-preview.

Granskningarna producerar `REVIEW-REPORT.md`, vars meta-block (commit, datum, scope, mode) är det freshness-grinden i launch läser; kalibreringskörningar skriver i stället `REVIEW-REPORT-CALIBRATION.md` och rör aldrig metan (`workflows/nortropic-review.js`). Launchen producerar fyra saker: `EVAL-RESULT.md` (poängkortet — informativt, aldrig blockerande; grindarna blockerar, evalen mäter), den svenska kundöverlämningen `HANDOVER.md`, samt de klientfyllda `gbp-checklist-klient.md` och `gsc-steg-klient.md` (`workflows/nortropic-launch.js`).

Retron sluter cirkeln: `STEWARD-REPORT.md` med förslag i `~/Workflow/steward-proposals/<datum>/`, där varje applicerat förslag blir en commit i det här repot. EVAL-RESULT-filerna är kedjans minne — retron jämför varje ny klients kriteriepoäng mot tidigare klienter på samma rubrikversion (`agents/nortropic-steward.md`, MODE: retro).
