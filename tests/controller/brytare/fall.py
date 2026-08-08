#!/usr/bin/env python3.12
"""tests/controller/brytare/fall.py — kontraktsfall för controller/brytare/cli.

    python3.12 tests/controller/brytare/fall.py     exit 0 = alla fall håller

Det här är INTE exitgrinden. `verify/bin/h-013-exit` är grinden och ägs av
människan; den här filen täcker vad grinden inte når och får aldrig åberopas
som bevis för att skiva 11 är klar.

Vad grinden inte når: anropsfelens klassning (eget och utforarens — bägge
exit 1, förbrukar inte, fingerprintas inte, aldrig stackspår) · klasserna
3/5/6/7/8 vidarebefordrade med sina exakta koder (grinden mäter bara 4) ·
ordagrann vidarebefordran bevisad mot en direkt utforarkörning, med
fingerprintraden som enda tillägg och sist · tröskel 1 öppnar på första
felet, med radordningen failure → fingerprint → "brytare öppen" sist ·
sifferföljdsnormalisering över timeoutvärdet, mätt på tröskelbeteende ·
citerad sökväg (gits/Pythons form) med bokstavsvarians är samma
fingerprint · ordskillnad i klass 6-orsaken ger två fingerprints ·
PROCESSENS exitkod i den uppmätta kanalformen: grindens K15 mäter att
olika exitkod ger olika fingerprint, här ligger motpolen (samma kod är
fortfarande EN klass, även när den kastade stdouten skiljer sig),
fingerprintens form, signalkodernas minustecken och återfallet `-` för
klasser som inte bär någon processkod · kvotmatchning på
klass 6 (mönstret möter hela failuretexten, inte bara nonzero-vägen) · en
mönsterfil med enbart tomma och blanka rader kvotklassar ingenting — en
blankrad som substrängsmönster hade matchat nästan allt · andra mönstret i
filen räcker · status-verbets form: färskt tillstånd utan att katalogen
skapas, räknare och fingerprints efter körningar · trasig tillståndsfil är
ett fel, aldrig ett färskt tillstånd och startar aldrig kommandot (kanarie)
— en öppen brytare får inte nollställas tyst eller köras förbi · toppvakten (utforaren saknas → internt fel på stdout,
aldrig stackspår) · exitkod 2 aldrig, svept över samtliga fall.

Workspaces är FRISTÅENDE temp-repon, med avsikt (h-012-formen): brytaren
arbetar via utforaren som arbetar uteslutande `git -C <ws>`. Delad
objektdatabas med roten är h-006:s behov och prövas av grinden via h-005;
fristående repon håller fallen hermetiska och rör aldrig rotens `.git`.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROT = Path(__file__).resolve().parents[3]
CLI = ROT / "controller/brytare/cli"
UTFORARE = ROT / "controller/utforare/cli"
ANROP, LAUNCH, NONZERO, TIMEOUT, INGEN_KANDIDAT, GITFEL, INTERNT = 1, 3, 4, 5, 6, 7, 8
OPPEN, BUDGET_SLUT = 9, 10

SKRIPT = {
    "andra.sh": '#!/usr/bin/env bash\necho ny > fil.txt\n',
    "tyst.sh": '#!/usr/bin/env bash\nexit 0\n',
    "klagar-kvot.sh": '#!/usr/bin/env bash\necho "kvoten tog slut"\n',
    "klagar-db.sh": '#!/usr/bin/env bash\necho "databasen svarade inte"\n',
    "faller9.sh": '#!/usr/bin/env bash\necho "provfel i steget" >&2\nexit 9\n',
    "sover.sh": '#!/usr/bin/env bash\nsleep 120\n',
    # Citerade vägar i gits/Pythons standardform, bokstavsvarians (AAA/BBB) som
    # siffernormaliseringen aldrig kan jämna ut — endast vägersättningen kan.
    "fel-cit-a.sh": '#!/usr/bin/env bash\n'
                    'echo "kan inte öppna \'/tmp/provAAA/lager/l.lock\': upptagen" >&2\nexit 7\n',
    "fel-cit-b.sh": '#!/usr/bin/env bash\n'
                    'echo "kan inte öppna \'/tmp/provBBB/lager/l.lock\': upptagen" >&2\nexit 7\n',
    # DEN UPPMÄTTA KANALFORMEN (smoke 2026-08-08): allt på STDOUT, TOM stderr.
    # h-009 KASTAR sessionens stdout vid nonzero, så det enda som når brytaren
    # är "nonzero_exit: processen avslutade med kod N" — processkoden är felets
    # enda bärare. proc1-a/proc1-b skiljer sig ENDAST i den kastade texten,
    # proc64 i koden. Signalfixturerna ger negativa koder (-15 / -9).
    "proc1-a.sh": '#!/usr/bin/env bash\necho "3 tester föll i sviten"\nexit 1\n',
    "proc1-b.sh": '#!/usr/bin/env bash\necho "verktyget saknas i PATH"\nexit 1\n',
    "proc64.sh": '#!/usr/bin/env bash\necho "usage: worker [flaggor]"\nexit 64\n',
    "sig-term.sh": '#!/usr/bin/env bash\nkill -s TERM $$\n',
    "sig-kill.sh": '#!/usr/bin/env bash\nkill -s KILL $$\n',
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
    kuv.write_text('{"task_id": "h-013-fall", "spec_sha256": "fall"}\n', encoding="utf-8")

    def nytt_ws(namn: str) -> Path:
        ws = kat / namn
        ws.mkdir()
        for argv in (["init", "-q"],
                     ["-c", "user.name=fixtur", "-c", "user.email=fixtur@test",
                      "-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m", "bas"]):
            subprocess.run(["git", "-C", str(ws), *argv], capture_output=True, check=True)
        return ws

    ratt = fel = 0
    KODER: list[int] = []

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
        KODER.append(r.returncode)
        return r.returncode, r.stdout, r.stderr.strip()

    def status(kat_arg: str) -> dict:
        r = subprocess.run([str(CLI), "status", kat_arg], capture_output=True,
                           text=True, cwd=ROT, timeout=30)
        KODER.append(r.returncode)
        try:
            return json.loads(r.stdout)
        except ValueError:
            return {}

    def fprader(ut: str) -> list[str]:
        return [r for r in ut.splitlines() if r.startswith("fingerprint: ")]

    # Delat failure-workspace: fixturerna här lämnar det rent.
    FW = nytt_ws("ws-fel")

    # --- ANROPSFEL, EGNA: klassade, aldrig stackspår, förbrukar inte ---
    d0 = str(kat / "d-anrop")
    anropsfall = [
        ("fel-verb", ["spring", d0, "h-x", "5", "2", str(FW), str(kuv), "5", "--", "/bin/echo"]),
        ("utan-delare", ["kor", d0, "h-x", "5", "2", str(FW), str(kuv), "5", "/bin/echo"]),
        ("for-fa-argument", ["kor", d0, "h-x", "5", str(FW), str(kuv), "5", "--", "/bin/echo"]),
        ("tomt-kommando", ["kor", d0, "h-x", "5", "2", str(FW), str(kuv), "5", "--"]),
        ("budget-icke-tal", ["kor", d0, "h-x", "fem", "2", str(FW), str(kuv), "5", "--", "/bin/echo"]),
        ("budget-negativ", ["kor", d0, "h-x", "-1", "2", str(FW), str(kuv), "5", "--", "/bin/echo"]),
        ("troskel-noll", ["kor", d0, "h-x", "5", "0", str(FW), str(kuv), "5", "--", "/bin/echo"]),
        ("troskel-icke-tal", ["kor", d0, "h-x", "5", "x", str(FW), str(kuv), "5", "--", "/bin/echo"]),
        ("status-utan-katalog", ["status"]),
        ("status-extra-argument", ["status", d0, "x"]),
    ]
    for namn, argv in anropsfall:
        kod, ut, err = kor(*argv)
        doma(namn, kod == ANROP, f"exit={kod}", f"exit={ANROP}")
        doma(f"{namn}/orsak", ut.strip() != "", "tom stdout", "orsaken på stdout")
        doma(f"{namn}/traceback", "traceback" not in (ut + err).lower(),
             "traceback", "aldrig traceback")
    st = status(d0)
    doma("anropsfel/forbrukar-inte", st.get("forbrukat") == 0 and st.get("fingerprints") == {},
         str(st), "egna anropsfel förbrukar inte och fingerprintas inte")

    # --- ANROPSFEL, UTFORARENS: exit 1 vidarebefordrad, ingen fingerprintrad ---
    utan_git = kat / "ws-utan-git"
    utan_git.mkdir()
    d1 = str(kat / "d-ufel")
    kod, ut, _ = kor("kor", d1, "h-x", "5", "2", str(utan_git), str(kuv), "5", "--", "/bin/echo", "x")
    doma("u-anropsfel/kod", kod == ANROP, f"exit={kod}", f"exit={ANROP} — utforarens anropsfel vidarebefordras")
    doma("u-anropsfel/orsak", "workspace" in ut, ut.strip()[:60], "utforarens orsak ordagrant")
    doma("u-anropsfel/ingen-fingerprint", fprader(ut) == [], ut.strip()[:60],
         "anropsfel fingerprintas aldrig")
    st = status(d1)
    doma("u-anropsfel/forbrukar-inte", st.get("forbrukat") == 0 and st.get("fingerprints") == {},
         str(st), "utforarens anropsfel förbrukar inte")

    # --- KANDIDATEN: exakt en rad, aldrig extra, räknas i budgeten ---
    ws = nytt_ws("ws-arlig")
    dk = str(kat / "d-kandidat")
    kod, ut, err = kor("kor", dk, "h-x", "5", "3", str(ws), str(kuv), "30", "--", str(kat / "andra.sh"))
    doma("kandidat/kod", kod == 0, f"exit={kod} [{ut.strip()[:50]}]", "exit=0")
    doma("kandidat/en-rad", ut.endswith("\n") and ut.count("\n") == 1, repr(ut[:70]),
         "EXAKT en rad på stdout — rapporten oförändrad, aldrig extra rader")
    doma("kandidat/stderr", err == "", err[:60], "tom stderr")
    try:
        rapport = json.loads(ut)
    except ValueError:
        rapport = {}
    doma("kandidat/status", rapport.get("status") == "candidate",
         str(rapport.get("status")), "status=candidate — h-006-parsbar JSON")
    st = status(dk)
    doma("kandidat/raknas", st.get("forbrukat") == 1, str(st.get("forbrukat")),
         "succén räknas i budgeten")
    doma("kandidat/ofingeprintad", st.get("fingerprints") == {}, str(st.get("fingerprints")),
         "en kandidat fingerprintas aldrig")

    # --- ORDAGRANN VIDAREBEFORDRAN: klass 6 mätt mot en direkt utforarkörning ---
    ru = subprocess.run([str(UTFORARE), "kor", str(FW), str(kuv), "30", "--", str(kat / "tyst.sh")],
                        capture_output=True, text=True, cwd=ROT, timeout=90)
    d6 = str(kat / "d-tyst")
    kod, ut, _ = kor("kor", d6, "h-x", "9", "9", str(FW), str(kuv), "30", "--", str(kat / "tyst.sh"))
    doma("klass6/kod", kod == INGEN_KANDIDAT, f"exit={kod}",
         f"exit={INGEN_KANDIDAT} — utforarens kod vidarebefordras exakt")
    doma("klass6/ordagrant", ut.startswith(ru.stdout) and ru.stdout.strip() != "",
         repr(ut[:70]), "börjar med utforarens stdout ordagrant")
    rest = ut[len(ru.stdout):]
    doma("klass6/fingerprint-sist", rest.startswith("fingerprint: ") and rest.count("\n") == 1,
         repr(rest[:70]), "enda tillägget är fingerprintraden, sist")

    # --- KLASSERNA 3/5/7/8: vidarebefordrade med sina exakta koder + fingerprint ---
    kod, ut, _ = kor("kor", str(kat / "d-l"), "h-x", "9", "9", str(FW), str(kuv), "30",
                     "--", str(kat / "finns-inte.sh"))
    doma("klass3/kod", kod == LAUNCH, f"exit={kod}", f"exit={LAUNCH} launch_failed")
    doma("klass3/klass", "launch_failed" in ut, ut.strip()[:60], "klassen ordagrant")
    doma("klass3/fingerprint", len(fprader(ut)) == 1, ut.strip()[:60], "fingerprintrad finns")

    kod, ut, _ = kor("kor", str(kat / "d-n"), "h-x", "9", "9", str(FW), str(kuv), "30",
                     "--", str(kat / "faller9.sh"))
    doma("klass4/kod", kod == NONZERO, f"exit={kod}", f"exit={NONZERO} nonzero_exit")
    doma("klass4/orsak", "provfel" in ut and "9" in ut, ut.strip()[:70],
         "sessionens stderr och koden 9 bevarade i orsaken")

    kod, ut, _ = kor("kor", str(kat / "d-t"), "h-x", "9", "9", str(FW), str(kuv), "1",
                     "--", str(kat / "sover.sh"))
    doma("klass5/kod", kod == TIMEOUT, f"exit={kod}", f"exit={TIMEOUT} timeout")
    doma("klass5/klass", "timeout" in ut.lower(), ut.strip()[:60], "klassen ordagrant")
    doma("klass5/fingerprint", len(fprader(ut)) == 1, ut.strip()[:60], "fingerprintrad finns")

    trasig = kat / "ws-trasig"
    trasig.mkdir()
    (trasig / ".git").write_text("gitdir: /finns/inte\n", encoding="utf-8")
    kod, ut, _ = kor("kor", str(kat / "d-g"), "h-x", "9", "9", str(trasig), str(kuv), "30",
                     "--", str(kat / "andra.sh"))
    doma("klass7/kod", kod == GITFEL, f"exit={kod}", f"exit={GITFEL} gitfel")
    doma("klass7/klass", "gitfel" in ut, ut.strip()[:60], "klassen ordagrant")
    doma("klass7/fingerprint", len(fprader(ut)) == 1, ut.strip()[:60], "fingerprintrad finns")

    # Klass 8 vidarebefordrad: PATH med enbart python3.12 → utforarens git
    # saknas → utforarens toppvakt ger internt fel, brytaren bär koden vidare.
    bindir = kat / "bin"
    bindir.mkdir()
    os.symlink(shutil.which("python3.12"), bindir / "python3.12")
    ws = nytt_ws("ws-klass8")
    kod, ut, err = kor("kor", str(kat / "d-i"), "h-x", "9", "9", str(ws), str(kuv), "30",
                       "--", "/bin/echo", "x", miljo=dict(os.environ, PATH=str(bindir)))
    doma("klass8/kod", kod == INTERNT, f"exit={kod} [{ut.strip()[:50]}]", f"exit={INTERNT}")
    doma("klass8/klass", "internt fel" in ut, ut.strip()[:60], "klassen ordagrant")
    doma("klass8/fingerprint", len(fprader(ut)) == 1, ut.strip()[:60], "fingerprintrad finns")
    doma("klass8/ingen-traceback", "traceback" not in err.lower(), err[:60], "stderr utan stackspår")

    # --- TRÖSKEL 1: första felet öppnar, radordningen är kontraktets ---
    dt1 = str(kat / "d-troskel1")
    kod, ut, _ = kor("kor", dt1, "h-x", "9", "1", str(FW), str(kuv), "30",
                     "--", str(kat / "faller9.sh"))
    rader = ut.strip().splitlines()
    doma("troskel1/kod", kod == OPPEN, f"exit={kod}", f"exit={OPPEN} — tröskel 1 öppnar på första felet")
    doma("troskel1/failure-forst", len(rader) >= 3 and "provfel" in rader[0],
         ut.strip()[:70], "den klassade failuren skrivs FÖRST")
    doma("troskel1/fingerprint-mitten", len(rader) >= 3 and rader[-2].startswith("fingerprint: "),
         ut.strip()[:70], "fingerprintraden före öppningsraden")
    doma("troskel1/oppning-sist", len(rader) >= 1 and rader[-1].startswith("brytare öppen: "),
         rader[-1][:60] if rader else "tomt", "sist raden 'brytare öppen: <orsak>'")
    st = status(dt1)
    doma("troskel1/status", st.get("oppen") is True and isinstance(st.get("orsak"), str)
         and st.get("orsak") != "", str(st)[:80], "status bär oppen och en icke-tom orsak")
    kanarie = kat / "kanarie-t1"
    kod, ut, _ = kor("kor", dt1, "h-x", "9", "1", str(FW), str(kuv), "30",
                     "--", "/usr/bin/touch", str(kanarie))
    doma("troskel1/redan-oppen", kod == OPPEN and not kanarie.exists(),
         f"exit={kod} kanarie={kanarie.exists()}", "redan öppen startar inget kommando")

    # --- NORMALISERING PÅ BETEENDE: timeoutvärdet är en sifferföljd ---
    # "överskred 1 s" och "överskred 2 s" är samma fel; tröskel 2 ska öppna.
    dn = str(kat / "d-norm-siffra")
    k1, _, _ = kor("kor", dn, "h-x", "9", "2", str(FW), str(kuv), "1", "--", str(kat / "sover.sh"))
    k2, ut, _ = kor("kor", dn, "h-x", "9", "2", str(FW), str(kuv), "2", "--", str(kat / "sover.sh"))
    doma("norm-siffra/oppnar", k1 == TIMEOUT and k2 == OPPEN, f"koder {k1}/{k2}",
         f"{TIMEOUT} sedan {OPPEN} — olika timeoutvärden är samma fingerprint")

    # Citerad sökväg (gits och Pythons standardform) normaliseras också —
    # granskningsfynd delsteg 1: apostrofen före / hade annars gömt vägen för
    # ersättningen, och bokstavsvariansen hade gett två fingerprints.
    dc = str(kat / "d-norm-citat")
    k1, _, _ = kor("kor", dc, "h-x", "9", "2", str(FW), str(kuv), "30", "--", str(kat / "fel-cit-a.sh"))
    k2, ut, _ = kor("kor", dc, "h-x", "9", "2", str(FW), str(kuv), "30", "--", str(kat / "fel-cit-b.sh"))
    doma("norm-citat/oppnar", k1 == NONZERO and k2 == OPPEN, f"koder {k1}/{k2}",
         f"{NONZERO} sedan {OPPEN} — citerad väg med bokstavsvarians är samma fingerprint")

    # Ordskillnad i klass 6-orsaken: två fingerprints, tröskel 2 öppnar inte.
    do = str(kat / "d-norm-ord")
    k1, u1, _ = kor("kor", do, "h-x", "9", "2", str(FW), str(kuv), "30", "--", str(kat / "klagar-kvot.sh"))
    k2, u2, _ = kor("kor", do, "h-x", "9", "2", str(FW), str(kuv), "30", "--", str(kat / "klagar-db.sh"))
    doma("norm-ord/oppnar-inte", k1 == INGEN_KANDIDAT and k2 == INGEN_KANDIDAT,
         f"koder {k1}/{k2}", "ordskillnad är två fingerprints — ingen öppning vid tröskel 2")
    doma("norm-ord/skilda", fprader(u1) and fprader(u2) and fprader(u1)[0] != fprader(u2)[0],
         f"{fprader(u1)[:1]} / {fprader(u2)[:1]}", "fingerprintsträngarna skilda")

    # --- PROCESSENS EXITKOD, i den kanalform workern MÄTTS ha ---
    # Grinden K15 mäter ena hållet: olika processkod ger olika fingerprint.
    # Här ligger MOTPOLEN — en fix som splittrar samma fel vore lika fel som
    # den som smälte ihop olika — plus formen, signalkoderna och återfallet.

    # Samma processkod, HELT olika kastad stdout: fortfarande EN klass. Det är
    # ärligt och inte en brist i brytaren: h-009 kastar sessionens stdout, så
    # texterna är strukturellt oskiljbara nedströms. Tröskel 2 ska öppna.
    dpk = str(kat / "d-proc-kastad")
    k1, u1, _ = kor("kor", dpk, "h-x", "9", "2", str(FW), str(kuv), "30", "--", str(kat / "proc1-a.sh"))
    k2, u2, _ = kor("kor", dpk, "h-x", "9", "2", str(FW), str(kuv), "30", "--", str(kat / "proc1-b.sh"))
    doma("proc/kastad-stdout", k1 == NONZERO and k2 == OPPEN, f"koder {k1}/{k2}",
         f"{NONZERO} sedan {OPPEN} — samma processkod är EN klass även när den "
         "kastade stdouten skiljer sig")
    doma("proc/barer-koden", bool(fprader(u1)) and ":1:" in fprader(u1)[0],
         str(fprader(u1)[:1]), "fingerprinten bär processens exitkod 1")

    # Olika processkod, samma kanalform: två fingerprints, ingen öppning.
    dps = str(kat / "d-proc-skilda")
    k1, u1, _ = kor("kor", dps, "h-x", "9", "2", str(FW), str(kuv), "30", "--", str(kat / "proc1-a.sh"))
    k2, u2, _ = kor("kor", dps, "h-x", "9", "2", str(FW), str(kuv), "30", "--", str(kat / "proc64.sh"))
    doma("proc/skilda-oppnar-inte", k1 == NONZERO and k2 == NONZERO, f"koder {k1}/{k2}",
         f"{NONZERO} båda gångerna — kod 1 och kod 64 får aldrig öppna vid tröskel 2")
    doma("proc/skilda-fp", bool(fprader(u1)) and bool(fprader(u2))
         and fprader(u1)[0] != fprader(u2)[0] and ":64:" in fprader(u2)[0],
         f"{fprader(u1)[:1]} / {fprader(u2)[:1]}",
         "skilda fingerprints, den andra bär koden 64")

    # Signalkoder är NEGATIVA (h-009 bär subprocessens returncode rått).
    # Minustecknet överlever siffernormaliseringen — men bara koden skiljer
    # SIGTERM från SIGKILL, så utlyftet måste läsa tecknet med.
    dpg = str(kat / "d-proc-signal")
    k1, u1, _ = kor("kor", dpg, "h-x", "9", "2", str(FW), str(kuv), "30", "--", str(kat / "sig-term.sh"))
    k2, u2, _ = kor("kor", dpg, "h-x", "9", "2", str(FW), str(kuv), "30", "--", str(kat / "sig-kill.sh"))
    doma("proc/signal-oppnar-inte", k1 == NONZERO and k2 == NONZERO, f"koder {k1}/{k2}",
         f"{NONZERO} båda gångerna — SIGTERM och SIGKILL är två olika fel")
    doma("proc/signal-fp", bool(fprader(u1)) and bool(fprader(u2))
         and fprader(u1)[0] != fprader(u2)[0] and ":-15:" in fprader(u1)[0]
         and ":-9:" in fprader(u2)[0],
         f"{fprader(u1)[:1]} / {fprader(u2)[:1]}",
         "fingerprintarna bär -15 respektive -9")

    # Klasser UTAN processkod faller tillbaka på `-`: en okänd failuretext får
    # aldrig bli ett anropsfel, och en timeout får ingen påhittad kod.
    dpu = str(kat / "d-proc-utan")
    _, u1, _ = kor("kor", dpu, "h-x", "9", "9", str(FW), str(kuv), "1", "--", str(kat / "sover.sh"))
    doma("proc/utan-kod", bool(fprader(u1)) and fprader(u1)[0].startswith(f"fingerprint: {TIMEOUT}:-:"),
         str(fprader(u1)[:1]), "timeout bär ingen processkod — återfallet är `-`")

    # --- KVOT: mönstret möter hela failuretexten, även klass 6 ---
    dq = kat / "d-kvot6"
    dq.mkdir()
    (dq / "kvot.monster").write_text("kvoten tog slut\n", encoding="utf-8")
    kod, ut, _ = kor("kor", str(dq), "h-x", "1", "5", str(FW), str(kuv), "30",
                     "--", str(kat / "klagar-kvot.sh"))
    rader = ut.strip().splitlines()
    doma("kvot6/kod", kod == OPPEN, f"exit={kod} [{ut.strip()[:50]}]",
         f"exit={OPPEN} — kvotmönster matchar klass 6-failuretexten")
    doma("kvot6/klass", "kvot_slut" in ut, ut.strip()[:70], "klassen kvot_slut namnges")
    doma("kvot6/ingen-fingerprint", fprader(ut) == [], ut.strip()[:70],
         "kvot_slut fingerprintas aldrig")
    doma("kvot6/oppning-sist", bool(rader) and rader[-1].startswith("brytare öppen: "),
         rader[-1][:60] if rader else "tomt", "sist raden 'brytare öppen: <orsak>'")
    st = status(str(dq))
    doma("kvot6/oforbrukad", st.get("forbrukat") == 0 and st.get("fingerprints") == {},
         str(st)[:80], "kvot_slut förbrukar inte och fingerprintas inte — mätt i status")

    # Enbart tomma och blanka rader i mönsterfilen kvotklassar ingenting:
    # en blankrad som substrängsmönster hade matchat nästan varje failuretext.
    db = kat / "d-kvot-blank"
    db.mkdir()
    (db / "kvot.monster").write_text("\n\n   \n\t\n", encoding="utf-8")
    kod, ut, _ = kor("kor", str(db), "h-x", "9", "9", str(FW), str(kuv), "30",
                     "--", str(kat / "klagar-kvot.sh"))
    doma("kvot-blank/kod", kod == INGEN_KANDIDAT, f"exit={kod}",
         f"exit={INGEN_KANDIDAT} — blanka rader är inga mönster")
    doma("kvot-blank/ingen-kvot", "kvot_slut" not in ut, ut.strip()[:60],
         "kvot_slut nämns aldrig")

    # Andra mönstret i filen räcker — matchningen läser hela filen.
    d2m = kat / "d-kvot-tva"
    d2m.mkdir()
    (d2m / "kvot.monster").write_text("aldrig denna text\nkvoten tog slut\n", encoding="utf-8")
    kod, ut, _ = kor("kor", str(d2m), "h-x", "9", "9", str(FW), str(kuv), "30",
                     "--", str(kat / "klagar-kvot.sh"))
    doma("kvot-tva/kod", kod == OPPEN and "kvot_slut" in ut, f"exit={kod} [{ut.strip()[:50]}]",
         "andra mönstret i filen kvotklassar")

    # --- STATUS: färskt tillstånd, exakta nycklar, katalogen skapas inte ---
    ofodd = kat / "d-ofodd"
    st = status(str(ofodd))
    doma("status/farskt", st == {"oppen": False, "orsak": None, "forbrukat": 0, "fingerprints": {}},
         str(st)[:80], "färskt tillstånd med exakt de fyra nycklarna")
    doma("status/skapar-inte", not ofodd.exists(), "katalogen skapades",
         "status läser, aldrig skriver")

    dr = str(kat / "d-raknar")
    kor("kor", dr, "h-x", "9", "9", str(FW), str(kuv), "30", "--", str(kat / "faller9.sh"))
    kor("kor", dr, "h-x", "9", "9", str(FW), str(kuv), "30", "--", str(kat / "faller9.sh"))
    st = status(dr)
    doma("status/raknar", st.get("forbrukat") == 2 and list(st.get("fingerprints", {}).values()) == [2],
         str(st)[:80], "två lika fel: forbrukat 2, en fingerprint med räknaren 2")

    # --- TRASIG TILLSTÅNDSFIL: fel, aldrig ett färskt tillstånd ---
    dtr = kat / "d-trasig"
    dtr.mkdir()
    (dtr / "tillstand.json").write_text("inte json\n", encoding="utf-8")
    kanarie_tr = kat / "kanarie-trasig"
    kod, ut, err = kor("kor", str(dtr), "h-x", "9", "2", str(FW), str(kuv), "30",
                       "--", "/usr/bin/touch", str(kanarie_tr))
    doma("trasig/kor", kod == ANROP and ut.strip() != "", f"exit={kod} [{ut.strip()[:50]}]",
         f"exit={ANROP} med orsak — en trasig fil får inte läsas som färsk")
    doma("trasig/inget-kommando", not kanarie_tr.exists(), "kanarien skrevs",
         "trasig tillståndsfil startar aldrig kommandot — filen kan gömma en öppen brytare")
    doma("trasig/traceback", "traceback" not in (ut + err).lower(), "traceback", "aldrig traceback")
    kod, ut, _ = kor("status", str(dtr))
    doma("trasig/status", kod == ANROP and ut.strip() != "", f"exit={kod}",
         f"exit={ANROP} — status ljuger inte fram ett färskt tillstånd")
    (dtr / "tillstand.json").write_text('{"oppen": "ja"}\n', encoding="utf-8")
    kod, ut, _ = kor("status", str(dtr))
    doma("trasig/fel-form", kod == ANROP, f"exit={kod} [{ut.strip()[:50]}]",
         f"exit={ANROP} — JSON utan brytartillståndets form är också trasig")

    # --- TOPPVAKTEN: utforaren saknas → internt fel på stdout, aldrig stackspår ---
    kopia_rot = kat / "kopia"
    (kopia_rot / "controller/brytare").mkdir(parents=True)
    kopia = kopia_rot / "controller/brytare/cli"
    shutil.copy(CLI, kopia)
    os.chmod(kopia, 0o755)
    r = subprocess.run([str(kopia), "kor", str(kat / "d-topp"), "h-x", "9", "2",
                        str(FW), str(kuv), "30", "--", str(kat / "faller9.sh")],
                       capture_output=True, text=True, errors="replace", cwd=ROT, timeout=90)
    KODER.append(r.returncode)
    doma("toppvakt/kod", r.returncode == INTERNT, f"exit={r.returncode}", f"exit={INTERNT}")
    doma("toppvakt/klass", r.stdout.startswith("internt fel:"), r.stdout.strip()[:60],
         "klassen internt fel på stdout")
    doma("toppvakt/ingen-traceback", "traceback" not in r.stderr.lower(), r.stderr.strip()[:60],
         "stderr utan stackspår")

    # --- EXITKOD 2 ALDRIG — svept över samtliga uppmätta koder ---
    doma("ej-2/svep", 2 not in KODER, f"koder: {sorted(set(KODER))}",
         "2 är ODÖMBART (_lib.sh) och används aldrig")

    subprocess.run(["rm", "-rf", str(kat)])
    print(f"\n{ratt} rätt, {fel} fel")
    return 1 if fel else 0


if __name__ == "__main__":
    sys.exit(main())
