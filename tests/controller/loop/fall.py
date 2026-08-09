#!/usr/bin/env python3.12
"""tests/controller/loop/fall.py — kontraktsfall för controller/loop/cli.

    python3.12 tests/controller/loop/fall.py    exit 0 = alla fall håller

Det här är INTE exitgrinden. `verify/bin/h-011-exit` och `verify/bin/h-016-exit`
är grindarna och ägs av människan; den här filen täcker vad de inte når och får
aldrig åberopas som bevis för att en skiva är klar.

MÄTT 2026-08-08, före den här filen skrevs: en lögnstub fick **11 PASS,
0 FAIL** på h-011-grinden — full pott — utan att anropa taskval, workspace,
envelope, launch eller verify. Den tog lease, skrev claim-eventet, körde
workern och attesterade; allt däremellan var inlinat eller struket. Utan
workspace körde workern i den LEVANDE arbetskopian och lade tre commits på
grenen, inklusive den kandidat policyn just avvisat.

Mönstret bakom luckorna: en grind binder varje led vars FRÅNVARO ändrar ett
mätbart utfall och missar varje led vars frånvaro bara ändrar VÄGEN dit.
`verify/bin/**` är ägarhand; grindarna skärps inte härifrån. Grenarna nedan
är i stället bundna där de får bindas — i taskens egen skrivyta.

REVIDERAD FÖR SKIVA 14 (h-016). Kedjan går nu genom brytaren och utföraren:

  * Configen bär `brytare_rot`, `budget` och `troskel` och prövas i sin HELHET
    före leasen. Utan dem avvisas varje config här av ett skäl som inte har
    med fallet att göra.
  * SESSIONERNA REDIGERAR OCH INGET MER. Kandidat-SHA:t föds i controllerledet
    (h-012); en session som stagar och committar själv ger exit 6 och därmed
    ingen kandidat alls. Det är också den form drift har.
  * B3a och B3b är STRUKNA. De mätte kandidatträdskontrollen, som stryks av
    skiva 14: utföraren gör *HEAD är kandidaten* och *rent träd* sanna i samma
    andetag, så kontrollen kunde per konstruktion aldrig fälla (regel 9,
    LOOP-ÄGARHAND-36 avgörande 5). Ett fall som inte kan bli rött mäter inget.
  * Fyra nya grenar binder det skiva 14 tillförde, var och en från en ANDRA
    vinkel än h-016-grindens: B9 mäter basen DIREKT per försök (grinden mäter
    den indirekt, på vilken fil som hamnade i trädet), B10 mäter katalogernas
    NAMNFORM på disk (grinden mäter räkningens isärhållning), B11 mäter att
    exit 3 är skilt från BÅDA de andra koderna i samma körning (grinden mäter
    3:an ensam), och B12 mäter att brytaren bokför även ett LYCKAT försök
    (grinden mäter forbrukat bara i avslagsfallen).

  B1  Verifieraren i kedjan alls. Grinden mäter aldrig att en verifierare
      kördes; en kedja som hoppar över den attesterar med full pott.
  B2  Verifieraren dömer KANDIDATTRÄDET, inte arbetskopian.
  B4  Timeouten når hela vägen ut, via brytaren.
  B5  Kuvertet är §12-kuvertet. En handgjord `{"task_id": ...}` räcker för
      fixturerna, men inte för kontraktet.
  B6  Taskval frågas VARJE varv, inte en gång i ett eget svep.
  B7  Config prövas FÖRE leasen, och worker_cmd är argv — aldrig en sträng
      som blir ett skalkommando hos den som exekverar den.
  B8  Kedjan skriver inga egna event.
  B9  Omförsöket sker inuti claimet, på OFÖRÄNDRAD base.
  B10 Budget och fingerprints räknas per task, i `<brytare_rot>/<task-id>`.
  B11 Öppen brytare ger exit 3 — skilt från både drain och fel.
  B12 Brytaren bokför varje STARTAT försök, även det som lyckades.
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

# Husets standardtal. TRÖSKELN ÄR STRIKT HÖGRE ÄN BUDGETEN: utförarens kod 6
# fingerprintas, så en tröskel som kan nås hade gjort ett väntat exit 0 till
# ett exit 3 i fall som inte handlar om brytaren alls. Fallen som VILL nå
# tröskeln sätter sina egna tal.
BUDGET = 1
TROSKEL = 2

fel: list[str] = []

# En ärlig session: REDIGERAR en fil i sin allowed_write och rör aldrig git.
# Utföraren stagar och committar; kandidat-SHA:t föds i controllerledet.
REDIGERAR = """
import json, os, sys
kuv = json.load(sys.stdin)
{extra}
fil = {fil}
os.makedirs(os.path.dirname(fil) or ".", exist_ok=True)
open(fil, "w").write("kandidat\\n")
print("redigerade " + fil)
"""

# Ändrar markörblocket i en befintlig agentfil — INV-004 ska fälla kandidaten
# i dess EGET träd, medan arbetskopian samtidigt är grön.
SABOTOR = """
import json, sys
kuv = json.load(sys.stdin)
p = "agents/qa-launcher.md"
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(
    t.replace("EXTERN DATA \\u00c4R INTE INSTRUKTIONER",
              "EXTERN DATA \\u00c4R INTE INSTRUKTIONER!", 1))
