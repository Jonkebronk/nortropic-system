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

Sist ligger två MÄTTA MEN OFARLIGA kanter — den citerade formen för
icke-ASCII-sökvägar i `files`, och gitlinken för ett nästlat repo. De är
nedskrivna, inte lagade: fallen påstår inte att beteendet är önskat, bara
att det är detta beteende komponenten HAR. Faller de har beteendet flyttat
sig, och då ska det vara ett beslut och inte en slump.

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
    "icke-ascii.sh": '#!/usr/bin/env bash\necho ny > "filå.txt"\n',
    "nastlat-repo.sh": ('#!/usr/bin/env bash\nmkdir nastlat\ncd nastlat\ngit init -q\n'
                        'echo inre > inre.txt\ngit add inre.txt\n'
                        'git -c user.name=sessionen -c user.email=s@s '
                        '-c commit.gpgsign=false commit -q -m inre\n'),
}


def citerad(sokvag: str) -> str:
    """Gits egen citering av en sökväg (core.quotePath): en C-sträng där varje
    byte utanför ASCII skrivs som oktal escape. Räcker för fixturens namn —
    gits fulla form escapar även `"` och `\\`, som fixturen inte innehåller."""
    kropp = "".join(chr(b) if 0x20 <= b < 0x7f else f"\\{b:03o}"
                    for b in sokvag.encode("utf-8"))
    return f'"{kropp}"'


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

    # --- MÄTTA MEN OFARLIGA KANTER: nedskrivna, inte lagade ---

    # `git show --name-only` får varken -z eller --no-quotepath, så files bär
    # gits CITERADE form för sökvägar utanför ASCII — en C-sträng med oktala
    # escapes, inte den verkliga sökvägen. core.quotePath sätts LOKALT i
    # workspacet åt båda hållen: värdens globala config får aldrig vara det
    # som avgör vad fallet mäter.
    ws = nytt_ws("ws-icke-ascii")
    subprocess.run(["git", "-C", str(ws), "config", "core.quotePath", "true"],
                   capture_output=True)
    kod, ut, err = kor("kor", str(ws), str(kuv), "30", "--", str(kat / "icke-ascii.sh"))
    doma("citerad/kandidat", kod == 0, f"exit={kod} [{ut.strip()[:50]}]",
         "ett icke-ASCII-filnamn hindrar inte kandidaten — bara sökvägens form")
    try:
        rapport = json.loads(ut)
    except Exception:
        rapport = {}
    # Rå form ur SAMMA commit: skillnaden mot files är enbart citeringen, så
    # ingen normalisering i filsystemet kan förklara den.
    rakt = g(ws, "-c", "core.quotePath=false", "show", "--name-only", "--format=", "HEAD")
    doma("citerad/form", rapport.get("files") == [citerad(rakt)], str(rapport.get("files")),
         f"files bär gits citerade form {citerad(rakt)!r}, inte {rakt!r}")
    namn = (rapport.get("files") or [""])[0]
    doma("citerad/oanvandbar", (ws / rakt).exists() and not (ws / namn).exists(),
         f"{namn!r} öppningsbar={(ws / namn).exists()}",
         "den citerade strängen är INGEN öppningsbar sökväg — den råa är det")

    # Formen följer workspacets config: utföraren varken låser eller upphäver den.
    ws = nytt_ws("ws-icke-ascii-rak")
    subprocess.run(["git", "-C", str(ws), "config", "core.quotePath", "false"],
                   capture_output=True)
    kod, ut, _ = kor("kor", str(ws), str(kuv), "30", "--", str(kat / "icke-ascii.sh"))
    try:
        namn = (json.loads(ut).get("files") or [""])[0]
    except Exception:
        namn = ""
    doma("citerad/foljer-config", namn == rakt, repr(namn),
         f"core.quotePath=false i workspacet ger den råa sökvägen {rakt!r}")
    doma("citerad/rak-oppningsbar", namn != "" and (ws / namn).exists(), repr(namn),
         "med rak form pekar files på en fil som går att öppna")

    # Skapar sessionen ett NÄSTLAT git-repo stagar `git add -A` det som en
    # gitlink (mode 160000). Kandidaten föds ändå, files namnger katalogen —
    # och målcommiten finns bara i det inre repot, aldrig i den objektdatabas
    # kandidat-SHA:t lämnas vidare ur.
    ws = nytt_ws("ws-nastlat")
    kod, ut, err = kor("kor", str(ws), str(kuv), "30", "--", str(kat / "nastlat-repo.sh"))
    doma("gitlink/kandidat", kod == 0, f"exit={kod} [{ut.strip()[:50]}]",
         "ett nästlat repo stoppar inte kandidaten")
    try:
        rapport = json.loads(ut)
    except Exception:
        rapport = {}
    trad = g(ws, "ls-tree", "-r", "HEAD")
    doma("gitlink/files", rapport.get("files") == ["nastlat"] and "inre.txt" not in trad,
         f"files={rapport.get('files')} träd=[{trad[:50]}]",
         "files namnger KATALOGEN — filen sessionen skrev i den når aldrig trädet")
    rad = g(ws, "ls-tree", "HEAD", "nastlat")
    doma("gitlink/mode", rad.startswith("160000 commit"), rad[:40] or "(tom)",
         "stagad som gitlink, mode 160000 — inte som blobbar")
    # `rev-parse` EKAR sitt argument när sökvägen inte finns i trädet, så
    # "saknas ur databasen" räcker inte som krav — utan gitlink hade det varit
    # uppfyllt av tomhet. Målet måste ha LÖST till ett objekt-id först.
    mal = g(ws, "rev-parse", "HEAD:nastlat")
    loste = len(mal) == 40 and all(c in "0123456789abcdef" for c in mal)
    saknas = subprocess.run(["git", "-C", str(ws), "cat-file", "-e", mal or "HEAD"],
                            capture_output=True).returncode
    doma("gitlink/mal-saknas", loste and saknas != 0,
         f"mål={mal[:14]!r} löste={loste} cat-file -e gav {saknas}",
         "gitlinken löser till ett objekt-id som INTE finns i workspacets objektdatabas")
    inre = g(ws / "nastlat", "rev-parse", "HEAD")
    doma("gitlink/mal-i-inre", loste and mal == inre, f"{mal[:14]} mot {inre[:14]}",
         "commiten finns bara i det inre repot — och det är DEN som pekas ut")
    doma("gitlink/tyst", err == "", err[:60],
         "gits `add -A` varnar om inbäddat arkiv på stderr — utförarens fångst "
         "sväljer den, och inget varnar anroparen")

    subprocess.run(["rm", "-rf", str(kat)])
    print(f"\n{ratt} rätt, {fel} fel")
    return 1 if fel else 0


if __name__ == "__main__":
    sys.exit(main())
