#!/usr/bin/env python3.12
"""tests/controller/launch/fall.py — kontraktsfall för controller/launch/cli.

    python3.12 tests/controller/launch/fall.py     exit 0 = alla fall håller

Det här är INTE exitgrinden. `verify/bin/h-009-exit` är grinden och ägs av
människan; den här filen täcker vad grinden inte når och får aldrig åberopas
som bevis för att skiva 6c är klar.

**Kanariefågeln i stället för processtabellen.** Grindens K4 letar rest med
`pgrep -f` och `ps -eo command`. Under Claude Codes sandbox är båda blinda:
pgrep svarar "Cannot get process list" och `ps -eo command` ger noll rader.
Mätt 2026-08-08 med en levande `sleep 120` igång sade K4 ändå PASS. Här
mäts därför EFFEKTEN i stället: barnbarnet skriver en rad till en fil med
jämna mellanrum, och växer filen efter timeouten levde det vidare. Det
kräver ingen processtabell och fungerar i båda miljöerna.

Kanariefågeln räknar NER och dör av sig själv. En `while true` hade lämnat
en levande process efter sig om städningen fallerar — och att lämna rest i
ett prov som mäter rest vore svårt att försvara.

Grinden kör aldrig ett kommando som rapporterar sin cwd, läser aldrig
tillbaka `<timeout-s>`, och räcker kuvertets sökväg till testskriptet som
argument. En lögnstub som kastade alla tre argumenten fick 8 PASS 0 FAIL
(mätt 2026-08-08) och körde workern i den levande arbetskopian. Avsnittet
ARGUMENTEN NÅR PROCESSEN nedan är det grinden bevisligen inte kan skilja.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROT = Path(__file__).resolve().parents[3]
CLI = ROT / "controller/launch/cli"
KUVERT_CLI = ROT / "controller/envelope/cli"
ANROP, LAUNCH, NONZERO, TIMEOUT = 1, 3, 4, 5

# Kanariefågeln tickar i högst TICKAR × 0,2 s och dör sedan av sig själv.
KANARIE = """#!/usr/bin/env bash
( for i in $(seq 1 60); do echo tick >> "$1"; sleep 0.2; done ) &
sleep 120
"""

SKRIPT = {
    "var.sh": '#!/usr/bin/env bash\npwd -P\n',
    "kuvert.sh": ('#!/usr/bin/env bash\n'
                  'echo "env=${NORTROPIC_KUVERT:-SAKNAS}"\n'
                  'python3.12 -c \'import json,sys;print("stdin="+json.load(sys.stdin)["task_id"])\'\n'),
    "miljo.sh": ('#!/usr/bin/env bash\n'
                 'echo "gh=${GH_TOKEN:-SAKNAS} github=${GITHUB_TOKEN:-SAKNAS} '
                 'slack=${SLACK_TOKEN:-SAKNAS} path=${PATH:+finns} home=${HOME:+finns}"\n'),
    "tyst.sh": '#!/usr/bin/env bash\nexit 0\n',
    "kod7.sh": '#!/usr/bin/env bash\necho ut >&2\nexit 7\n',
    "binart.sh": '#!/usr/bin/env bash\nprintf "rad1\\n\\x00\\xff rad2"\n',
    "langsam.sh": '#!/usr/bin/env bash\nsleep 120\n',
    "kanarie.sh": KANARIE,
}


def main() -> int:
    if not os.access(CLI, os.X_OK):
        print(f"FAIL  {CLI} saknas eller är inte körbar")
        return 1

    kat = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR") or "/tmp"))
    ws = kat / "ws"
    ws.mkdir()
    for namn, kropp in SKRIPT.items():
        p = kat / namn
        p.write_text(kropp, encoding="utf-8")
        os.chmod(p, 0o755)

    sha = subprocess.run(["git", "-C", str(ROT), "rev-parse", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    kuv = kat / "kuvert.json"
    r = subprocess.run([str(KUVERT_CLI), "build", "h009-fall", "h-001", sha],
                       capture_output=True, text=True, cwd=ROT)
    if r.returncode != 0 or not r.stdout.strip():
        print("SKIP  kunde inte bygga provkuvert — odömbart")
        return 2
    kuv.write_text(r.stdout, encoding="utf-8")

    ratt = fel = 0

    def doma(namn: str, villkor: bool, sett: str, krav: str) -> None:
        nonlocal ratt, fel
        if villkor:
            ratt += 1
        else:
            fel += 1
            print(f"FAIL  {namn} — krav: {krav} · sett: {sett}")

    def kor(timeout: str, *kommando: str) -> tuple[int, bytes, str]:
        r = subprocess.run([str(CLI), "run", str(ws), str(kuv), timeout, "--", *kommando],
                           capture_output=True, cwd=ROT, timeout=90)
        return r.returncode, r.stdout, r.stderr.decode("utf-8", "replace").strip()

    # --- ARGUMENTEN NÅR PROCESSEN: det grinden inte kan skilja ---
    kod, ut, err = kor("30", str(kat / "var.sh"))
    doma("cwd", ut.decode().strip() == str(ws.resolve()), ut.decode().strip(),
         f"processen ska köra i {ws.resolve()} — grinden prövar det aldrig")
    doma("cwd/stderr", err == "", err[:60], "tom stderr")

    kod, ut, _ = kor("30", str(kat / "kuvert.sh"))
    text = ut.decode("utf-8", "replace")
    doma("kuvert/env", f"env={kuv.resolve()}" in text, text.strip()[:70],
         "NORTROPIC_KUVERT med absolut sökväg")
    doma("kuvert/stdin", "stdin=h-001" in text, text.strip()[:70],
         "kuvertets innehåll på stdin")
    doma("kuvert/ej-i-workspace", not any(ws.iterdir()), str(list(ws.iterdir())),
         "kuvertet får ALDRIG läggas i workspacet — workern kör git add -A där")

    # v4.1 §10. Ligger utanför h-009:s exit_criterion och prövas därför här.
    miljo = dict(os.environ, GH_TOKEN="hemlig", GITHUB_TOKEN="hemlig", SLACK_TOKEN="hemlig")
    r = subprocess.run([str(CLI), "run", str(ws), str(kuv), "30", "--", str(kat / "miljo.sh")],
                       capture_output=True, text=True, cwd=ROT, env=miljo, timeout=60)
    doma("env/rensad", "gh=SAKNAS github=SAKNAS slack=SAKNAS" in r.stdout, r.stdout.strip()[:70],
         "GH_*, GITHUB_* och SLACK_* rensas (v4.1 §10)")
    doma("env/behallen", "path=finns home=finns" in r.stdout, r.stdout.strip()[:70],
         "PATH och HOME behålls — workern måste kunna köra")

    # --- TIMEOUT: värdet ska följa argumentet, inte en konstant ---
    tider = {}
    for begard in ("1", "4"):
        start = time.monotonic()
        kod, ut, err = kor(begard, str(kat / "langsam.sh"))
        tider[begard] = time.monotonic() - start
        doma(f"timeout-{begard}/kod", kod == TIMEOUT, f"exit={kod}", f"exit={TIMEOUT}")
        doma(f"timeout-{begard}/klass", b"timeout" in ut.lower(), ut.decode()[:60],
             "klassen timeout på stdout")
        doma(f"timeout-{begard}/tid", float(begard) <= tider[begard] < float(begard) + 3,
             f"{tider[begard]:.1f}s", f"ska döda strax efter {begard}s")
        doma(f"timeout-{begard}/stderr", err == "", err[:60], "tom stderr")

    # Den avgörande mätningen: en hårdkodad timeout ger samma tid för båda.
    # Absoluta gränser ensamma fäller inte en konstant som råkar ligga inom dem.
    doma("timeout/foljer-argumentet", tider["4"] - tider["1"] >= 2.0,
         f"1s tog {tider['1']:.1f}s, 4s tog {tider['4']:.1f}s — skillnad "
         f"{tider['4'] - tider['1']:.1f}s",
         "skillnaden ska följa argumentet, inte vara noll")

    # --- PROCESSGRUPPEN: kanariefågeln, inte processtabellen ---
    spar = kat / "kanarie.txt"
    spar.write_text("", encoding="utf-8")
    kod, ut, _ = kor("2", str(kat / "kanarie.sh"), str(spar))
    vid_timeout = len(spar.read_text(encoding="utf-8").splitlines())
    time.sleep(2.5)
    efterat = len(spar.read_text(encoding="utf-8").splitlines())
    doma("grupp/barnbarn-dott", vid_timeout == efterat, f"{vid_timeout} → {efterat} rader",
         "barnbarnet ska dö med gruppen — växer filen levde det vidare")
    doma("grupp/tickade", vid_timeout > 0, f"{vid_timeout} rader",
         "kanariefågeln måste ha hunnit ticka, annars mäter provet ingenting")

    # --- STDOUT OFÖRÄNDRAD, in i minsta byte ---
    kod, ut, _ = kor("30", str(kat / "binart.sh"))
    doma("stdout/binart", ut == b"rad1\n\x00\xff rad2", repr(ut)[:60],
         "byte för byte, ingen radbrytning tillagd")
    kod, ut, _ = kor("30", str(kat / "tyst.sh"))
    doma("stdout/tomt", kod == 0 and ut == b"", f"exit={kod} ut={ut!r}",
         "tyst lyckad process ger exit 0 och tom stdout")

    # --- FAILURE-KLASSERNA ---
    kod, ut, _ = kor("30", str(kat / "kod7.sh"))
    doma("nonzero/kod", kod == NONZERO, f"exit={kod}", f"exit={NONZERO}")
    doma("nonzero/bevarad", b"7" in ut, ut.decode()[:60], "koden 7 bevarad i orsaken")
    doma("nonzero/ej-timeout", b"timeout" not in ut.lower(), ut.decode()[:60],
         "får inte klassas som timeout")

    kod, ut, _ = kor("30", str(kat / "finns-inte.sh"))
    doma("launch_failed/kod", kod == LAUNCH, f"exit={kod}", f"exit={LAUNCH}")
    doma("launch_failed/orsak", ut.strip() != b"", "tom stdout", "orsaken på stdout")

    # --- ANROPSFEL: klassade, aldrig stackspår ---
    anropsfall = [
        ("saknat-kuvert", [str(ws), str(kat / "nix.json"), "5", "--", "/bin/echo", "x"]),
        ("saknat-ws", [str(kat / "ingen-ws"), str(kuv), "5", "--", "/bin/echo", "x"]),
        ("timeout-noll", [str(ws), str(kuv), "0", "--", "/bin/echo", "x"]),
        ("timeout-text", [str(ws), str(kuv), "snart", "--", "/bin/echo", "x"]),
        ("utan-delare", [str(ws), str(kuv), "5", "/bin/echo", "x"]),
        ("tomt-kommando", [str(ws), str(kuv), "5", "--"]),
        ("trasigt-kuvert", [str(ws), str(kat / "var.sh"), "5", "--", "/bin/echo", "x"]),
    ]
    for namn, argv in anropsfall:
        r = subprocess.run([str(CLI), "run", *argv], capture_output=True, text=True,
                           cwd=ROT, timeout=60)
        doma(namn, r.returncode == ANROP, f"exit={r.returncode}", f"exit={ANROP}")
        doma(f"{namn}/orsak", r.stdout.strip() != "", "tom stdout", "orsaken på stdout")
        doma(f"{namn}/stderr", r.stderr.strip() == "", r.stderr.strip()[:50], "tom stderr")
        doma(f"{namn}/traceback", "traceback" not in (r.stdout + r.stderr).lower(),
             "traceback", "aldrig traceback")

    subprocess.run(["rm", "-rf", str(kat)])
    print(f"\n{ratt} rätt, {fel} fel")
    return 1 if fel else 0


if __name__ == "__main__":
    sys.exit(main())
