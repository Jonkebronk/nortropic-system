# nortropic-system

Senast verifierad mot systemet: 2026-07-28 · v17 (denna commit)

Nortropic är ett system av Claude Code-agenter, skills och workflows som planerar, bygger, granskar och lanserar konverterande webbplatser för svenska egenföretagare och lokala småföretag — hantverkare, frisörer, hunddagis, blomsterhandlare... (kalibrering per kund via briefens §7 Kalibreringsprofil; scope-gränserna i [docs/06-scope.md](docs/06-scope.md)). Det är byggt för en operatör som kör en sajt i taget: människan fattar besluten vid de hårda stoppen, agenterna gör arbetet däremellan. Kvaliteten mäts med en versionerad eval-rubrik, och systemet förbättrar sig självt via en steward som föreslår — och som sedan v15 dessutom självapplicerar en strikt avgränsad ändringsklass under konstitutionen ([docs/07-konstitution.md](docs/07-konstitution.md)), grindat av kill-switchen `AUTOPILOT` (default `off`); allt annat kräver mänskligt godkännande.

Det här repot är systemets källa till sanning: i drift är repo-roten operatörens `~/.claude`, och `.gitignore` är en vitlista som spårar enbart systemfilerna.

## Flödet

En kundsajt går genom tolv noder. Tre av dem är hårda stopp där en människa måste agera; resten drivs av kommandon.

| Nod | Steg | Kommando | Artefakt |
|---|---|---|---|
| 1 | Research | inget — operatören skriver `research.md` (5 obligatoriska fält) | `research.md` |
| 2 | Plan | `/nortropic-plan <research.md>` | `PROJECT-BRIEF.md` |
| 3 | Briefgodkännande | **HÅRT STOPP** — människan godkänner briefen och svarar på öppna frågor | godkänd brief |
| 4 | Init | `/nortropic-init <PROJECT-BRIEF.md>` | GitHub-repo + Vercel-preview |
| 5 | Innehåll | inget eget kommando — huvudsessionen kör agenten `content-designer` på projektet | copy + bilder, `TODO-COPY` fylld |
| 6 | Review | `/nortropic-review` (kadens: full → `--diff` → full) | `REVIEW-REPORT.md` |
| 7 | Launch | `/nortropic-launch` | verdikt, `EVAL-RESULT.md`, `HANDOVER.md` |
| 8 | Juridik | **HÅRT STOPP** — människan signerar Gate 6-fynden | juridiskt sign-off |
| 9 | Deploy | `/vercel:deploy` (efter sign-off) | produktionssajt |
| 10 | Efterarbete | inget kommando — kör `gbp-checklist-klient.md` + `gsc-steg-klient.md` | GBP live, GSC verifierad |
| 11 | Retro | `/nortropic-retro <projektmapp \| system>` | `STEWARD-REPORT.md` + förslag |
| 12 | Godkänn förslag | **HÅRT STOPP** — "applicera förslag N" till huvudsessionen | systemcommits |

Detaljerad nodkarta med agent, modell och effort per nod finns i [docs/01-oversikt.md](docs/01-oversikt.md). Sedan **v16** kan flödet köras **obemannat** för låginsatskunder: bär research-filen raden `Läge: obemannat` orkestrerar `/nortropic-autobygg` noderna 2→7 utan det mänskliga nod-3-stoppet och samlar saknade fakta/beslut i en `FINAL-TOUCHES.md` — men nod 8 (juridik) och nod 9 (deploy) förblir alltid mänskliga, och systemet publicerar aldrig själv (se [docs/00-guide.md](docs/00-guide.md)).

## Repokartan

- **`agents/`** — de 7 agenterna: `project-planner`, `stack-builder`, `content-designer`, `design-reviewer`, `seo-optimizer`, `qa-launcher`, `nortropic-steward`. Frontmattern bär modellkontraktet (model/effort) som doctor #8 vaktar.
- **`skills/`** — 10 skills: tre pipeline-steg som bara människan får trigga (`nortropic-plan`, `nortropic-init`, `nortropic-retro`, alla med `disable-model-invocation: true`) och sju kunskaps-/grindskills (`nortropic-stack`, `nortropic-antislop`, `nortropic-bild`, `nortropic-seo-lokal`, `nortropic-prelaunch`, `nortropic-eval`, `gsap-build`).
- **`workflows/`** — 5 workflows: `nortropic-review.js` (3 granskningslinser + adversariell verifiering), `nortropic-launch.js` (freshness-grind → 7 granskningslinser → fixloop ≤3 → eval → handover), `nortropic-verify-suite.js` (v15 — trappans regressionsnät: doctor → plan-torrtest + eval-stabilitet + template-spotcheck mot frysta baselines), `nortropic-autobygg.js` (v16 — obemannat kund-flöde: plan→init→content→review→grind-torrkörning med tre villkorade stopp; deployar aldrig) och `nortropic-final-touches.js` (v16 — genererar `FINAL-TOUCHES.md`, delad av autobygg + manuell efter launch).
- **`vendored-skills/`** — facit-kopior av de 9 bärande tredjepartsskillsen (designkanonen ×8 inkl. `frontend-design` + `content-humanizer`), var och en med `VENDORED.md`. Doctor #9 diffar originalen mot kopiorna.
- **`tests/`** — verify-suitens frysta baselines (`tests/fixtures/`). Människoägda per konstitutionen §A6; kandidater tas fram med `--cut-baseline`, committandet är en mänsklig handling.
- **`AUTOPILOT`** — trappans kill-switch: `off` | `n1` | `on` (saknad fil = `off`). Skrivs endast av människa; nivåbyte är en commit.
- **`CLAUDE.md`** — versionerad rot-pekare (v17), laddas varje tur: en rad som pekar till det enkla dokumentationslagret så lagren aldrig glider isär.
- **`docs/`** — dokumentationen (denna leverans). Beskriver det systemet ÄR; varje påstående ska gå att spåra till en fil.

## Dokumentation

Dokumentationen har sedan **v17** två lager: börja i det enkla, gå vidare till det avancerade.

- [docs/00-borja-har.md](docs/00-borja-har.md) — **börja här**: hela systemet förklarat från noll för en nybörjare (det enkla lagret)
- [docs/00-guide.md](docs/00-guide.md) — operatörsguiden: hur systemet används och varför det ser ut som det gör
- [docs/01-oversikt.md](docs/01-oversikt.md) — nodkartan, de tre hårda stoppen och artefaktkedjan
- [docs/02-agenter.md](docs/02-agenter.md) — de 7 agenterna: roll, modell/effort, obligatoriska steg, eskaleringar, minne
- [docs/03-regelverk.md](docs/03-regelverk.md) — systemets hårda regler med motiv och exakt källfil
- [docs/04-justeringskarta.md](docs/04-justeringskarta.md) — vad varje större designval kostar, köper och hur det skruvas
- [docs/05-beslutslogg.md](docs/05-beslutslogg.md) — beslutslogg (ADR-lite), seedad ur git-historiken och förd framåt vid varje applicerat förslag
- [docs/06-scope.md](docs/06-scope.md) — ringmodellen: vad som byggs, vad som byggs vid efterfrågan, vad som är nej med hänvisning
- [docs/07-konstitution.md](docs/07-konstitution.md) — konstitutionen: §A aldrig självmodifierbart, §B självförbättringstrappans lagar
- [docs/arkiv/](docs/arkiv/) — fryst designhistorik (`systemplan.md`), engångschecklistan för den lokala flytten (`lokal-flytt.md`) och v13-snapshotten av hantverkarprofilen (`hantverkare-profil-v13.md`)
