---
name: nortropic-antislop
description: Anti-AI-slop quality gate for Nortropic local service websites. Use when reviewing, scoring, or fixing the design or copy of a Swedish local service business site (plumber, electrician, cleaner, HVAC, locksmith...). Detects generic AI patterns, weak CTAs, SaaS-style design that does not serve lead generation, and forbidden copy phrases. Trigger with /nortropic-antislop [file-or-dir], or when the user says "slop check", "does this look AI-generated", "kvalitetsgranska", or before any Nortropic design review.
argument-hint: "[file-or-dir]"
---

# Nortropic Anti-Slop Quality Gate

You are auditing a website for a **Swedish local service business**. The site has exactly one job: make a stressed homeowner **call the number or send a quote request**. Every check below exists to serve that job. If `$ARGUMENTS` names a file or directory, audit that scope; otherwise audit the whole project.

## The North Star

A local service site is NOT a SaaS landing page, NOT a portfolio, NOT a brand experience. The visitor has a broken pipe, a dead outlet, or a dirty office. They are comparing 3 tabs in 30 seconds on a phone. The site wins by being **instantly credible and instantly callable**.

Judge every element by one question: *does this get a stressed person in Sverige to ring or begära offert faster?* If not, it is decoration — and decoration that looks AI-generated actively costs trust.

## Audit Process

1. Read the scoped files (pages first, then components, then copy/content files).
2. Run the **Visual Slop Checklist** (below) against layout/components.
3. Run the **Copy Blocklist** (`references/copy-blocklist.md`) against all Swedish text.
4. Score with the rubric. Report violations with file:line, severity, and a concrete fix.
5. For deep scoring or fixes beyond this gate, escalate on-demand (see Escalation).

## Visual Slop Checklist (summary — full version in `references/design-checklist.md`)

**Instant-fail patterns (each −15 points):**
- Phone number not visible in the header on mobile viewport
- No CTA ("Ring oss" / "Få offert") above the fold
- Hero built on a generic gradient (purple/indigo/teal blends) with floating blobs or grid-dot backgrounds
- Emoji used as feature icons, or the same lucide icon set laid out in the classic 3-column "features" grid with one-word titles
- Quote form with more than 5 fields, or hidden behind a modal

**Slop signals (each −5 points):**
- Glassmorphism cards, neon glows, or dark-mode-first design (tradespeople sites are viewed in daylight, outdoors, on phones)
- Stock photos of American call-center agents with headsets, or obviously AI-generated people
- Centered everything: centered hero, centered paragraphs, centered feature grid — no visual hierarchy
- Animated counters ("500+ nöjda kunder" counting up), typewriter headlines, scroll-hijacking
- Testimonial cards with perfect 5-star ratings, stocky avatars, and no verifiable name/ort
- Section order copied from SaaS templates: Hero → Logos → Features → Pricing → FAQ → CTA
- Identical border-radius + shadow on every single card (template smell)
- Footer with 4 columns of links a 5-page site does not have

**What a GOOD Nortropic site looks like:**
- Sticky header: logo left, **synligt telefonnummer + ring-knapp right** (tel: link, thumb-reachable)
- Hero: pain-point headline in Swedish ("Stopp i avloppet? Vi är där inom 2 timmar"), sub-line with service area, one primary CTA + phone, trust row (Google-betyg, år i branschen, certifikat) directly under
- Floating call button on mobile (bottom-right, 56px+ touch target)
- Real photos: the team, the vans, actual jobs (before/after). Imperfect beats perfect.
- Trust signals near every CTA: F-skatt, försäkring, garantier, riktiga omdömen med namn och ort
- Service pages that answer the visitor's actual situation, ending in the same CTA pair
- Warm, professional palette anchored by the client's bransch per briefens §5 (t.ex. blue = VVS/rör, green = städ/miljö, amber/orange = el/energi) — never the default indigo-500

## Copy Blocklist (summary — full list in `references/copy-blocklist.md`)

Forbidden AI-slop phrases, Swedish and English. Each occurrence −3 points:
- "Vi förstår att...", "I dagens digitala värld", "Oavsett om du... eller...", "Vi finns här för dig", "skräddarsydda lösningar", "helhetslösningar", "ta din X till nästa nivå"
- "Unlock", "Elevate", "Seamless", "Empower", "Effortless", "state-of-the-art", em-dash chains, rule-of-three adjective triplets ("snabbt, smidigt och säkert" as filler)
- Generic superlatives without proof ("marknadsledande", "bäst i branschen")

**Good Nortropic copy** is concrete, calm, direct Swedish — concrete services, concrete tider, concrete areas ("Vi rensar avlopp i hela Täby — oftast samma dag"). Short sentences. Numbers and place names beat adjectives. These universal principles apply to every bransch; THE VOICE (adjektiv, exempelmeningar, legitimt bransch-vernacular) is defined per client in the brief's **§7 Röstregister**, and the brief's **bransch-antislop (§7.3)** applies on top of the base blocklist. §7 can never whitelist the universal sins.

## Premium-checklistan (det positiva rummet)

Blocklistan och slop-checklistan är **negativytan** — vad som inte får finnas. `references/premium-checklist.md` är **positivytan**: 8 checkbara punkter (PK-1…PK-8, tre kategorier: Taste, Substans, Upplevd kvalitet) för vad som ska finnas för premium-känsla. design-reviewer går igenom den i varje granskning och taggar fynd `[PK-n]`; content-designer refererar PK-5 (bildspråk) och PK-8 (svensk microcopy); qa-launchers mobilpass (Gate 3) prickar PK-7. Ingen egen poängskala — punkterna informerar fynd som flödar in i eval-kriterierna 1, 3, 9, 10.

## Scoring Rubric (0–100)

Start at 100, subtract per violation above, then verify the positives:

| Dimension | Max deduction if missing/weak |
|---|---|
| Phone + CTA visibility (header, hero, mobile floating) | −30 |
| Trust signals (reviews w/ names, certifikat, F-skatt, garantier) | −20 |
| Copy quality (Swedish, concrete, blocklist-clean) | −20 |
| Design distinctiveness (not template/SaaS/slop patterns) | −20 |
| Mobile-first ergonomics (thumb reach, touch targets, load feel) | −10 |

**Verdict bands:** 90–100 launch-ready · 75–89 fix the listed items · 50–74 significant rework · <50 redesign the flagged sections before any review continues.

## Escalation (on-demand skills)

> **Obs:** design-reviewer laddar dessa obligatoriskt som **designkanonen** (se agentens processteg "Ladda designkanonen") — listan här gäller direktkörningar av `/nortropic-antislop` och övriga användare av gaten.

This gate finds problems. For deeper work, invoke via the Skill tool:
- `taste` — quantified design scoring when the 0–100 number is contested
- `impeccable` — systematic polish pass to FIX what this gate flagged
- `soft-skill` — the expensive-agency fundamentals (spacing, shadows, type scale)
- `frontend-design` / `ui-ux-pro-max` — direction when a section needs redesign, not tweaks
- `emil-design-eng` — animation/interaction quality
- `web-design-guidelines` — general web craft checks

## Report Format

```
## Anti-Slop Audit: <scope>  —  Score: NN/100 (verdict band)

### Instant fails (fix before anything else)
- [file:line] finding → concrete fix

### Slop signals
- [file:line] finding → concrete fix

### Copy violations
- [file:line] "quoted phrase" → suggested rewrite (Swedish)

### What is already working
- 2–4 genuine strengths so good patterns are not "fixed" away
```

Never pad the report. If the site is clean, say so in three lines and give the score.
