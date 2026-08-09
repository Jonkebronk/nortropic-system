# Att köra loopen

**Skriven 2026-08-09, UR den första verkliga körningen** — inte före den. Varje siffra
och varje utfall nedan är mätt på `premiar-1`, som körde `p-001` och `p-002` mot main
`3e781fa` och attesterade båda. En manual skriven i förväg hade varit en gissning.

Detta är driftdokumentet. Byggandet styrs av [byggplan-v3.md](byggplan-v3.md) och
[regler.md](regler.md); de rör inte den här filen.

---

## 1. Vad en körning är

`controller/loop/cli run <config.json>` går igenom backloggen task för task. Per task:
lease → claim → **försök** (workspace på oförändrad base → kuvert → brytare → utförare →
session) → parse → policy → verifierare → attestation. Faller ett försök görs det om
inuti claimet tills brytarens budget tar slut.

**Kedjan dömer tre saker:** att rapporten är välformad, att diffen håller sig inom
`allowed_write` och budgetarna, och att configens verifierare är grön mot kandidatträdet.
Den dömer **inte** om tasken blev löst — taskens eget `exit_test` körs aldrig av kedjan.
En attestation betyder *"diffen var laglig och de globala invarianterna höll"*. Den
per-task-domen fäller du, med taskens grind, innan du mergar.

## 2. Före körningen

Configen ligger utanför repot så att körningen aldrig smutsar arbetskopian. Mall och
fältförklaringar finns i [`config/README.md`](../../config/README.md).

```
mkdir -p ~/.nortropic/kor
cp config/loop-config.exempel.json ~/.nortropic/kor/min-korning.json
```

Fyll i `base_sha` (`git rev-parse HEAD`) och ett unikt `run_id`. Initiera state en gång
per körning — annars faller taskval före första varvet med
`state: … kunde inte rekonstrueras`:

```
./controller/state/cli init ~/.nortropic/kor/state
```

**`budget` måste vara strikt större än `troskel`.** Brytaren prövar budget före öppen, så
ett för snålt tak maskerar en öppen brytare permanent.

## 3. Körningen

Kör **från reporoten** — `spec` och `worker_cmd` pekar repo-relativt:

```
./controller/loop/cli run ~/.nortropic/kor/min-korning.json
```

**Terminalen är tyst medan en session arbetar.** Loopen skriver ingenting förrän ett varv
är avgjort. Mätt på premiären: tio till tjugo minuter per task, och två tasks tog ungefär
en timme. Skillnaden mellan *arbetar* och *hängd* syns inte i terminalen.

Följ den utifrån, från ett annat fönster:

```
ls ~/.nortropic/kor/workspaces/                       # vilket försök som pågår
git -C ~/.nortropic/kor/workspaces/<attempt> status --porcelain   # vad sessionen skrivit
cat ~/.nortropic/kor/state/events.jsonl               # vilka tasks som claimats
```

Attempt-katalogen heter `<run_id>-<task>-<försöksnummer>`, så `premiar-1-p-001-2` är
andra försöket på `p-001`.

## 4. Läs utfallet

```
varv 1 p-001: attesterad c721599bf09342a1d4141869be2ed911688492d3
varv 2 p-002: attesterad 95c33a34bd502575c099610c1cb06a8b04bbf98a
drain klar: 2 varv, 2 attesterade, base 95c33a34bd502575c099610c1cb06a8b04bbf98a
```

| Exitkod | Betyder | Vad du gör |
|---|---|---|
| **0** | Drain slutförd — backloggen är slut eller allt behörigt är gjort | Granska kandidaterna, för dem till main |
| **1** | Fel: trasig config, upptagen lease, brytarens anropsfel, städning som inte gick | Läs orsaken på stderr och åtgärda; ingen körning har skett |
| **3** | Rent stopp: brytaren öppnade och drainet avslutades före nästa claim | Se §6 |

Ett avbrutet varv skriver `varv N <task>: avbrutet i <steg> — <systerns klass ordagrant>`.
Steget namnger vilket led som brast: `workspace`, `kuvert`, `forsok`, `parse`, `policy`,
`verifierare`, `attest`.

