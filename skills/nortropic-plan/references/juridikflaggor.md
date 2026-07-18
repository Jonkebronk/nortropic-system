# Juridikflaggregistret — §7.7:s fasta flagglista

Plannern sätter flaggor ur research i briefens §7. Registret är fast; stewarden föreslår tillägg/statusändringar via vanliga förslagsflödet. qa-launchers legal-grind (Gate 6) läser §7-flaggorna (via `content/profile.ts` i byggrepot) och rapporterar per aktiv flaggas kravlista — juridik förblir human-only, alltid.

**Status per flagga:** `hanterad (modul finns)` | `ohanterad (modul saknas)` | `scope-nej`.

**Flödena:**
- **Ohanterad flagga** → öppen fråga i briefen, ordagrant: "kräver juridikmodul X som inte finns — beslut vid nod 3: bygg modulen (offereras som eget arbete) eller tacka nej."
- **Scope-nej-flagga** → briefen rekommenderar hänvisning.
- **Ring 2-principen:** en modul byggs först när första sådana kunden säger ja — efterfrågan före bygge.

## Flaggorna

| Flagga | Status | Innebörd / modulkrav |
|---|---|---|
| **hälsa/kropp/medicin-närhet** | `ohanterad (modul saknas)` | Kräver modul: patientsäkerhetslagens gränser + marknadsföringslagens beviskrav på hälsopåståenden + friskrivning + subjektiv inramning ("många upplever..." — aldrig utfallslöften) |
| **livsmedel** | `ohanterad (modul saknas)` | Livsmedelsinformation, allergener, lokala tillstånd |
| **finans/försäkring** | `ohanterad (modul saknas)` | Tillståndskrav (FI), rådgivningsgränser, riskinformation |
| **barn som primär målgrupp** | `ohanterad (modul saknas)` | Skärpt marknadsföringsregim, samtyckesfrågor |
| **alkohol/tobak** | `ohanterad (modul saknas)` | Marknadsföringsförbud/-begränsningar |
| **e-handel/distansavtal** | `scope-nej` | Utanför scope: bygg skyltfönster, hänvisa handeln till Shopify/motsvarande. Distansavtalslagen + ångerrätt + betalflöden hör hemma i en handelsplattform, inte i en statisk sajt |
| **bokning/inloggning/medlemsdata** | `hanterad (modul finns)` — endast i extern form | Stateful behov. Default: extern bokningstjänst (Bokadirekt/Calendly/Cal.com hostat) integrerad statiskt via länk/embed, med `gate1Test` = "boka-flödet når extern bokning och fungerar". EGET tillstånd med databas/auth är utanför pipelinen — offereras separat som systemutveckling med eget drift-SLA, aldrig som Nortropic-sajt |
| **ingen flagga** | `hanterad (modul finns)` | Bas-juridiken räcker: Integritetspolicy, cookie-läge, Företagsuppgifter, claims-verifierbarhet (Gate 6-basen i nortropic-prelaunch) |

Vid denna leverans (v13) är endast basen `hanterad` — hälsa-modulen (och övriga) byggs först när första sådana kunden säger ja.
