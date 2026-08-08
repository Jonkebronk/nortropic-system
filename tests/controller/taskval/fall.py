#!/usr/bin/env python3.12
"""tests/controller/taskval/fall.py — kontraktsfall för controller/taskval/cli.

    python3.12 tests/controller/taskval/fall.py    exit 0 = alla fall håller

Det här är INTE exitgrinden. `verify/bin/h-010-exit` är grinden och ägs av
människan; den här filen täcker vad grinden inte når och får aldrig åberopas
som bevis för att skiva 8 är klar.

MÄTT 2026-08-08, före den här filen skrevs: fyra kontraktsbrott gav VAR FÖR
SIG 10 PASS 0 FAIL i grinden, och alla fyra tillsammans likaså. Grindens
fixturer beträder aldrig grenarna:

  B1  "samtliga depends_on" mot "bara depends_on[0]" — ingen fixtur i
      grinden har mer än ETT beroende, så skillnaden är omätbar där.
  B2  "status frånvarande ELLER pending" mot "varje status diskvalificerar"
      — grinden skriver aldrig ett pending-event.
  B3  oläsbar spec → tomt val exit 0 i stället för exit 1. Grinden läser
      aldrig en trasig spec, så "fel" och "ingen behörig" är samma utfall
      för den. Det är exakt den sammanblandning _lib.sh:s krav_mekanism
      finns till för att förhindra på andra hållet.
  B4  oinitierad state → tolkas som tom. Grinden initierar alltid.

Därtill: en attestbutik som KRASCHAR ger samma exit 1 som "ingen
attestation". Läses de lika blir en trasig butik ett tyst omval av redan
klart arbete — fail-open åt det farliga hållet.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROT = Path(__file__).resolve().parents[3]
CLI = ROT / "controller/taskval/cli"
ATT = ROT / "controller/attest/cli"
ST = ROT / "controller/state/cli"

S1 = "1111111111111111111111111111111111111111"
S2 = "2222222222222222222222222222222222222222"


def kor(argv: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([str(a) for a in argv], capture_output=True, text=True,
                          cwd=ROT, timeout=60)


def spec(kat: Path, namn: str, tasks: list[dict] | str) -> Path:
    p = kat / namn
    p.write_text(tasks if isinstance(tasks, str)
                 else json.dumps({"tasks": tasks}, ensure_ascii=False), encoding="utf-8")
    return p


def rader(stkat: Path) -> int:
    logg = stkat / "events.jsonl"
    return len(logg.read_text(encoding="utf-8").splitlines()) if logg.exists() else 0


def tabell(stkat: Path) -> dict[str, str]:
    r = kor([ST, "rebuild", stkat])
    return {x["task"]: x["status"] for x in json.loads(r.stdout)} if r.returncode == 0 else {}


def main() -> int:
    ratt = fel = 0

    def doma(namn: str, villkor: bool, sett: str, krav: str) -> None:
        nonlocal ratt, fel
        if villkor:
            ratt += 1
        else:
            fel += 1
            print(f"FAIL  {namn} — krav: {krav} · sett: {sett}")

    def val(namn: str, sp: Path, attkat: Path, stkat: Path, vantat: str,
            kmd: str = "select") -> None:
        r = kor([CLI, kmd, sp, attkat, stkat])
        doma(namn, r.returncode == 0 and r.stdout.strip() == vantat,
             f"exit={r.returncode} ut=[{r.stdout.strip()}] err=[{r.stderr.strip()[:70]}]",
             f"exit=0 ut=[{vantat}]")

    def avvisas(namn: str, sp: Path, attkat: Path, stkat: Path, kmd: str = "select") -> None:
        r = kor([CLI, kmd, sp, attkat, stkat])
        # Ett fel får ALDRIG se ut som ett tomt val: exit 1, tom stdout,
        # orsak på stderr. Tom stdout + exit 0 är "ingen behörig task".
        doma(namn, r.returncode == 1, f"exit={r.returncode}", "exit=1")
        doma(f"{namn}/tyst-stdout", r.stdout.strip() == "", f"[{r.stdout.strip()[:70]}]",
             "tom stdout — ett fel är inget val")
        doma(f"{namn}/orsak", r.stderr.strip() != "", "tom stderr", "orsaken ska namnges")
        doma(f"{namn}/traceback", "Traceback" not in r.stderr, "stackspår ur komponenten",
             "aldrig traceback")

    with tempfile.TemporaryDirectory(prefix="taskval-fall.") as tmp:
        W = Path(tmp)

        # --- B1: "samtliga depends_on". Grindens fixturer har max ett beroende.
        # A-tva sorterar FÖRE y-rot i kodpunkt, så en läsare som nöjer sig med
        # ett av beroendena avslöjar sig i själva valet.
        sp_flera = spec(W, "flera.json", [
            {"id": "A-tva", "depends_on": ["z-rot", "y-rot"]},   # första klar, andra inte
            {"id": "B-tva", "depends_on": ["y-rot", "z-rot"]},   # sista klar, första inte
            {"id": "y-rot", "depends_on": []},
            {"id": "z-rot", "depends_on": []},
        ])
        a1, s1 = W / "att1", W / "st1"
        kor([ST, "init", s1])
        kor([ATT, a1, "write", "z-rot", S1])
        val("B1/forsta-dep-racker-inte", sp_flera, a1, s1, "y-rot")
        kor([ATT, a1, "write", "y-rot", S2])
        val("B1/bada-dep-klara", sp_flera, a1, s1, "A-tva")

        # --- B2: pending är VALBART, allt annat är det inte.
        sp_st = spec(W, "status.json", [
            {"id": "p-ett", "depends_on": []},
            {"id": "q-tva", "depends_on": []},
        ])
        a2, s2 = W / "att2", W / "st2"
        kor([ST, "init", s2])
        kor([ST, "append", s2, json.dumps({"task": "p-ett", "status": "pending"})])
        val("B2/pending-ar-valbar", sp_st, a2, s2, "p-ett")
        # En status utanför {frånvarande, pending} diskvalificerar. Utan det här
        # fallet kan B2 "rättas" genom att strunta i state helt.
        kor([ST, "append", s2, json.dumps({"task": "p-ett", "status": "running"})])
        val("B2/okand-status-diskvalificerar", sp_st, a2, s2, "q-tva")
        # pending igen efter running: state är en logg, senaste eventet gäller.
        kor([ST, "append", s2, json.dumps({"task": "p-ett", "status": "pending"})])
        val("B2/ater-pending-ar-valbar", sp_st, a2, s2, "p-ett")

        # --- B3: specen är indata och kan vara trasig. Sex former, ett utfall.
        a3, s3 = W / "att3", W / "st3"
        kor([ST, "init", s3])
        avvisas("B3/saknad-fil", W / "finns-inte.json", a3, s3)
        avvisas("B3/inte-json", spec(W, "trasig.json", "{ inte json"), a3, s3)
        avvisas("B3/ingen-tasklista", spec(W, "utan.json", '{"uppgifter": []}'), a3, s3)
        avvisas("B3/task-utan-id", spec(W, "utan-id.json", [{"depends_on": []}]), a3, s3)
        avvisas("B3/depends-inte-lista",
                spec(W, "dep.json", [{"id": "a", "depends_on": "b"}]), a3, s3)
        # Två rader med samma id är två sanningar om samma task — vilken
        # depends_on gäller? Ett tyst val mellan dem är värre än en vägran.
        avvisas("B3/dubblerat-id", spec(W, "dubbel.json", [
            {"id": "a", "depends_on": []}, {"id": "a", "depends_on": ["b"]},
        ]), a3, s3)
        # Tom backlog är däremot inget fel: den är bara tom.
        val("B3/tom-backlog", spec(W, "tom.json", []), a3, s3, "")

        # --- B4: state anges av anroparen och kan saknas.
        sp_enkel = spec(W, "enkel.json", [{"id": "a-ett", "depends_on": []}])
        avvisas("B4/oinitierad-state", sp_enkel, a3, W / "ingen-state")
        s4 = W / "st4"
        s4.mkdir()
        (s4 / "events.jsonl").write_text('{"task":"a-ett","status":"claimed"}', encoding="utf-8")
        avvisas("B4/trunkerad-logg", sp_enkel, a3, s4)

        # --- Attest som kraschar får inte läsas som "ingen attestation".
        a5, s5 = W / "att5", W / "st5"
        a5.mkdir()
        kor([ST, "init", s5])
        (a5 / "attestations.json").write_text("{ trasig", encoding="utf-8")
        avvisas("attest/krasch-ar-inte-obehorig", sp_enkel, a5, s5)

        # --- claim: effekten mäts i loggen, inte i claimens utsaga.
        sp_kedja = spec(W, "kedja.json", [
            {"id": "k-1", "depends_on": []},
            {"id": "k-2", "depends_on": []},
        ])
        a6, s6 = W / "att6", W / "st6"
        kor([ST, "init", s6])
        val("claim/forsta", sp_kedja, a6, s6, "k-1", kmd="claim")
        doma("claim/eventet-namnger-ratt-task", tabell(s6).get("k-1") == "claimed",
             str(tabell(s6)), "k-1 claimed i rebuild")
        val("claim/andra", sp_kedja, a6, s6, "k-2", kmd="claim")
        # Grindens K9 räknar bara rader för claim två och tre. Här prövas att
        # ANDRA eventet också namnger rätt task.
        doma("claim/andra-eventet-namnger-ratt-task", tabell(s6).get("k-2") == "claimed",
             str(tabell(s6)), "k-2 claimed i rebuild")
        fore = rader(s6)
        for _ in range(3):
            kor([CLI, "select", sp_kedja, a6, s6])
        doma("select/muterar-aldrig", rader(s6) == fore, f"{fore} → {rader(s6)}",
             "tre select lämnar loggen orörd")
        # Ett claim som misslyckas får inte lämna ett halvt spår.
        fore = rader(s6)
        avvisas("claim/trasig-spec", W / "trasig.json", a6, s6, kmd="claim")
        doma("claim/fel-appendar-inget", rader(s6) == fore, f"{fore} → {rader(s6)}",
             "ett avvisat claim rör aldrig loggen")

        # --- Anropsformen. Fel antal argument är ett fel, inte ett tomt val.
        for namn, argv in (("inga-argument", [CLI]),
                           ("okant-kommando", [CLI, "valj", sp_enkel, a3, s3]),
                           ("for-fa-argument", [CLI, "select", sp_enkel, a3])):
            r = kor(argv)
            doma(f"anrop/{namn}", r.returncode == 1 and r.stdout.strip() == "",
                 f"exit={r.returncode} ut=[{r.stdout.strip()[:40]}]", "exit=1, tom stdout")

    print(f"\n{ratt} rätt, {fel} fel")
    return 1 if fel else 0


if __name__ == "__main__":
    sys.exit(main())
