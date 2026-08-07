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
| `sandbox.filesystem.denyWrite` (26) | Nekar skalvägen mot §A på OS-nivå (Seatbelt) |
| `sandbox.network` | Tom allowlist utom `api.anthropic.com`, `strictAllowlist`, `allowManagedDomainsOnly` |
| `requiredMinimum/MaximumVersion` | Claude Code vägrar starta utanför 2.1.224 |
| `env.DISABLE_AUTOUPDATER` | Bakgrundsuppdatering av — pinnen håller |

### Känd begränsning

Tretton av `denyWrite`-posterna pekar på `~/nortropic/worktrees/**`, en katalog som ännu inte finns. Deras verkan är **OVERIFIERAD** tills skiva 5 skapar ett worktree. Klonhalvan är verifierad 2026-08-07 med `EPERM` från Seatbelt.

`Edit`-regler täcker alla filredigerande verktyg; `Write`-regler matchar inte och ska inte användas.
