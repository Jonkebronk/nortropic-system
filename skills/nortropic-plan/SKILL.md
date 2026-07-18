---
name: nortropic-plan
description: Step 1 of the Nortropic pipeline — turns a client research.md into a complete PROJECT-BRIEF.md via the project-planner agent. User-triggered only.
argument-hint: "[path-to-research.md]"
disable-model-invocation: true
context: fork
agent: project-planner
---

Create a complete Nortropic PROJECT-BRIEF.md from the client research file: **$ARGUMENTS**

1. Read the research file at the path above. If no path was given, look for `research.md` in the current directory; if none exists, stop and say exactly which file you need. Research-filen kan innehålla den namngivna sektionen **"Designreferenser" (VALFRI)** — lista gärna egna referenser (URL + 1–3 meningars motivering per referens): de vägs in i din inhämtning tillsammans med din egen jakt, likvärdigt. Receptet om användaren vill jaga själv: 3 verkliga branschsajter (omdömesjakten: högt betyg → deras sajt → footer "Hemsida av X" → byråns portfolio), 1–2 från SiteInspire/Land-book, max 2 Dribbble-koncept. Frasen **"hoppa över inspirationsjakt"** i research.md stänger av din egna jakt (5d.2) — inget annat gör det.
2. **Run your INPUT GATE first**: verify the research contains business name, phone number, at least one service, at least one ort/service area, and a usable USP. If anything is missing, STOP and return only the numbered list of missing items — do not plan on guesses.
3. Apply your full planning process (site-architecture, seo-plan, cro on demand) and write `PROJECT-BRIEF.md` in the same directory as the research file, with all 7 sections per your system prompt. §7 Kalibreringsprofil är kalibreringskontraktet nedströms (primärhandling, röstregister, bransch-antislop, kvittolista, schema-typ, SEO-läge, juridikflaggor) — bevisregeln gäller: varje fältvärde citerar research-rad eller 5d-fynd, fält utan belägg blir öppen fråga. Steg 5d Inspirationsinhämtning körs varje plan: användarens eventuella referenser öppnas + skärmdumpas (5d.1), du jagar ALLTID 4–6 egna kandidater ur `references/inspirationskallor.md` (5d.2, budget max 6 skärmdumpade/~10 hämtningar, hoppas endast på frasen "hoppa över inspirationsjakt"), och riktningen väljs ur hela poolen likvärdigt (5d.3) — "kunde ej öppnas" vid källa som inte renderas, aldrig fabricerade observationer, read-only mot främmande sajter. Briefens §5 bär Referensöversättningen med Ursprung-kolumnen (research/planner) så användaren ser vid briefgodkännandet varifrån varje val kom. The brief must carry the Google-betyg line (value/count/review-URL, or `saknas — öppen fråga`) and, when research.md provides reviews, the structured Omdömen block to seed `content/testimonials.ts` — so verified trust data reaches stack-builder instead of becoming a TODO-FACT.
4. Return to the user: a 5-line executive summary of the brief (business, conversion goal, page count, keyword focus, design direction), the list of open questions that need the user's answers, and the reminder that the next step is `/nortropic-init <path-to-PROJECT-BRIEF.md>` once the brief is approved.

Do not create any repository or scaffold anything — this step produces the brief only.
