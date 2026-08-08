#!/usr/bin/env python3.12
"""tests/controller/policy/fall.py — kontraktsfall för controller/policy/cli.

    python3.12 tests/controller/policy/fall.py     exit 0 = alla fall håller

Det här är INTE exitgrinden. `verify/bin/h-007-exit` är grinden och ägs av
människan; den här filen täcker vad grinden inte når och får aldrig åberopas
som bevis för att skiva 7 är klar.

Grinden prövar fem av §A-mängdens sökvägar. De fem den INTE prövar står
först nedan — bland dem konstitutionen själv. En lögnstub som dömde på
sökvägsprefix tog `docs/07-konstitution.md` med exit 0 och fick ändå
14 PASS 0 FAIL (mätt 2026-08-08).

Grinden använder tre task-id men bara två accepterade former, och båda
reduceras till "något under controller/ plus något under docs/". Avsnittet
TASK-ID-SKOPNING nedan är därför det grinden bevisligen inte kan skilja:
läser komponenten tasksens egen allowed_write, eller släpper den in allt
under controller/?
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROT = Path(__file__).resolve().parents[3]
CLI = ROT / "controller/policy/cli"
ACCEPT, ANROP, SEKTION_A, UTANFOR, DOCS, FILBUDGET, RADBUDGET = 0, 1, 3, 4, 5, 6, 7

BESL = "docs/05-beslutslogg.md"
BORJA = "docs/00-borja-har.md"

# (namn, task-id, {sökväg: tillägg}, väntad kod, sökväg orsaken MÅSTE namnge)
# Sista fältet är den ÖVERTRÄDANDE sökvägen — inte varje ändrad fil. En
# kandidat kan innehålla lagliga filer bredvid den olagliga, och orsaken ska
# peka ut den som brast.
FALL: list[tuple] = [
    # --- §A-ytor som grindens K1 aldrig prövar ---
    ("konstitutionen", "h-001", {"docs/07-konstitution.md": "\n# p\n"}, SEKTION_A,
     "docs/07-konstitution.md"),  # GRUNDLAGEN — lögnstubben tog denna med exit 0
    ("regelverket", "h-001", {"docs/03-regelverk.md": "\n# p\n"}, SEKTION_A, "docs/03-regelverk.md"),
    ("claude-md", "h-001", {"CLAUDE.md": "\n# p\n"}, SEKTION_A, "CLAUDE.md"),
    ("eval-rubriken", "h-001",
     {"skills/nortropic-eval/references/eval-rubric.md": "\n# p\n"}, SEKTION_A,
     "skills/nortropic-eval/references/eval-rubric.md"),  # §A2, måttstocken
    ("juridikflaggorna", "h-001",
     {"skills/nortropic-plan/references/juridikflaggor.md": "\n# p\n"}, SEKTION_A,
     "skills/nortropic-plan/references/juridikflaggor.md"),  # §A4
    ("radering-av-sektion-a", "h-001", {"AUTOPILOT": None}, SEKTION_A,
     "AUTOPILOT"),  # en §A-fil som RADERAS är lika rörd som en som ändras

    # --- TASK-ID-SKOPNING: det grinden inte kan skilja ---
    ("ratt-task-ratt-yta", "h-006",
     {"controller/worker/p.txt": "p\n", BESL: "| p |\n"}, ACCEPT, None),  # h-006 i sin egen yta
    ("fel-task-annans-yta", "h-001",
     {"controller/worker/p.txt": "p\n", BESL: "| p |\n"}, UTANFOR,
     "controller/worker/p.txt"),  # grinden prövar aldrig att task-id spelar roll
    ("h001-i-policyytan", "h-001",
     {"controller/policy/p.txt": "p\n", BESL: "| p |\n"}, UTANFOR, "controller/policy/p.txt"),
    ("h007-i-egen-yta", "h-007",
     {"controller/policy/p.txt": "p\n", BESL: "| p |\n", BORJA: "p\n"}, ACCEPT, None),

    # --- docs-kravet är en mängd, inte ett ja/nej ---
    ("h007-halva-docs", "h-007", {"controller/policy/p.txt": "p\n", BESL: "| p |\n"}, DOCS,
     "docs/00-borja-har.md"),  # docs_impact har TVÅ sökvägar; en räcker inte
    ("h007-fel-docs", "h-007", {"controller/policy/p.txt": "p\n", BORJA: "p\n"}, DOCS,
     "docs/05-beslutslogg.md"),  # rätt antal docs-filer, fel mängd

    # --- ägarhandsytorna: avvisas, men som utanför allowed_write ---
    ("specs", "h-001", {"specs/prov.json": "{}\n"}, UTANFOR, "specs/prov.json"),  # ägarhand, inte §A-vaktens jobb
    ("verify", "h-001", {"verify/bin/prov": "p\n"}, UTANFOR, "verify/bin/prov"),  # ägarhand

    # --- anropsfel ---
    ("okant-task-id", "h-999", {"controller/state/p.txt": "p\n", BESL: "| p |\n"}, ANROP, None),
]


def git(*argv: str, kat: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(kat or ROT), *argv],
                          capture_output=True, text=True)


def main() -> int:
    if not os.access(CLI, os.X_OK):
        print(f"FAIL  {CLI} saknas eller är inte körbar")
        return 1

    base = git("rev-parse", "HEAD").stdout.strip()
    gren = f"h007-fall-{os.getpid()}"
    yttre = tempfile.mkdtemp(dir=os.environ.get("TMPDIR") or "/tmp")
    ws = Path(yttre) / "ws"
    git("branch", "-f", gren, base)
    if git("worktree", "add", str(ws), gren).returncode != 0:
        print("SKIP  kunde inte skapa provworktree — odömbart")
        return 2

    ratt = fel = 0

    def doma(namn: str, villkor: bool, sett: str, krav: str) -> None:
        nonlocal ratt, fel
        if villkor:
            ratt += 1
        else:
            fel += 1
            print(f"FAIL  {namn} — krav: {krav} · sett: {sett}")

    def kandidat(andringar: dict) -> str:
        git("reset", "--hard", base, kat=ws)
        git("clean", "-fdq", kat=ws)
        for sokvag, text in andringar.items():
            p = ws / sokvag
            if text is None:
                p.unlink(missing_ok=True)
                continue
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("a", encoding="utf-8") as f:
                f.write(text)
        git("add", "-A", kat=ws)
        git("commit", "-q", "-m", "fall", kat=ws)
        return git("rev-parse", "HEAD", kat=ws).stdout.strip()

    def kor(task: str, kand: str) -> tuple[int, str, str]:
        r = subprocess.run([str(CLI), "check", task, base, kand],
                           capture_output=True, text=True, cwd=ROT, timeout=60)
        return r.returncode, r.stdout.strip(), r.stderr.strip()

    try:
        for namn, task, andringar, vantad, namnger in FALL:
            kod, ut, err = kor(task, kandidat(andringar))
            doma(namn, kod == vantad, f"exit={kod} ut=[{ut[:60]}]", f"exit={vantad}")
            doma(f"{namn}/stderr", err == "", f"[{err[:60]}]", "tom stderr")
            doma(f"{namn}/traceback", "traceback" not in (ut + err).lower(),
                 "traceback i utdata", "aldrig traceback")
            if vantad != ACCEPT:
                doma(f"{namn}/orsak", ut != "", "tom stdout", "avslag måste namnge orsaken")
            if namnger:
                doma(f"{namn}/namnger", namnger in ut, f"[{ut[:60]}]",
                     f"orsaken ska namnge {namnger}")

        # Budgetarnas gränser. Taket är inklusivt: 8 filer och 600 rader går igenom.
        for namn, antal, vantad in (("filer-8", 7, ACCEPT), ("filer-9", 8, FILBUDGET)):
            a = {f"controller/state/f{n}.txt": "p\n" for n in range(antal)}
            a[BESL] = "| p |\n"
            kod, ut, _ = kor("h-001", kandidat(a))
            doma(namn, kod == vantad, f"exit={kod} ut=[{ut[:50]}]", f"exit={vantad}")

        for namn, rader, vantad in (("rader-600", 599, ACCEPT), ("rader-601", 600, RADBUDGET)):
            a = {"controller/state/stor.txt": "".join(f"r{n}\n" for n in range(rader)),
                 BESL: "| p |\n"}
            kod, ut, _ = kor("h-001", kandidat(a))
            doma(namn, kod == vantad, f"exit={kod} ut=[{ut[:50]}]", f"exit={vantad}")

        # Ett taggobjekt som candidate-sha får aldrig peelas till en annan
        # commit och prövas i smyg (h-006:s lärdom, LOOP-H-006 delsteg 2).
        tagg = git("rev-parse", "100d-baseline-20260730").stdout.strip()
        if tagg:
            kod, ut, err = kor("h-001", tagg)
            doma("tagg-som-kandidat", kod == ANROP, f"exit={kod} ut=[{ut[:50]}]", f"exit={ANROP}")
            doma("tagg-som-kandidat/stderr", err == "", f"[{err[:50]}]", "tom stderr")

        # Evidence: ett avslag utan sparat bevis är ett påstående.
        ev = ROT / "controller/policy/evidence"
        fore = len(list(ev.glob("*.json"))) if ev.is_dir() else 0
        kod, _, _ = kor("h-001", kandidat({"AUTOPILOT": "\non\n"}))
        nya = sorted(ev.glob("*.json"), key=lambda p: p.stat().st_mtime)
        doma("evidence/nytt", len(nya) > fore, f"{fore} → {len(nya)}", "en ny evidence-fil")
        if nya:
            # Ett oläsbart bevis ska bli ett FAIL, aldrig ett stackspår ur
            # provet självt — ett prov som kraschar rapporterar ingenting.
            try:
                d = json.loads(nya[-1].read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                d = {}
                doma("evidence/lasbart", False, f"{type(e).__name__}: {e}",
                     "evidence ska vara läsbar JSON")
            doma("evidence/verdikt", d.get("verdikt") == "sektion_a",
                 str(d.get("verdikt")), "verdikt sektion_a")
            doma("evidence/filer", "AUTOPILOT" in d.get("andrade_filer", []),
                 str(d.get("andrade_filer")), "AUTOPILOT i andrade_filer")
    finally:
        git("worktree", "remove", "--force", str(ws))
        subprocess.run(["rm", "-rf", yttre])
        git("branch", "-D", gren)
        git("worktree", "prune")

    print(f"\n{ratt} rätt, {fel} fel")
    return 1 if fel else 0


if __name__ == "__main__":
    sys.exit(main())
