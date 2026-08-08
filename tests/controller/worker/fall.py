#!/usr/bin/env python3.12
"""tests/controller/worker/fall.py — kontraktsfall för controller/worker/cli.

    python3.12 tests/controller/worker/fall.py      exit 0 = alla fall håller

Det här är INTE exitgrinden. `verify/bin/h-006-exit` är grinden och ägs av
människan; den här filen täcker det grinden inte når, och den får aldrig
åberopas som bevis för att skiva 6 är klar.

Varje fall bär vad kontraktet kräver och vad som faktiskt hände. Tre fall
kommer ur defekter som mättes fram 2026-08-08 och som provets nio kontroller
inte kunde se — de är märkta REGRESSION och ska aldrig tas bort:

  tagg-objekt      exit 0 med ETT ANNAT SHA än kuvertets (tyst substitution)
  sha-radbrytning  "$" matchade före avslutande \\n, fel failure-klass
  brutet-ror       "Exception ignored in ... BrokenPipeError" på stderr

Fallet `tva-sha-i-filen` är det provet bevisligen inte kan skilja: dess
kuvertmall innehåller bara ett SHA, så "läser fältet candidate_sha" och
"tar sista 40-hex-strängen i filen" ger där samma svar.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROT = Path(__file__).resolve().parents[3]
CLI = ROT / "controller/worker/cli"

# 2 är ODÖMBART i exit-testerna (_lib.sh rad 2) och är därför inte en
# failure-klass här. Filens EGET exit 2 nedan är just den betydelsen: odömbar
# körning, inte underkänd komponent.
GILTIG, ANROP, OPARSBAR, SHA_SAKNAS, INTERNT, TOM = 0, 1, 3, 4, 5, 6


def git(*argv: str) -> str:
    return subprocess.run(["git", "-C", str(ROT), *argv],
                          capture_output=True, text=True).stdout.strip()


SHA = git("rev-parse", "HEAD")
SHA2 = git("rev-parse", "HEAD~1")
TREE = git("rev-parse", "HEAD^{tree}")
TAGG = git("rev-parse", "100d-baseline-20260730")
FALSK = "b" * 40


def kuvert(sha: str, **extra) -> str:
    return json.dumps({"status": "candidate", "candidate_sha": sha,
                       "files": ["controller/state/cli"], **extra})


# (namn, innehåll, väntad kod, väntad stdout eller None, kommentar)
FALL: list[tuple] = [
    # --- positiva: kandidaten ska komma tillbaka OFÖRÄNDRAD ---
    ("commit-head", kuvert(SHA), GILTIG, SHA, "kuvertets eget SHA returneras"),
    ("commit-head1", kuvert(SHA2), GILTIG, SHA2, "andra SHA — fäller hårdkodning"),
    ("versaler", kuvert(SHA.upper()), GILTIG, SHA, "normaliseras till gemener"),
    ("extra-nyckel", kuvert(SHA, tests_run=3), GILTIG, SHA, "okända fält är tillåtna"),
    ("crlf", kuvert(SHA) + "\r\n", GILTIG, SHA, "radslut är blanktecken i JSON"),
    ("omgivande-blank", "  \n" + kuvert(SHA) + "\n  ", GILTIG, SHA, "blanktecken runt objektet"),
    ("tva-sha-i-filen", kuvert(SHA, note=SHA2), GILTIG, SHA,
     "PROVLUCKA: fältet gäller, inte sista hex-strängen i filen"),

    # --- SHA finns inte, eller är inte en commit ---
    ("tagg-objekt", kuvert(TAGG), SHA_SAKNAS, None,
     "REGRESSION: ^{commit} peelade taggen till en ANNAN commit"),
    ("tree", kuvert(TREE), SHA_SAKNAS, None, "ett tree är ingen commit"),
    ("slumpat-sha", kuvert(FALSK), SHA_SAKNAS, None, "välformat men finns inte"),

    # --- oparsbart ---
    ("prosa", "Jag har nu byggt komponenten och allt fungerar bra!\n", OPARSBAR, None, ""),
    ("prosa-med-sha", f"Klart! Jag committade {SHA} och allt är grönt.\n", OPARSBAR, None,
     "hex-sträng i prosa är inte ett kuvert"),
    ("markdown-stakat", "```json\n" + kuvert(SHA) + "\n```\n", OPARSBAR, None, ""),
    ("prosa-fore", "Klart!\n" + kuvert(SHA), OPARSBAR, None, "ingen utplockning ur prosa"),
    ("prosa-efter", kuvert(SHA) + "\nAllt grönt.\n", OPARSBAR, None, ""),
    ("tva-objekt", kuvert(SHA) + kuvert(SHA2), OPARSBAR, None, "vilket skulle gälla?"),
    ("candidate-sha-rad", f"CANDIDATE_SHA: {SHA}\nCHANGED_FILES: x\n", OPARSBAR, None,
     "v4.1 §11.1-formatet är inte JSON"),
    ("nan", kuvert(SHA)[:-1] + ',"n":NaN}', OPARSBAR, None, "RFC 8259 har ingen NaN"),
    ("infinity", kuvert(SHA)[:-1] + ',"n":Infinity}', OPARSBAR, None, ""),
    ("dubblerad-nyckel",
     '{"status":"candidate","candidate_sha":"%s","candidate_sha":"%s","files":["x"]}' % (FALSK, SHA),
     OPARSBAR, None, "sista värdet vinner tyst i Pythons json"),
    ("bom", "﻿" + kuvert(SHA), OPARSBAR, None, ""),
    ("json-array", "[" + kuvert(SHA) + "]", OPARSBAR, None, ""),
    ("json-strang", '"bara en sträng"', OPARSBAR, None, ""),
    ("saknat-falt", '{"status":"candidate","files":["x"]}', OPARSBAR, None,
     "AVSIKTLIGT: JSON men inget kuvert — schemabrott är oparsbart, inte sha-saknat"),
    ("fel-status", kuvert(SHA).replace('"candidate"', '"failure"', 1), OPARSBAR, None, ""),
    ("forkortat-sha", kuvert(SHA[:12]), OPARSBAR, None, "förkortning är tvetydig"),
    ("sha-radbrytning", json.dumps({"status": "candidate", "candidate_sha": SHA + "\n",
                                    "files": ["x"]}), OPARSBAR, None,
     "REGRESSION: $ matchade före avslutande radbrytning"),
    ("files-tom-lista", kuvert(SHA).replace('["controller/state/cli"]', "[]"), OPARSBAR, None, ""),
    ("files-tom-strang", kuvert(SHA).replace('"controller/state/cli"', '""'), OPARSBAR, None, ""),
    ("trunkerad", kuvert(SHA)[:-8], OPARSBAR, None, "det realistiska workerfelet"),

    # --- tomt ---
    ("noll-byte", "", TOM, None, ""),
    ("blanktecken", "   \n\t\n", TOM, None, ""),
]


def kor(argv: list[str]) -> tuple[int, str, str]:
    r = subprocess.run([str(CLI), *argv], capture_output=True, text=True, cwd=ROT, timeout=30)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def main() -> int:
    if not os.access(CLI, os.X_OK):
        print(f"FAIL  {CLI} saknas eller är inte körbar")
        return 1
    if not TAGG:
        print("SKIP  taggen 100d-baseline-20260730 saknas — tagg-regressionen är odömbar")
        return 2

    kat = tempfile.mkdtemp(dir=os.environ.get("TMPDIR") or "/tmp")
    ratt = fel = 0

    def doma(namn: str, villkor: bool, sett: str, krav: str) -> None:
        nonlocal ratt, fel
        if villkor:
            ratt += 1
        else:
            fel += 1
            print(f"FAIL  {namn} — krav: {krav} · sett: {sett}")

    for namn, innehall, vantad_kod, vantad_ut, _ in FALL:
        p = Path(kat) / namn
        p.write_text(innehall, encoding="utf-8")
        kod, ut, err = kor(["parse", str(p)])
        doma(namn, kod == vantad_kod, f"exit={kod} ut=[{ut[:70]}]", f"exit={vantad_kod}")
        doma(f"{namn}/ej-2", kod != 2, "exit=2", "2 är ODÖMBART i exit-testerna, aldrig en dom")
        if vantad_ut is not None:
            doma(f"{namn}/stdout", ut == vantad_ut, f"[{ut[:70]}]", f"exakt [{vantad_ut}]")
        doma(f"{namn}/stderr", err == "", f"[{err[:70]}]", "tom stderr")
        doma(f"{namn}/traceback", "traceback" not in (ut + err).lower(), "traceback i utdata",
             "aldrig traceback")

    # Icke-UTF8 måste hanteras som byte, inte som text.
    p = Path(kat) / "icke-utf8"
    p.write_bytes(b'{"status":"candidate","candidate_sha":"' + SHA.encode() + b'","files":["\xff"]}')
    kod, ut, err = kor(["parse", str(p)])
    doma("icke-utf8", kod == OPARSBAR, f"exit={kod}", f"exit={OPARSBAR}")
    doma("icke-utf8/stderr", err == "", f"[{err[:70]}]", "tom stderr")

    # Kraschytan: inget av detta får ge stackspår eller kod utanför 0-5.
    for namn, argv, vantad in (("fil-saknas", ["parse", f"{kat}/finns-inte"], INTERNT),
                               ("katalog", ["parse", kat], INTERNT),
                               ("inga-argument", [], ANROP),
                               ("bara-parse", ["parse"], ANROP),
                               ("tva-filer", ["parse", "a", "b"], ANROP),
                               ("okant-kommando", ["blaha"], ANROP)):
        kod, ut, err = kor(argv)
        doma(namn, kod == vantad, f"exit={kod} ut=[{ut[:60]}]", f"exit={vantad}")
        doma(f"{namn}/stderr", err == "", f"[{err[:70]}]", "tom stderr")

    # Brutet rör: tolkens egen spolning skrev tidigare på stderr.
    p = Path(kat) / "for-ror"
    p.write_text("prosa\n", encoding="utf-8")
    with subprocess.Popen([str(CLI), "parse", str(p)], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, cwd=ROT) as pr:
        pr.stdout.close()
        _, e = pr.communicate(timeout=30)
    doma("brutet-ror/stderr", e.strip() == b"", f"[{e[:70]!r}]",
         "REGRESSION: tom stderr mot brutet rör")

    print(f"\n{ratt} rätt, {fel} fel")
    return 1 if fel else 0


if __name__ == "__main__":
    sys.exit(main())