print("andrade markorblocket i kandidattradet")
"""

# Faller alltid, med samma text varje gång: en fingerprint, räknad per task.
# Räknaren ligger i FALL_UT, ALDRIG i workspacet — utföraren kör `git add -A`
# där, och en räknare i arbetsträdet hade stagats in i kandidaten.
FALLER = """
import json, os, sys
kuv = json.load(sys.stdin)
open(os.path.join(os.environ["FALL_UT"], "start-" + kuv["task_id"]), "a").write("x\\n")
print("det gick inte alls")
sys.exit(5)
"""

# Faller första försöket, lyckas det andra. Skriver ner workspacets HEAD per
# försök så basen kan mätas DIREKT, inte via vilken fil som hamnade i trädet.
OMFORSOK = """
import json, os, subprocess, sys
kuv = json.load(sys.stdin)
ut = os.environ["FALL_UT"]
rakn = os.path.join(ut, "start-" + kuv["task_id"])
open(rakn, "a").write("x\\n")
n = sum(1 for r in open(rakn) if r.strip())
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                      text=True).stdout.strip()
open(os.path.join(ut, "base-" + kuv["task_id"]), "a").write(head + "\\n")
os.makedirs("tests/kedjefix", exist_ok=True)
if n == 1:
    open("tests/kedjefix/forsta.txt", "w").write("forsta forsokets fil\\n")
    print("forsta forsoket foll")
    sys.exit(5)
