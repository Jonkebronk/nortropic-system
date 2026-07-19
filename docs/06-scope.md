# Scope — ringmodellen

Senast verifierad mot systemet: 2026-07-19 · v15 (denna commit)

Vad Nortropic bygger, vad som byggs vid efterfrågan, och vad som är nej. Principen bakom gränsen: **pipelinen levererar stateless sajter som aldrig kräver jour — det är vallgraven, inte en teknisk brist.** En sajt utan databas, inloggning eller eget tillstånd kan inte läcka persondata den inte har, går inte ner av en migrering och väcker ingen klockan tre. Kalibreringen per kund sker i briefens §7 (`agents/project-planner.md`), aldrig genom att systemet kopieras per bransch.

## Ring 1 — lokala förtroendetjänster (ÖPPEN, profilstyrd)

Svenska egenföretagare och lokala småföretag vars sajt ska driva EN primärhandling: hantverkare, frisörer, massörer*, hunddagis, blomsterhandlare, fotografer, redovisningskonsulter... Kalibreringen (primärhandling, röst, kvitton, schema, SEO-läge) genereras per kund i §7 och transporteras som `content/profile.ts`. **Bokning via extern tjänst ingår här** (Bokadirekt/Calendly/Cal.com hostat, integrerad via länk/embed) — sajten förblir stateless. *Branscher med juridikflaggor (t.ex. hälsa-närhet) kräver att flaggans modul finns — se `skills/nortropic-plan/references/juridikflaggor.md`.

## Ring 2 — nya arketyper och juridikmoduler (BYGGS VID FÖRSTA JA)

Arketyper och juridikmoduler som inte finns ännu (hälsa/kropp, livsmedel, finans, barn som målgrupp, alkohol/tobak) byggs först när första sådana kunden säger ja — efterfrågan före bygge — och **offereras som eget arbete**, inte som del av standardleveransen. Ohanterad flagga stannar alltid vid nod 3: bygg modulen eller tacka nej.

## Ring 3 — nej, med hänvisning

- **E-handel/distansavtal:** nej. Bygg skyltfönstret; hänvisa handeln till Shopify/motsvarande. Distansavtalslag, ångerrätt och betalflöden hör hemma i en handelsplattform.
- **Eget tillstånd (databas/inloggning/medlemsdata):** utanför pipelinen. Offereras som separat systemutveckling (Railway-klass infrastruktur, eget drift-SLA) eller hänvisas — aldrig som Nortropic-sajt.
- **Föreningssajter:** nej som produkt (löst gratis av laget.se/Svenskalag) — ja som kärleksprojekt, utanför affären.
