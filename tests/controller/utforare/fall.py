#!/usr/bin/env python3.12
"""tests/controller/utforare/fall.py — kontraktsfall för controller/utforare/cli.

    python3.12 tests/controller/utforare/fall.py     exit 0 = alla fall håller

Det här är INTE exitgrinden. `verify/bin/h-012-exit` är grinden och ägs av
människan; den här filen täcker vad grinden inte når och får aldrig åberopas
som bevis för att skiva 10 är klar.

Vad grinden inte når: anropsfelens klassning, inklusive workspace-vakten
(`git -C ""` hade träffat anroparens cwd — i drift reporoten) · de exakta
exitkoderna (6 ingen kandidat, 7 gitfel, 8 internt, vidarebefordrade 4/5 från
h-009) · gitfel-ledet (trasig gitdir får inte klassas "inga ändrade filer") ·
binär sessionsstdout (h-009 vidarebefordrar bytes oförändrade — domen får
aldrig krascha på dem) · en session som committar SJÄLV (rent träd + flyttad
HEAD får inte ge orsaken "inga ändrade filer") · fast identitet även när
GIT_AUTHOR_*/GIT_COMMITTER_* står i miljön (env slår config, så `-c` ensamt
räcker inte) · värdkonfig `status.showUntrackedFiles=no` får inte gömma nya
filer ur domen · enbart ignorerade filer ger failure · toppvakten (internt
fel klassas på stdout, aldrig stackspår) · rapportens byteform: exakt en rad.

Workspacet är här ett FRISTÅENDE temp-repo, med avsikt: utföraren arbetar
uteslutande `git -C <ws>`. Delad objektdatabas med roten är h-006:s behov
och prövas av grinden via h-005; ett fristående repo håller fallen hermetiska
och rör aldrig rotens `.git`.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROT = Path(__file__).resolve().parents[3]
CLI = ROT / "controller/utforare/cli"
ANROP, NONZERO, TIMEOUT, INGEN_KANDIDAT, GITFEL, INTERNT = 1, 4, 5, 6, 7, 8

SKRIPT = {
    "andra.sh": '#!/usr/bin/env bash\necho ny > fil.txt\n',
    "klagar.sh": '#!/usr/bin/env bash\necho "SESSIONSFEL: kvoten tog slut"\n',
    "tyst.sh": '#!/usr/bin/env bash\nexit 0\n',
    "skrap.sh": '#!/usr/bin/env bash\necho x > skrap.tmp\n',
    "faller.sh": '#!/usr/bin/env bash\nexit 9\n',
    "sover.sh": '#!/usr/bin/env bash\nsleep 120\n',
    "binar-andra.sh": '#!/usr/bin/env bash\nprintf "\\377\\376"\necho ny > fil.txt\n',
    "binar-ren.sh": '#!/usr/bin/env bash\nprintf "\\377\\376"\n',
    "sjalvcommit.sh": ('#!/usr/bin/env bash\necho x > egen.txt\ngit add egen.txt\n'
                       'git -c user.name=sessionen -c user.email=s@s '
                       '-c commit.gpgsign=false commit -q -m egen\n'),
}


def main() -> int:
    if not os.access(CLI, os.X_OK):
        print(f"FAIL  {CLI} saknas eller är inte körbar")
        return 1

    kat = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR") or "/tmp"))
    for namn, kropp in SKRIPT.items():
        p = kat / namn
        p.write_text(kropp, encoding="utf-8")
        os.chmod(p, 0o755)
    kuv = kat / "kuvert.json"
    kuv.write_text('{"task_id": "h-012-fall", "spec_sha256": "fall"}\n', encoding="utf-8")

    def nytt_ws(namn: str) -> Path:
        ws = kat / namn
        ws.mkdir()
        for argv in (["init", "-q"],
                     ["-c", "user.name=fixtur", "-c", "user.email=fixtur@test",
                      "-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m", "bas"]):
            subprocess.run(["git", "-C", str(ws), *argv], capture_output=True, check=True)
        (ws / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(ws), "add", ".gitignore"], capture_output=True)
        subprocess.run(["git", "-C", str(ws), "-c", "user.name=fixtur",
                        "-c", "user.email=fixtur@test", "-c", "commit.gpgsign=false",
                        "commit", "-q", "-m", "ignorlista"], capture_output=True)
        return ws

    def g(ws: Path, *argv: str) -> str:
        return subprocess.run(["git", "-C", str(ws), *argv],
                              capture_output=True, text=True).stdout.strip()

    ratt = fel = 0

    def doma(namn: str, villkor: bool, sett: str, krav: str) -> None:
        nonlocal ratt, fel
        if villkor:
            ratt += 1
        else:
            fel += 1
            print(f"FAIL  {namn} — krav: {krav} · sett: {sett}")

    def kor(*argv: str, miljo: dict | None = None) -> tuple[int, str, str]:
        r = subprocess.run([str(CLI), *argv], capture_output=True, text=True,
                           errors="replace", cwd=ROT, env=miljo, timeout=90)
        return r.returncode, r.stdout, r.stderr.strip()

    # --- ANROPSFEL: klassade, aldrig stackspår ---
    ws0 = nytt_ws("ws-anrop")
    anropsfall = [
        ("fel-verb", ["spring", str(ws0), str(kuv), "5", "--", "/bin/echo"]),
        ("utan-delare", ["kor", str(ws0), str(kuv), "5", "/bin/echo"]),
        ("for-fa-argument", ["kor", str(ws0), "5", "--", "/bin/echo"]),
        ("tomt-kommando", ["kor", str(ws0), str(kuv), "5", "--"]),
    ]
    for namn, argv in anropsfall:
        kod, ut, err = kor(*argv)
        doma(namn, kod == ANROP, f"exit={kod}", f"exit={ANROP}")
        doma(f"{namn}/orsak", ut.strip() != "", "tom stdout", "orsaken på stdout")
        doma(f"{namn}/traceback", "traceback" not in (ut + err).lower(),
             "traceback", "aldrig traceback")

    # Workspace-vakten: git -C "" hade träffat anroparens cwd — i drift reporoten.
    rot_fore = subprocess.run(["git", "-C", str(ROT), "status", "--porcelain"],
                              capture_output=True, text=True).stdout
    kod, ut, _ = kor("kor", "", str(kuv), "5", "--", "/bin/echo", "x")
    doma("tomt-ws/kod", kod == ANROP, f"exit={kod}", f"exit={ANROP}")
    doma("tomt-ws/namnger", "workspace" in ut, ut.strip()[:60], "orsaken namnger workspacet")
    rot_efter = subprocess.run(["git", "-C", str(ROT), "status", "--porcelain"],
                               capture_output=True, text=True).stdout
    doma("tomt-ws/roten-orord", rot_fore == rot_efter, "status ändrades", "reporoten orörd")

    vanlig = kat / "ws-utan-git"
    vanlig.mkdir()
    kod, ut, _ = kor("kor", str(vanlig), str(kuv), "5", "--", "/bin/echo", "x")
    doma("ws-utan-git/kod", kod == ANROP, f"exit={kod}",
         f"exit={ANROP} — katalog utan .git är inget workspace")

    # h-009:s eget anropsfel (obefintligt workspace) stoppas redan av vår vakt.
    kod, ut, _ = kor("kor", str(kat / "finns-inte"), str(kuv), "5", "--", "/bin/echo", "x")
    doma("saknat-ws/kod", kod == ANROP, f"exit={kod}", f"exit={ANROP}")
    doma("saknat-ws/orsak", ut.strip() != "", "tom stdout", "orsaken på stdout")

    # --- KANDIDATEN: exakt en rad, git är källan ---
    ws = nytt_ws("ws-arlig")
    kod, ut, err = kor("kor", str(ws), str(kuv), "30", "--", str(kat / "andra.sh"))
    doma("kandidat/kod", kod == 0, f"exit={kod}", "exit=0")
    doma("kandidat/en-rad", ut.endswith("\n") and ut.count("\n") == 1, repr(ut[:70]),
         "EXAKT en rad på stdout — h-006 parsar hela strömmen")
    doma("kandidat/stderr", err == "", err[:60], "tom stderr")
    try:
        rapport = json.loads(ut)
    except Exception:
        rapport = {}
    doma("kandidat/status", rapport.get("status") == "candidate",
         str(rapport.get("status")), "status=candidate")
    doma("kandidat/sha-ur-git", rapport.get("candidate_sha") == g(ws, "rev-parse", "HEAD"),
         str(rapport.get("candidate_sha"))[:12], "candidate_sha = workspacets HEAD")
    doma("kandidat/files", rapport.get("files") == ["fil.txt"],
         str(rapport.get("files")), "files exakt ur git show, sorterade")

    # --- FAST IDENTITET: även när miljön försöker bestämma ---
    ws = nytt_ws("ws-identitet")
    miljo = dict(os.environ,
                 GIT_AUTHOR_NAME="Intrang", GIT_AUTHOR_EMAIL="intrang@test",
                 GIT_COMMITTER_NAME="Intrang", GIT_COMMITTER_EMAIL="intrang@test")
    kod, ut, _ = kor("kor", str(ws), str(kuv), "30", "--", str(kat / "andra.sh"), miljo=miljo)
    identitet = g(ws, "log", "-1", "--format=%an %ae %cn %ce")
    doma("identitet/fast", identitet == "nortropic-utforare utforare@nortropic "
                                        "nortropic-utforare utforare@nortropic",
         identitet, "GIT_AUTHOR_*/GIT_COMMITTER_* i miljön får inte vinna över den fasta")

    # --- INGEN KANDIDAT: failure utan commit, orsak ordagrant eller namngivet steg ---
    ws = nytt_ws("ws-klagar")
    fore = g(ws, "rev-list", "--count", "HEAD")
    kod, ut, _ = kor("kor", str(ws), str(kuv), "30", "--", str(kat / "klagar.sh"))
    doma("klagar/kod", kod == INGEN_KANDIDAT, f"exit={kod}", f"exit={INGEN_KANDIDAT}")
    doma("klagar/ordagrant", "SESSIONSFEL: kvoten tog slut" in ut, ut.strip()[:70],
         "sessionens text ordagrant i orsaken")
    doma("klagar/ingen-commit", g(ws, "rev-list", "--count", "HEAD") == fore,
         g(ws, "rev-list", "--count", "HEAD"), f"{fore} commits, oförändrat")

    ws = nytt_ws("ws-tyst")
    kod, ut, _ = kor("kor", str(ws), str(kuv), "30", "--", str(kat / "tyst.sh"))
    doma("tyst/kod", kod == INGEN_KANDIDAT, f"exit={kod}", f"exit={INGEN_KANDIDAT}")
    doma("tyst/namnger-steget", ut.strip() == "inga ändrade filer i workspacet",
         ut.strip()[:70], "tom orsak sväljs inte — steget namnges")

    # Enbart ignorerade filer: domen läser porcelain, inte filsystemet.
    ws = nytt_ws("ws-skrap")
    fore = g(ws, "rev-list", "--count", "HEAD")
    kod, ut, _ = kor("kor", str(ws), str(kuv), "30", "--", str(kat / "skrap.sh"))
    doma("ignorerat/kod", kod == INGEN_KANDIDAT, f"exit={kod}",
         f"exit={INGEN_KANDIDAT} — en ignorerad fil är ingen ändring")
    doma("ignorerat/ingen-commit", g(ws, "rev-list", "--count", "HEAD") == fore,
         g(ws, "rev-list", "--count", "HEAD"), "ingen commit")

    # Sessionen committar SJÄLV: rent träd + flyttad HEAD ljuger inte "inga ändringar".
    ws = nytt_ws("ws-sjalvcommit")
    fore = int(g(ws, "rev-list", "--count", "HEAD"))
    kod, ut, _ = kor("kor", str(ws), str(kuv), "30", "--", str(kat / "sjalvcommit.sh"))
    doma("sjalvcommit/kod", kod == INGEN_KANDIDAT, f"exit={kod}", f"exit={INGEN_KANDIDAT}")
    doma("sjalvcommit/namnger", "committade själv" in ut, ut.strip()[:70],
         "orsaken namnger självcommitten, inte 'inga ändrade filer'")
    doma("sjalvcommit/ingen-egen", int(g(ws, "rev-list", "--count", "HEAD")) == fore + 1,
         g(ws, "rev-list", "--count", "HEAD"),
         f"{fore + 1} commits — sessionens egen, ingen från utföraren")

    # Värdkonfig får inte gömma nya filer ur domen (status.showUntrackedFiles=no).
    ws = nytt_ws("ws-gomd-config")
    subprocess.run(["git", "-C", str(ws), "config", "status.showUntrackedFiles", "no"],
                   capture_output=True)
    kod, ut, _ = kor("kor", str(ws), str(kuv), "30", "--", str(kat / "andra.sh"))
    doma("gomd-config/kandidat", kod == 0, f"exit={kod} [{ut.strip()[:50]}]",
         "ny fil ger kandidat även när värdkonfig gömmer otrackat")

    # --- BINÄR SESSIONSSTDOUT: domen kraschar aldrig på sessionens bytes ---
    ws = nytt_ws("ws-binar-andra")
    kod, ut, err = kor("kor", str(ws), str(kuv), "30", "--", str(kat / "binar-andra.sh"))
    doma("binar-andring/kandidat", kod == 0, f"exit={kod} err=[{err[:40]}]",
         "ändrade filer ger kandidat oavsett vad sessionen skrev på stdout")
    ws = nytt_ws("ws-binar-ren")
    kod, ut, err = kor("kor", str(ws), str(kuv), "30", "--", str(kat / "binar-ren.sh"))
    doma("binar-ren/kod", kod == INGEN_KANDIDAT, f"exit={kod}", f"exit={INGEN_KANDIDAT}")
    doma("binar-ren/ingen-krasch", "traceback" not in (ut + err).lower()
         and ut.startswith("inga ändrade filer"), f"[{ut.strip()[:50]}] err=[{err[:40]}]",
         "failure-klass på stdout, aldrig UnicodeDecodeError")

    # --- H-009:S KLASSER: vidarebefordrade oförändrade, skilda koder ---
    ws = nytt_ws("ws-faller")
    kod, ut, _ = kor("kor", str(ws), str(kuv), "30", "--", str(kat / "faller.sh"))
    doma("nonzero/kod", kod == NONZERO, f"exit={kod}", f"exit={NONZERO} som h-009")
    doma("nonzero/klass", "nonzero_exit" in ut, ut.strip()[:60], "klassen på stdout")
    doma("nonzero/bevarad", "9" in ut, ut.strip()[:60], "koden 9 bevarad i orsaken")

    ws = nytt_ws("ws-sover")
    kod, ut, _ = kor("kor", str(ws), str(kuv), "1", "--", str(kat / "sover.sh"))
    doma("timeout/kod", kod == TIMEOUT, f"exit={kod}", f"exit={TIMEOUT} som h-009")
    doma("timeout/klass", "timeout" in ut.lower(), ut.strip()[:60], "klassen på stdout")

    # --- GITFEL: trasig gitdir får aldrig klassas "inga ändrade filer" ---
    trasig = kat / "ws-trasig"
    trasig.mkdir()
    (trasig / ".git").write_text("gitdir: /finns/inte\n", encoding="utf-8")
    kod, ut, _ = kor("kor", str(trasig), str(kuv), "30", "--", str(kat / "andra.sh"))
    doma("gitfel/kod", kod == GITFEL, f"exit={kod}", f"exit={GITFEL}")
    doma("gitfel/namnger", ut.startswith("gitfel:"), ut.strip()[:60],
         "orsaken namnger git-ledet, inte 'inga ändrade filer'")

    # --- TOPPVAKTEN: internt fel klassas på stdout, aldrig stackspår ---
    bindir = kat / "bin"
    bindir.mkdir()
    pyt = shutil.which("python3.12")
    os.symlink(pyt, bindir / "python3.12")
    ws = nytt_ws("ws-toppvakt")
    kod, ut, err = kor("kor", str(ws), str(kuv), "5", "--", "/bin/echo", "x",
                       miljo=dict(os.environ, PATH=str(bindir)))
    doma("toppvakt/kod", kod == INTERNT, f"exit={kod}", f"exit={INTERNT}")
    doma("toppvakt/klass", ut.startswith("internt fel:"), ut.strip()[:60],
         "klassen internt fel på stdout")
    doma("toppvakt/ingen-traceback", "traceback" not in err.lower(), err[:60],
         "stderr utan stackspår")

    subprocess.run(["rm", "-rf", str(kat)])
    print(f"\n{ratt} rätt, {fel} fel")
    return 1 if fel else 0


if __name__ == "__main__":
    sys.exit(main())