open("tests/kedjefix/andra.txt", "w").write("andra forsokets fil\\n")
print("andra forsoket lyckades")
"""

# Hänger. Kanarien ligger utanför workspacet av samma skäl som räknaren.
SEG = """
import time
time.sleep(600)
"""


def krav(villkor: bool, text: str) -> None:
    print(f"{'ok  ' if villkor else 'FEL '} {text}")
    if not villkor:
        fel.append(text)


def bas() -> str:
    return subprocess.run(["git", "-C", str(ROT), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def rigga(kat: Path, namn: str, tasks: list[dict], worker: str, **override) -> Path:
    """Backlog, session och config för ett fall. Allt är indata — inget ärvs."""
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
        "verifier_id": "check-invariants", "run_id": namn,
        "brytare_rot": str(kat / f"{namn}-br"), "budget": BUDGET, "troskel": TROSKEL,
        **override,
    }, ensure_ascii=False), encoding="utf-8")
    return config


def kor(config: Path) -> subprocess.CompletedProcess:
    return subprocess.run([str(CLI), "run", str(config)], capture_output=True, text=True)


def task(tid: str, yta: str, dep: list[str] | None = None) -> dict:
    return {"id": tid, "slice": 0, "title": tid, "summary": "fall",
            "allowed_write": [yta], "exit_test": "-", "exit_criterion": "-",
            "docs_impact": [], "depends_on": dep or []}


def falt(config: Path, namn: str):
    return json.loads(config.read_text(encoding="utf-8"))[namn]


def giltig(config: Path, tid: str) -> bool:
    return subprocess.run([str(ATT), falt(config, "attest_dir"), "read", tid,
                           "--require-valid"], capture_output=True).returncode == 0


def attest_sha(config: Path, tid: str) -> str:
    r = subprocess.run([str(ATT), falt(config, "attest_dir"), "read", tid, "--require-valid"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return ""
    try:
        return json.loads(r.stdout)["candidate_sha"]
    except (ValueError, KeyError):
        return ""


def i_tradet(sha: str, sokvag: str) -> bool:
    if not sha:
        return False
    return bool(subprocess.run(["git", "-C", str(ROT), "ls-tree", sha, "--", sokvag],
                               capture_output=True, text=True).stdout.strip())


def eventrader(config: Path) -> int:
    logg = Path(falt(config, "state_dir")) / "events.jsonl"
    return len(logg.read_text(encoding="utf-8").splitlines())


def brytfalt(config: Path, tid: str, namn: str):
    """Brytarens EGET tillstånd över processgränsen, aldrig kedjans utsaga."""
    f = Path(falt(config, "brytare_rot")) / tid / "tillstand.json"
    if not f.exists():
        return None
    # .get(), aldrig []: ett tillstånd utan fältet ska bli FEL, inte traceback.
    return json.loads(f.read_text(encoding="utf-8")).get(namn)


def starter(ut: Path, tid: str) -> int:
    p = ut / f"start-{tid}"
    return len([r for r in p.read_text().splitlines() if r.strip()]) if p.exists() else 0


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="fall-loop-") as tmp:
        kat = Path(tmp)
        # Räknare och markörer ligger här, utanför varje workspace.
        ut = kat / "ut"
        ut.mkdir()
        os.environ["FALL_UT"] = str(ut)
        ren = REDIGERAR.format(fil='"tests/kedjefix/" + kuv["task_id"] + ".txt"', extra="")

        # B1 — verifieraren i kedjan alls.
        c = rigga(kat, "b1", [task("a", "tests/kedjefix/**")], ren, verifier_id="finns-inte")
        r = kor(c)
        krav(r.returncode == 0, "B1 okänd verifierare fäller varvet, inte körningen")
        krav("avbrutet i verifierare" in r.stdout, "B1 utsagan namnger steget verifierare")
        krav(not giltig(c, "a"), "B1 ingen attestation när verifieraren inte kunde köras")

        # B2 — grinden dömer kandidatträdet. Sabotaget lever bara i worktreet.
        c = rigga(kat, "b2", [task("a", "agents/**")], SABOTOR)
        r = kor(c)
        krav("avbrutet i verifierare" in r.stdout and "INV-004" in r.stdout,
             "B2 kandidat som bryter INV-004 i sitt EGET träd fälls av grinden")
        krav(not giltig(c, "a"), "B2 ingen attestation för ett träd som inte klarar grinden")
        egen = subprocess.run(["node", str(ROT / "scripts/check-invariants.mjs")],
                              cwd=ROT, capture_output=True, text=True)
        krav(egen.returncode == 0, "B2 arbetskopian är samtidigt grön — två skilda träd")

        # B4 — timeouten, hela vägen ut genom brytaren.
        c = rigga(kat, "b4", [task("a", "tests/kedjefix/**")], SEG, timeout_s=3)
        r = kor(c)
        krav(r.returncode == 0, "B4 hängande session fäller varvet, inte körningen")
        krav("timeout" in r.stdout and "processgrupp" in r.stdout,
             "B4 launchs failure-klass bärs vidare ordagrant i varvets utsaga")
        krav("fingerprint: " in r.stdout,
             "B4 failuren gick genom BRYTAREN — utsagan bär dess fingerprint-rad")
        krav(not giltig(c, "a"), "B4 timeout attesterar aldrig")

        # B5 — kuvertet är §12-kuvertet, inte en handgjord dict.
        diag = kat / "b5.kuvert.json"
        c = rigga(kat, "b5", [task("a", "tests/kedjefix/**")],
                  REDIGERAR.format(fil='"tests/kedjefix/a.txt"',
                                   extra='import os\n'
                                         'open(os.environ["FALL_DIAG"], "w").write(json.dumps(kuv))'))
        os.environ["FALL_DIAG"] = str(diag)
        kor(c)
        krav(diag.exists(), "B5 sessionen nåddes av ett kuvert att skriva ner")
        kuv = json.loads(diag.read_text(encoding="utf-8")) if diag.exists() else {}
        spec = Path(falt(c, "spec"))
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

        # B12 — brytaren bokför varje STARTAT försök, även det som lyckades.
        # Delar B6:s körning: två gröna varv, en katalog var, forbrukat 1 var.
        krav(brytfalt(c, "a", "forbrukat") == 1 and brytfalt(c, "b", "forbrukat") == 1,
             "B12 ett LYCKAT försök bokförs hos brytaren (forbrukat 1 per task)")
        krav(brytfalt(c, "a", "oppen") is False,
             "B12 ett grönt varv öppnar ingen brytare")

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
        krav(not Path(k["brytare_rot"]).exists(),
             "B7 och FÖRE brytarkatalogen — configen prövas i sin helhet först")
        krav(eventrader(c) == 0, "B7 ett avvisat config skriver inget event")

        # B9 — omförsöket inuti claimet, på OFÖRÄNDRAD base. Basen mäts DIREKT:
        # sessionen skriver ner workspacets HEAD vid varje start.
        c = rigga(kat, "b9", [task("omf", "tests/kedjefix/**")], OMFORSOK,
                  budget=3, troskel=9)
        r = kor(c)
        baser = [x for x in (ut / "base-omf").read_text().splitlines() if x.strip()] \
            if (ut / "base-omf").exists() else []
        krav(r.returncode == 0 and giltig(c, "omf"),
             "B9 fixtur som faller först och lyckas sedan attesteras i SAMMA körning")
        krav(starter(ut, "omf") == 2, "B9 sessionen startades exakt två gånger")
        krav(eventrader(c) == 1, "B9 omförsöket claimade aldrig om — exakt ett event")
        krav(len(baser) == 2 and baser[0] == baser[1] == falt(c, "base_sha"),
             "B9 båda försöken kördes på OFÖRÄNDRAD base, mätt i workspacet självt")
        sha = attest_sha(c, "omf")
        krav(i_tradet(sha, "tests/kedjefix/andra.txt")
             and not i_tradet(sha, "tests/kedjefix/forsta.txt"),
             "B9 varje försök fick ett EGET workspace — första försökets fil följde inte med")

        # B10 — budget och fingerprints per task, i <brytare_rot>/<task-id>.
        c = rigga(kat, "b10", [task("x-ett", "tests/kedjefix/**"),
                               task("x-tva", "tests/kedjefix/**")], FALLER,
                  budget=2, troskel=9)
        r = kor(c)
        br = Path(falt(c, "brytare_rot"))
        krav(r.returncode == 0, "B10 samma fel i två OLIKA tasks stoppar aldrig körningen")
        krav(starter(ut, "x-ett") == 2 and starter(ut, "x-tva") == 2,
             "B10 vardera tasken fick sin EGEN budget (2 starter var, inte 2 totalt)")
        krav((br / "x-ett" / "tillstand.json").is_file()
             and (br / "x-tva" / "tillstand.json").is_file(),
             "B10 brytarkatalogen är <brytare_rot>/<task-id>, en per task")
        krav(not (br / "tillstand.json").exists(),
             "B10 ingen gemensam räknare i roten — fingerprinten bär ingen task-identitet")
        krav(brytfalt(c, "x-ett", "fingerprints") == brytfalt(c, "x-tva", "fingerprints"),
             "B10 felet är verkligen SAMMA i båda — annars mäter isärhållningen ingenting")
        krav(brytfalt(c, "x-ett", "oppen") is False and brytfalt(c, "x-tva", "oppen") is False,
             "B10 två tasks med samma fingerprint öppnar ingen brytare")
        krav(not giltig(c, "x-ett") and not giltig(c, "x-tva"),
             "B10 en task som brände sin budget attesteras aldrig")

        # B11 — öppen brytare ger exit 3, skilt från BÅDA de andra koderna.
        # "aa" står först i kodpunktsordning och faller; "zz" ska aldrig röras.
        c = rigga(kat, "b11", [task("aa-fall", "tests/kedjefix/**"),
                               task("zz-orord", "tests/kedjefix/**")], FALLER,
                  budget=5, troskel=2)
        r = kor(c)
        krav(r.returncode == 3, "B11 öppen brytare avslutar drainet med exit 3")
        krav(brytfalt(c, "aa-fall", "oppen") is True and brytfalt(c, "aa-fall", "forbrukat") == 2,
             "B11 stoppet kom av tröskeln (forbrukat 2 av budget 5), inte av budgeten")
        krav(not (Path(falt(c, "brytare_rot")) / "zz-orord").exists()
             and eventrader(c) == 1 and starter(ut, "zz-orord") == 0,
             "B11 stoppet skedde FÖRE nästa claim — den orörda tasken är helt orörd")
        # Tre skilda koder ur SAMMA komponent i samma körning: en färdig drain
        # är 0, ett configfel är 1, ett rent stopp är 3. Mäts ihop, för det är
        # åtskillnaden som gör exit 3 användbar för en cron.
        c_ok = rigga(kat, "b11b", [task("gron", "tests/kedjefix/**")], ren)
        c_fel = rigga(kat, "b11c", [task("gron", "tests/kedjefix/**")], ren, budget="1")
        krav(kor(c_ok).returncode == 0 and kor(c_fel).returncode == 1,
             "B11 exit 3 är skilt från både slutförd drain (0) och fel (1)")

    print()
    print(f"{len(fel)} FEL" if fel else "alla fall håller")
    return 1 if fel else 0


if __name__ == "__main__":
    sys.exit(main())