## 5. Granska och föra till main

**Kandidaterna är commits utan gren.** Ingen ref pekar på dem; de nås bara via attesta-
tionsbutiken. Läs SHA:t där:

```
./controller/attest/cli ~/.nortropic/kor/attest read p-001
```

Kör **taskens egen grind** mot kandidatträdet — det är den dom kedjan inte kan fälla:

```
git worktree add --detach /tmp/kand <candidate_sha>
( cd /tmp/kand && ./verify/bin/<taskens exit_test> )
git worktree remove /tmp/kand
```

Parenteserna är avsiktliga: står du kvar i `/tmp/kand` när du river den faller `remove`
med *"Unable to read current working directory"* och lämnar en registrering efter sig
(mätt 2026-08-09). Blev det ändå fel: `git worktree prune` från reporoten.

Kedjande base gör att den SISTA attesterade kandidaten innehåller alla föregående. Är den
en ättling till main räcker en gren och en PR:

```
git branch kandidat-<run_id> <sista candidate_sha>
git push -u origin kandidat-<run_id>
gh pr create --base main --head kandidat-<run_id> --title "..." --body "..."
```

**Auto-merge är avstängt beslut.** Systemet producerar attesterade kandidater; människan
för dem till main.

> **Oreferade commits försvinner.** Ingen gren pekar på kandidaterna, så `git gc` kan
> städa bort dem när grace-perioden gått ut. Skapa grenen samma dag som körningen, eller
> acceptera att arbetet måste göras om.

## 6. När brytaren öppnat (exit 3)

Brytaren har ett tillstånd per task i `<brytare_rot>/<task-id>/tillstand.json`:

```json
{"oppen": false, "orsak": null, "forbrukat": 1, "fingerprints": {}}
```

`oppen: true` betyder att den tasken stoppar varje ny körning som når den. **Det finns
inget reset-verb** — h-015 äger återtaget och är inte byggd. Tills dess: läs orsaken,
åtgärda det som brast, och ta bort tillståndsfilen för just den tasken.

`forbrukat` är attempt-budgeten. Har den nått taket startas inget kommando för tasken,
och den förblir claimed resten av körningen.

## 7. Efter körningen — kontrollera att inget lämnades

```
git status --porcelain          # ska vara tom
git worktree list               # ska bara visa huvudträdet
ls ~/.nortropic/kor/workspaces/ # ska vara tom
ls ~/.nortropic/kor/lease/      # ska vara tom
```

Premiären lämnade allt fyra rent. Ligger ett workspace kvar rivs det med
`./controller/workspace/cli ~/.nortropic/kor/workspaces destroy <attempt>` — **destroy före
`rm -rf`**, annars blir föräldralösa poster kvar i `.git/worktrees` som fäller nästa
körnings `create`.

## 8. Kända gränser, mätta

**Leasens TTL är 180 s utan heartbeat.** Ett varv tog tio till tjugo minuter i premiären,
alltså långt över TTL:n. En andra controller kan i teorin ta över resursen mitt i en
levande körning. Kör aldrig två körningar mot samma `lease_dir` samtidigt.

**Kvoten.** En session per försök, tio till tjugo minuter var. Smoke-momentet mätte 8–20
sekunder — det var en trivial enfilsskrivning och säger ingenting om verkligt arbete.
Räkna om din kvotbudget efter den här siffran, inte den gamla.

**Timeouten.** Mallen sätter 900 s. Premiärens sessioner låg på tio till tjugo minuter, så
marginalen är tunnare än den ser ut. Höj den hellre än att låta ett halvfärdigt försök dö.

**Ingen notis.** `controller/notis/cli` (h-014) är obyggd. Tystnad efter en körning betyder
inte att allt gick bra — den är exakt lika tyst när något faller.

**Ingen livssignal.** Kedjan skriver ingenting medan en session arbetar. Använd §3:s
utifrånkommandon.

**Föräldralösa kandidatcommits.** Varje fallet försök lämnar en commit i objektdatabasen
som ingen ref når. De bryter ingenting, men `git count-objects -v` växer.
