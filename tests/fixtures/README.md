# tests/fixtures — verify-suitens frysta baselines

Dessa filer är konstitution §A6 (`docs/07-konstitution.md`): de uppdateras ENDAST av en människa, aldrig av trappmoderna eller någon annan autonom process. Ett regressionsnät som kan redigeras av det som ska fångas är inget nät.

Nya baseline-kandidater tas fram med `/nortropic-verify-suite --cut-baseline` (skriver `VERIFY-BASELINE-KANDIDAT-*.md` till `~/Workflow`); att granska kandidaten och committa den hit är en mänsklig handling. Efter en eval-rubrikversionsbump: klipp om `eval-baseline.md` en gång (en eval-körning), annars dömer suiten OGILTIG.
