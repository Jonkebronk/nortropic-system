#!/usr/bin/env bash
# config/worker-prompt.sh — gör kuvertet till en arbetsorder och startar workern.
#
# Detta är KONFIGURATION, inte en komponent: den pekas ut av configens
# worker_cmd och har därför ingen spec-rad. Byt den fritt — kedjan antar aldrig
# vilken binär som körs (h-009:s kontrakt).
#
# Kuvertet kommer på STDIN och i $NORTROPIC_KUVERT (h-009 levererar båda).
# Arbetskatalogen ÄR workspacet: h-009 sätter cwd, och allt sessionen skriver
# hamnar i kandidaten.
#
# SESSIONEN RÖR ALDRIG GIT. Utföraren (h-012) stagar och committar, och
# kandidat-SHA:t föds i controllerledet — därför behöver sessionen aldrig
# commiträtt, vilket är tur eftersom `git commit` faller under sandboxen.
# En session som committar SJÄLV ger ingen kandidat alls (utförarens kod 6).
set -u

KUV="$(cat)"
[ -n "$KUV" ] || { echo "worker-prompt: tomt kuvert på stdin"; exit 1; }

ORDER="$(KUV="$KUV" python3 - <<'PY'
import json
import os

k = json.loads(os.environ["KUV"])
kr = k.get("candidate_requirements", {})
om = kr.get("omfang", {})


def lista(rader):
    return "\n".join("  - " + str(r) for r in rader) if rader else "  (inga)"


d = [
    "Du arbetar som worker i ett kontrollplan. Uppgiften kommer ur en backlog,",
    "och dess utfall döms maskinellt efteråt. Svenska.",
    "",
    "# Uppgift: " + k.get("title", k["task_id"]),
    "",
    k.get("description", ""),
    "",
    "# Så här vet vi att den är gjord",
    "",
    lista(kr.get("utfall", [])),
    "",
    "# Skrivregler — hårda",
    "",
    "Du får ENDAST ändra filer som matchar:",
    lista(k.get("allowed_write", [])),
    "",
    "Du får ALDRIG röra:",
    lista(k.get("denied_write", [])),
    "",
    "Högst %s ändrade filer och %s tillagda rader."
    % (om.get("max_andrade_filer", "?"), om.get("max_tillagda_rader", "?")),
    "",
    "Dessa filer MÅSTE uppdateras i samma arbete:",
    lista(om.get("docs_uppdatering_i_samma_commit", [])),
    "",
    "En ändring utanför skrivytan gör hela arbetet avvisat — inte delvis, helt.",
    "",
    "# Hur du lämnar ifrån dig arbetet",
    "",
    "REDIGERA FILER. Kör ALDRIG `git add`, `git commit` eller någon annan",
    "git-skrivning: controllern stagar och committar åt dig, och en session som",
    "committar själv ger ingen kandidat alls.",
    "",
    "Du behöver inte skriva någon rapport — resultatet läses ur filerna.",
    "",
    "Kan du INTE lösa uppgiften: ändra ingenting och skriv ett kort stycke om",
    "varför. Den texten blir orsaken i utfallet, så var konkret.",
    "",
    "Basen du utgår från är %s och arbetskatalogen är redan rätt — arbeta med"
    % k.get("base_sha", "?")[:12],
    "relativa sökvägar.",
]
print("\n".join(d))
PY
)" || { echo "worker-prompt: kunde inte tolka kuvertet"; exit 1; }

exec claude -p "$ORDER" --output-format text --permission-mode acceptEdits
