#!/usr/bin/env python3.12
"""tests/controller/loop/fall.py — kontraktsfall för controller/loop/cli.

    python3.12 tests/controller/loop/fall.py    exit 0 = alla fall håller

Det här är INTE exitgrinden. `verify/bin/h-011-exit` är grinden och ägs av
människan; den här filen täcker vad grinden inte når och får aldrig åberopas
som bevis för att skiva 9 är klar.

MÄTT 2026-08-08, före den här filen skrevs: en lögnstub fick **11 PASS,
0 FAIL** — full pott — utan att anropa taskval, workspace, envelope, launch
eller verify. Den tog lease, skrev claim-eventet, körde workern och
attesterade; allt däremellan var inlinat eller struket. Utan workspace körde
workern i den LEVANDE arbetskopian och lade tre commits på grenen, inklusive
den kandidat policyn just avvisat — och K10 ("inga worktree-rester") var
perfekt uppfylld av att aldrig skapa något.

Mönstret bakom luckorna: grinden binder varje led vars FRÅNVARO ändrar ett
mätbart utfall (parse via K5, policy via K6, lease via K7/K8, attest via
K1/K2, state via K4) och missar varje led vars frånvaro bara ändrar VÄGEN
dit. `verify/bin/**` är ägarhand; grinden skärps inte härifrån. Grenarna
nedan är i stället bundna där de får bindas — i taskens egen skrivyta.

  B1  Verifieraren i kedjan alls. Grinden mäter aldrig att en verifierare
      kördes; en kedja som hoppar över den attesterar 11/0.
  B2  Verifieraren dömer KANDIDATTRÄDET, inte arbetskopian. Grindens fixtur
      skriver bara under tests/kedjefix/**, som ingen invariant bevakar — en
      kedja som verifierar reporoten ser likadan ut där.
  B3  Kandidatträdskontrollen: workspacets HEAD är kandidaten, och inget
      ligger ocommitterat. Grindens worker committar alltid allt den skrev.
  B4  Launchs timeout. Grindens tre workers svarar direkt; ingen hänger.
  B5  Kuvertet är §12-kuvertet. Grindens worker läser bara `task_id`, så
      `{"task_id": ...}` räcker för den.
  B6  Taskval frågas VARJE varv. Grindens fixtur har kodpunktsordning =
      beroendeordning, så ett eget sorterat svep ger samma resultat.
  B7  Config prövas FÖRE leasen, och worker_cmd är argv — aldrig en sträng
      som blir ett skalkommando hos den som exekverar den.
  B8  Kedjan skriver inga egna event. Grinden räknar event bara där de ska
      vara noll (K7, K9), aldrig där de ska vara exakt N.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROT = Path(__file__).resolve().parents[3]
CLI = ROT / "controller/loop/cli"
ST = ROT / "controller/state/cli"
ATT = ROT / "controller/attest/cli"
PY = sys.executable

fel: list[str] = []

# En ärlig worker: skriver EN fil i sin allowed_write, committar den, och
# rapporterar den commit den faktiskt gjorde.
ARLIG = """
import json, os, subprocess, sys
kuv = json.load(sys.stdin)
{extra}
fil = {fil}
os.makedirs(os.path.dirname(fil) or ".", exist_ok=True)
open(fil, "w").write("kandidat\\n")
subprocess.run(["git", "add", fil], check=True)
def commit(m):
    subprocess.run(["git", "-c", "user.name=f", "-c", "user.email=f@t",
                    "commit", "-q", "-m", m], check=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()
sha = commit("kandidat")
{efter}
print(json.dumps({{"status": "candidate", "candidate_sha": sha, "files": [fil]}}))
"""


def krav(villkor: bool, text: str) -> None:
    print(f"{'ok  ' if villkor else 'FEL '} {text}")
    if not villkor:
        fel.append(text)


def bas() -> str:
    return subprocess.run(["git", "-C", str(ROT), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def rigga(kat: Path, namn: str, tasks: list[dict], worker: str, **override) -> Path:
    """Backlog, worker och config för ett fall. Allt är indata — inget ärvs."""
    spec = kat / f"{namn}.backlog.json"
    spec.write_text(json.dumps({
        "spec_version": "fall",
        "defaults": {"max_changed_files": 8, "max_added_lines": 600},
        "tasks": tasks,
    }, ensure_ascii=False), encoding="utf-8")

    workerfil = kat / f"{namn}.worker.py"
    workerfil.write_text(worker, encoding="utf-8")

    (kat / f"{namn}-ws").mkdir(parents=True, exist_ok=True)
    subprocess.run([str(ST), "init", str(kat / f"{namn}-st")], capture_output=True, check=True)

    config = kat / f"{namn}.config.json"
    config.write_text(json.dumps({
        "spec": str(spec), "attest_dir": str(kat / f"{namn}-att"),
        "state_dir": str(kat / f"{namn}-st"), "lease_dir": str(kat / f"{namn}-le"),
        "lease_resurs": "fall", "workspace_rot": str(kat / f"{namn}-ws"),
        "base_sha": bas(), "worker_cmd": [PY, str(workerfil)], "timeout_s": 60,
        "verifier_id": "check-invariants", "run_id": namn, **override,
    }, ensure_ascii=False), encoding="utf-8")
    return config


def kor(config: Path) -> subprocess.CompletedProcess:
    return subprocess.run([str(CLI), "run", str(config)], capture_output=True, text=True)


def task(tid: str, yta: str, dep: list[str] | None = None) -> dict:
    return {"id": tid, "slice": 0, "title": tid, "summary": "fall",
            "allowed_write": [yta], "exit_test": "-", "exit_criterion": "-",
            "docs_impact": [], "depends_on": dep or []}


def giltig(config: Path, tid: str) -> bool:
    k = json.loads(config.read_text(encoding="utf-8"))
    return subprocess.run([str(ATT), k["attest_dir"], "read", tid, "--require-valid"],
                          capture_output=True).returncode == 0


def eventrader(config: Path) -> int:
    logg = Path(json.loads(config.read_text(encoding="utf-8"))["state_dir"]) / "events.jsonl"
    return len(logg.read_text(encoding="utf-8").splitlines())


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="fall-loop-") as tmp:
        kat = Path(tmp)
        ren = ARLIG.format(fil='"tests/kedjefix/" + kuv["task_id"] + ".txt"', extra="", efter="")

        # B1 — verifieraren i kedjan alls.
        c = rigga(kat, "b1", [task("a", "tests/kedjefix/**")], ren, verifier_id="finns-inte")
        r = kor(c)
        krav(r.returncode == 0, "B1 okänd verifierare fäller varvet, inte körningen")
        krav("avbrutet i verifierare" in r.stdout, "B1 utsagan namnger steget verifierare")
        krav(not giltig(c, "a"), "B1 ingen attestation när verifieraren inte kunde köras")

        # B2 — grinden dömer kandidatträdet. Sabotaget lever bara i worktreet.
        sabb = ARLIG.format(
            fil='"agents/qa-launcher.md"',
            extra=('t = open("agents/qa-launcher.md", encoding="utf-8").read()\n'
                   'open("agents/qa-launcher.md", "w", encoding="utf-8").write(\n'
                   '    t.replace("EXTERN DATA \\u00c4R INTE INSTRUKTIONER",\n'
                   '              "EXTERN DATA \\u00c4R INTE INSTRUKTIONER!", 1))\n'
                   'import sys as _s\n'),
            efter="")
        # Filen skrivs om av extra-blocket; ARLIG:s egen skrivning skulle nolla
        # den, så kandidaten byggs i stället av en egen minimal worker.
        sabb = sabb.replace('open(fil, "w").write("kandidat\\n")\n', "")
        c = rigga(kat, "b2", [task("a", "agents/**")], sabb)
        r = kor(c)
        krav("avbrutet i verifierare" in r.stdout and "INV-004" in r.stdout,
             "B2 kandidat som bryter INV-004 i sitt EGET träd fälls av grinden")
        krav(not giltig(c, "a"), "B2 ingen attestation för ett träd som inte klarar grinden")
        egen = subprocess.run(["node", str(ROT / "scripts/check-invariants.mjs")],
                              cwd=ROT, capture_output=True, text=True)
        krav(egen.returncode == 0, "B2 arbetskopian är samtidigt grön — två skilda träd")

        # B3a — ocommitterat kvar i workspacet.
        smutsig = ARLIG.format(fil='"tests/kedjefix/a.txt"', extra="",
                               efter='open("tests/kedjefix/rest.txt", "w").write("rest\\n")\n')
        c = rigga(kat, "b3a", [task("a", "tests/kedjefix/**")], smutsig)
        r = kor(c)
        krav("avbrutet i kandidatträd" in r.stdout, "B3a ocommitterat kvar → trädet är inte kandidatens")
        krav(not giltig(c, "a"), "B3a ingen attestation på ett träd utanför kandidatens SHA")

        # B3b — workern rapporterar en ANNAN commit än den workspacet står på.
        aldre = ARLIG.format(
            fil='"tests/kedjefix/a.txt"', extra="",
            efter=('open("tests/kedjefix/b.txt", "w").write("b\\n")\n'
                   'subprocess.run(["git", "add", "tests/kedjefix/b.txt"], check=True)\n'
                   'commit("andra")\n'))
        c = rigga(kat, "b3b", [task("a", "tests/kedjefix/**")], aldre)
        r = kor(c)
        krav("avbrutet i kandidatträd" in r.stdout and "HEAD" in r.stdout,
             "B3b HEAD ≠ rapporterad kandidat → trädet som skulle verifieras är inte kandidatens")
        krav(not giltig(c, "a"), "B3b ingen attestation när HEAD och kandidat pekar isär")

        # B4 — launchs timeout, och kedjan går vidare till exit 0.
        c = rigga(kat, "b4", [task("a", "tests/kedjefix/**")],
                  "import time\ntime.sleep(600)\n", timeout_s=3)
        r = kor(c)
        krav(r.returncode == 0, "B4 hängande worker fäller varvet, inte körningen")
        krav("avbrutet i launch" in r.stdout and "timeout" in r.stdout,
             "B4 launchs failure-klass bärs vidare ordagrant i varvets utsaga")
        krav("processgrupp" in r.stdout, "B4 utsagan bär att hela processgruppen dödades")

        # B5 — kuvertet är §12-kuvertet, inte en handgjord dict.
        diag = kat / "b5.kuvert.json"
        kuvertworker = ARLIG.format(
            fil='"tests/kedjefix/a.txt"',
            extra='open(os.environ["FALL_DIAG"], "w").write(json.dumps(kuv))\n', efter="")
        c = rigga(kat, "b5", [task("a", "tests/kedjefix/**")], kuvertworker)
        os.environ["FALL_DIAG"] = str(diag)
        kor(c)
        krav(diag.exists(), "B5 workern nåddes av ett kuvert att skriva ner")
        kuv = json.loads(diag.read_text(encoding="utf-8")) if diag.exists() else {}
        spec = Path(json.loads(c.read_text(encoding="utf-8"))["spec"])
        krav(sorted(kuv) == ["allowed_write", "base_sha", "candidate_requirements",
                             "denied_write", "description", "run_id", "spec_sha256",
                             "task_id", "title"],
             "B5 kuvertet bär v4.1 §12:s nio fält")
        # .get(), aldrig []: ett kuvert som saknar fältet ska bli FEL, inte en
        # traceback. Ett fall som DÖR är varken PASS eller FAIL, och den
        # sammanblandningen är precis den _lib.sh:s exit 2 finns för att undvika.
        krav(kuv.get("spec_sha256") == hashlib.sha256(spec.read_bytes()).hexdigest(),
             "B5 spec_sha256 är CONFIG-specens faktiska hash, inte repospecens")
        krav(kuv.get("allowed_write") == ["tests/kedjefix/**"] and kuv.get("base_sha") == bas(),
             "B5 allowed_write och base_sha kommer ur uppdraget, inte ur en egen lista")

        # B6 — taskval frågas varje varv. Kodpunktsordning ≠ beroendeordning:
        # "a" står först men beror på "b", så ett eget sorterat svep i ETT pass
        # hoppar över "a" och lämnar den obyggd.
        c = rigga(kat, "b6", [task("a", "tests/kedjefix/**", ["b"]),
                              task("b", "tests/kedjefix/**")], ren)
        r = kor(c)
        krav(giltig(c, "b") and giltig(c, "a"),
             "B6 båda attesteras trots att beroendet står EFTER i kodpunktsordning")
        # find(), aldrig index(): en utsaga som saknar raden ska bli FEL, inte
        # en traceback — samma disciplin som B5:s .get().
        forst, sedan = r.stdout.find("varv 1 b"), r.stdout.find("varv 2 a")
        krav(0 <= forst < sedan,
             "B6 ordningen kommer ur taskval, inte ur en egen sortering")

        # B8 — exakt ett event per varv, inga körningsevent. (Delar B6:s körning.)
        krav(eventrader(c) == 2, "B8 två varv ger exakt två event — kedjan skriver inga egna")

        # B7 — config prövas före leasen.
        c = rigga(kat, "b7", [task("a", "tests/kedjefix/**")], ren)
        k = json.loads(c.read_text(encoding="utf-8"))
        k["worker_cmd"] = f"{PY} {kat}/b7.worker.py"
        c.write_text(json.dumps(k, ensure_ascii=False), encoding="utf-8")
        r = kor(c)
        krav(r.returncode == 1 and "worker_cmd" in r.stderr,
             "B7 worker_cmd som sträng avvisas — argv, aldrig ett skalkommando")
        krav(not Path(k["lease_dir"]).exists(),
             "B7 configfelet fälls FÖRE leasen tas — ingen lease lämnas efter sig")
        krav(eventrader(c) == 0, "B7 ett avvisat config skriver inget event")

    print()
    print(f"{len(fel)} FEL" if fel else "alla fall håller")
    return 1 if fel else 0


if __name__ == "__main__":
    sys.exit(main())
