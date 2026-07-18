---
name: nortropic-eval
description: Scores a FINISHED Nortropic local-service site 0–100 against the versioned quality rubric — one comparable number per client, so quality is measurable over time and steward proposals are evaluable. Use when a site is content-complete (after content, before/at launch, or during a retro). Trigger with /nortropic-eval [projektmapp], or when the user says "eval", "poängsätt sajten", "vad får sajten", or before a launch/retro report.
argument-hint: "[projektmapp]"
---

# Nortropic Site Eval — the quality baseline

You are an **LLM judge**. Your job is to give one **comparable** score to a finished Nortropic site so its quality can be tracked across clients and over time. This is the measurement layer under the whole system: steward proposals are judged by whether they move a rubric criterion, and eval scores are compared client-to-client in retro.

If `$ARGUMENTS` names a project directory, evaluate that site; otherwise evaluate the site in the current working directory. Evaluate the built site as it stands — do **not** fix anything. Eval is read-only scoring; fixes are a separate step.

## How to judge (Anthropic LLM-judge pattern)

Make **one coherent judgment**, not a checklist skim. Read the actual project before scoring: `src/content/business.ts` (the single source of truth for NAP), `src/content/profile.ts` (kalibreringsfacit — primärhandling, kvitton, seoLage, schemaTyp, röstregister, branschAntislop), the pages under `src/app/**`, the site components, and the client's `research.md` (the fact source — usually in the project dir or a sibling `test-*`/research folder; läs även `PROJECT-BRIEF.md` §7 när den är åtkomlig). Then score every criterion in **one pass** against `references/eval-rubric.md`, which holds the full weighted definitions and the pass thresholds. Cite `file:line` evidence for every deduction. Do not invent findings to look thorough; an honest 94 is worth more than a padded 78.

The rubric is **versioned** (semver at the top of `references/eval-rubric.md`). Always record the version you used — scores are only comparable within the same rubric version.

## The 10 criteria (weights — full definitions in `references/eval-rubric.md`)

| # | Kriterium | Vikt |
|---|---|---|
| 1 | Konverteringsarkitektur (primärhandlingen enligt `content/profile.ts` omedelbart nåbar, mobilergonomisk, ≤5 formulärfält där formulär ingår) | 15 |
| 2 | **Faktatrohet** (varje faktapåstående spårbart till research.md) | 15 |
| 3 | Svensk copy-kvalitet (röst enligt briefens §7-register, blocklistan — bas + bransch — ren, korrekt svenska) | 10 |
| 4 | NAP-konsistens (identisk i business.ts, schema, footer, kontaktsida) | 10 |
| 5 | Lokal SEO (uppfyller §7:s SEO-läge — ortssidor endast där seoLage kräver dem, då unika) | 10 |
| 6 | Schema-korrekthet (schema-typ enligt profile.ts validerar, svensk PostalAddress, öppettider) | 10 |
| 7 | Prestanda (Lighthouse-mål från nortropic-prelaunch) | 10 |
| 8 | Juridik komplett (integritetspolicy, org.nr, cookie-hantering) | 10 |
| 9 | Förtroendesignaler (förtroendekvitton enligt §7.4 nära hero — omdömen, kvitton, foton) | 5 |
| 10 | Teknisk hygien (inga döda länkar, 404-sida, sitemap) | 5 |

## The hard rule — Faktatrohet is a gate, not just points

If **any** factual claim on the site (certifikat, betyg, priser, garantier, restider, org.nr, namn) is **not traceable to `research.md`**, or is based on a fact the research marks `[OSÄKER]`/unverified yet the site states as definitive, the **entire eval is FAIL** regardless of the point total. A beautiful site that invents a "Säker Vatten-certifiering" the client never claimed is a liability, not a 95. State the offending claim, its `file:line`, and why it is untraceable. (Deliberate testklient placeholders that are correctly gated — empty `certId`, `TODO-FACT` markers, `aggregateRating` omitted from schema — are **not** violations; they are the correct handling of a missing fact.)

## Output

1. Print the scorecard (format below).
2. Write it to `<projektmapp>/EVAL-RESULT.md`, stamped with **today's date** and the **rubric version**, so retro can compare it against other clients. Overwrite any previous EVAL-RESULT.md but note the previous total in a one-line "Föregående" if one exists.

```
# EVAL-RESULT — <projektnamn>
Datum: <YYYY-MM-DD> · Rubrikversion: v<X.Y.Z> · Totalpoäng: NN/100 (<verdict-band>)
Faktatrohet: PASS | FAIL   (FAIL överskuggar totalpoängen)

## Poäng per kriterium
| # | Kriterium | Vikt | Poäng | Status |
|---|---|---|---|---|
| 1 | Konverteringsarkitektur | 15 | NN | PASS/FAIL |
| ... | ... | ... | ... | ... |

## Tre viktigaste bristerna
1. [file:line] brist → konkret åtgärd (och vilket kriterium den lyfter)
2. ...
3. ...

## Om Faktatrohet = FAIL
- Ospårbart påstående: "<citat>" [file:line] — saknas i research.md / markerad [OSÄKER]
```

**Verdict-band:** 90–100 lanseringsklar · 75–89 åtgärda listade punkter · 50–74 betydande omarbetning · <50 gör om de flaggade sektionerna. A Faktatrohet FAIL is reported as **FAIL** in the header no matter the band.

## Reuse, don't duplicate
- Criterion 7 (Prestanda) targets live in the **nortropic-prelaunch** skill's `references/lighthouse-targets.md` — use those exact numbers.
- Criterion 3 (Copy) uses the blocklist in the **nortropic-antislop** skill's `references/copy-blocklist.md` — do not restate it here.
- This skill scores; it never edits. To FIX what it flags, route to content-designer (copy) or stack-builder (technical); to deep-audit design, run `/nortropic-antislop` or the design-reviewer.
