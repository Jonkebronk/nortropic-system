# Codex-handoff — autonoma loopen v1

Kort och exekverbart. Den fullständiga planen är auktoritativ; detta är ingången till den.

```text
PLAN_BASE_SHA      = 1eaa0724be990e14ae095b3be3910496d47d062e
PLAN_COMMIT_SHA    = d2394d66b4b556178f34f6df693a95b1e921066e
PLAN_PATH          = docs/loop/autonomous-loop-plan-v1.md
PLAN_BRANCH        = plan/autonomous-loop-v1
START_SLICE        = S1 · h-017 per-task-domen
```

`PLAN_COMMIT_SHA` är commiten som införde planen. Denna rad kunde inte skrivas i den commiten —
en fil kan inte bära sitt eget commit-SHA — så den fylldes i av en följdcommit på samma gren.
Läs planen ur `PLAN_COMMIT_SHA`; den är oförändrad sedan dess.

## DO_NOT_REDESIGN

Följande är beslutat och ska inte omprövas i implementationen:

- **Grinden slås upp på SÖKVÄG, aldrig på id.** Nyckeln kommer ur spec-radens `exit_test`, och
  `specs/**` är denied_write — därför kan den som skriver registret aldrig peka om sin egen task.
- **Uppslaget bor hos `controller/verify/cli`, inte hos loopen.** Kedjan läser aldrig specens
  tasklista; precedent finns i `controller/policy/cli`, som redan slår upp task-id ur samma fil.
- **Configens globala verifierare ERSÄTTS inte.** Båda domarna måste vara gröna.
- **Riggfel stannar före leasen** (registret prövas i sin helhet), **domen kostar försök.**
- **En ogrindad task attesteras som förut men UTAN `grind_id`.** Frånvaron av dom bokförs;
  körningen stoppas inte. (Ägarbeslut 2026-08-09.)
- **`controller/verify/register.json` ligger UTANFÖR skrivytan.** `controller/verify/cli` anges
  som exakt sökväg.
- **Attestation utan trusted task-gate verdict är aldrig auto-promotion-eligible.**
- **En trust-critical task döms med REPOTS komponenter, aldrig kandidatens.** Mätt: `kmd_run` kör
  grindfilen ur repot men med `cwd=mal`, och husets grindar adresserar komponenter relativt
  (`krav_komponent "controller/verify/cli"`). Utan denna regel dömer en ny domare sin egen födelse
  redan vid grindkörningen. Se planens **G20** — regeln byggs i S1, inte i S8.
- **Ingen force push.** CAS via `--force-with-lease` med EXPLICIT förväntad gammal SHA.
- **Eventströmmen är en egen butik.** Skiva 1:s `{task, status}` rörs inte.
- **Markdown är människans yta.** JSON/Task IR är genererad artefakt.

## VERIFY_BEFORE_CHANGE

Innan en rad ändras, kör och läs:

```bash
git rev-parse HEAD
for t in verify/bin/h-0*-exit; do echo "$t"; bash "$t" | tail -1; done
node scripts/check-invariants.mjs
```

Mätt vid PLAN_BASE_SHA: fjorton grindar, invarianter 8 PASS. `h-002-exit` kan ge exit 2
(ODÖMBART) i en sandbox som saknar skrivväg mot `scripts/` — det är miljön, inte ett fel.

Läs dessutom: `docs/loop/regler.md` (bindande) · `docs/loop/drift.md` (hur loopen körs) ·
`docs/05-beslutslogg.md` raderna LOOP-ÄGARHAND-36 t.o.m. -42 och LOOP-PREMIÄR-1.

## COMMIT_PER_SLICE

En slice = en gren `nortropic/loop-<id>` = en PR. Commit per delsteg. Beslutsloggsrad i **samma
commit** som ändringen (regel 7 + 17 + 22). Commitform `[LOOP] h-0NN delsteg N: ...` med
`Co-Authored-By`-trailer. Stanna vid öppnad PR.

## TESTS_REQUIRED

Beslut 3 gäller: **spec-rad och exit-test FÖRE kod.** Ingen slice byggs mot ett prov som inte
finns.

Per slice krävs:

1. baslinje utan komponent — rött av rätt skäl,
2. ärlig referens som **kastas före commit**,
3. lögnstubbar med EN lögn var, förutsagt utfall skrivet FÖRE körning,
4. hela batteriet grönt,
5. **körning i ägarterminalen före merge** — en grind är inte verifierad förrän den körts i den
   miljö som ska grinda (ÄGARHAND-39: samma commit gav 25/0 hos granskaren och 24/1 hos ägaren),
6. en fix prövas mot en **familj** legitima varianter, inte mot en enda referens (ÄGARHAND-38).

Mergevillkoret kedjas: `./verify/bin/h-0NN-exit && gh pr merge --rebase --delete-branch`.

## STOP_CONDITIONS

Stanna och fråga ägaren när något av detta inträffar:

- **Branch protection på `origin/main`** visar sig kräva PR eller status checks (OVERIFIERAT i
  planen). Auto-promotion faller då, och det ska upptäckas före S6 byggs, inte i drift.
- **Credential-identiteten för promotion** är inte avgjord.
- En slice kräver ändring i en fil **utanför sin `allowed_write`** — det är en spec-radsfråga,
  inte en implementationsfråga. (Hände redan en gång: bokföringsklausulen i h-017 gick inte att
  uppfylla i sin egen yta, ÄGARHAND-42.)
- Ett prov visar sig **inte kunna mäta** det kriteriet kräver — då är kriteriet fel, inte provet.
- Två misslyckade fixförsök på samma fel (byggplan §10, stoppregel).
- En task vill röra **§A-mängden** eller kundflödet.

## CODEX_START_HERE

**S1 · h-017.** Spec-raden finns på main (slice 15, `depends_on` h-002 + h-016, skrivytan vidgad
med `controller/attest/cli`). **Provet `verify/bin/h-017-exit` saknas och byggs FÖRST, i ägarhand
— inte av byggsessionen.**

Mätt och klart att bygga på:

- `"bash": "bash"` i `RUNNERS` räcker för att registret ska kunna starta husets grindar. Prövat i
  klon: `verify run p-001-exit .` → 6 PASS 0 FAIL, `h-002-exit` orört 6 PASS 0 FAIL,
  `hash_mismatch` fäller fortfarande när grinden drivit.
- `verify run h-016-exit <worktree>` → 25 PASS 0 FAIL med worktree-listan identisk före och efter.
  Rekursionsfrågan är besvarad; inget undantag behövs.
- Grindarnas kostnad: h-002 0,2 s · h-013 7,7 s · h-011 10,7 s · h-016 29 s. Ingen når en minut.
- `kmd_write` i `controller/attest/cli` bygger en fast dict med fyra fält. `grind_id` och
  `grind_sha256` läggs till som **valfria argument** så h-011:s och h-016:s anrop står orörda.
  `verify/bin/h-003-exit` grepar mot värden, inte fältuppsättning — extra fält fäller den inte.

- **G20 måste in i provet:** en trust-critical kandidat vars komponent är sabbad så att den alltid
  säger JA ska ändå inte attesteras. Bevis att inversionen är verklig: `_lib.sh` rad 7–14 gör
  `[ ! -x "$1" ]` på en relativ väg, och `kmd_run` sätter `cwd=mal`.

**Öppen riggfråga att lösa när provet skrivs:** `REGISTER` i `controller/verify/cli` är en fast
sökväg och går inte att peka om, så ett fixturregister kräver mutation av repots register med
säkerhetskopia och `trap` (h-002:s precedent, vald väg) — eller en klon som bär arbetsträdets
komponenter.
