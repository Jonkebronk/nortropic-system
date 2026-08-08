# config/

## managed-settings.json

Claude Codes managed settings för fabrikens byggmaskin. **Källkopia — installeras, läses aldrig härifrån i drift.**

Installationssökväg på macOS:

    /Library/Application Support/ClaudeCode/managed-settings.json

Ägd av `root:wheel`, läge `644`. Managed scope kan inte överridas av något i repot — det är kravet från B9 i granskningen 2026-07-31.

Installeras med:

    sudo cp config/managed-settings.json "/Library/Application Support/ClaudeCode/"
    sudo chown root:wheel "/Library/Application Support/ClaudeCode/managed-settings.json"
    sudo chmod 644 "/Library/Application Support/ClaudeCode/managed-settings.json"

Träder i kraft vid nästa sessionsstart.

### Vad den gör

| Nyckel | Verkan |
|---|---|
| `permissions.deny` (34) | Nekar verktygsvägen mot §A-mängden och läsning av nycklar |
| `sandbox.filesystem.denyWrite` (13) | Nekar skalvägen mot §A på OS-nivå (Seatbelt) |
| `sandbox.network` | Tom allowlist utom `api.anthropic.com`, `strictAllowlist`, `allowManagedDomainsOnly` |
| `requiredMinimum/MaximumVersion` | Claude Code vägrar starta utanför 2.1.224 |
| `env.DISABLE_AUTOUPDATER` | Bakgrundsuppdatering av — pinnen håller |

### Mätt begränsning i denyWrite — subpath, inte filskydd

En `denyWrite`-post nekar **hela sökvägsgrenen ovanför sitt mål**, inte bara målet.
Mätt 2026-08-07 med positiv kontroll: med provraden
`/Users/elinhaggstrom/nortropic/wt/a1/AUTOPILOT` installerad gick `mkdir ~/nortropic/wt2`
och `mkdir ~/nortropic/prov-igen` medan `mkdir ~/nortropic/wt` gav EPERM. Samma förälder,
samma användare, samma session. Gäller lika för glob och konkret sökväg.

Följd: `denyWrite` kan inte selektivt skydda filer i en katalog som också måste vara
skrivbar. Mekanismen fungerar där trädet redan finns (klonhalvan, verifierad 2026-08-07),
men inte där kontrollplanet självt måste skapa katalogen.

De tretton `~/nortropic/worktrees/**`-posterna är därför **borttagna** — de gjorde
worktree-roten oskapbar och skyddade ingenting. 26 → 13 denyWrite-poster.
§A-skyddet i workspacet vaktas i stället av skiva 7:s diffpolicy. Det är svagare:
diffpolicyn granskar resultatet, inte försöket.

`Edit`-regler täcker alla filredigerande verktyg; `Write`-regler matchar inte och ska inte användas.
