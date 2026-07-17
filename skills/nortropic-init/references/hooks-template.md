# Project `.claude/settings.local.json` Template

Written into every new Nortropic client repo by `/nortropic-init`. Two jobs: auto-format on every edit (PowerShell — official Windows hook guidance, no jq dependency), and pre-allow the commands the pipeline needs so builds do not stall on permission prompts.

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm install)",
      "Bash(pnpm add:*)",
      "Bash(pnpm build)",
      "Bash(pnpm dev:*)",
      "Bash(pnpm lint:*)",
      "Bash(npx prettier:*)",
      "Bash(npx lighthouse:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git push:*)",
      "Bash(git status)",
      "Bash(git diff:*)",
      "Bash(gh repo view:*)",
      "Bash(vercel link:*)",
      "Bash(vercel env:*)",
      "Bash(vercel:*)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "shell": "powershell",
            "command": "try { $inp = [Console]::In.ReadToEnd() | ConvertFrom-Json; $f = $inp.tool_input.file_path; if ($f -and $f -match '\\.(ts|tsx|js|jsx|css|json)$' -and (Test-Path -LiteralPath $f)) { npx prettier --write --ignore-unknown -- \"$f\" 2>$null | Out-Null } } catch {}; exit 0"
          }
        ]
      }
    ]
  }
}
```

Notes:
- The hook never blocks: every path exits 0; formatting failures are silent (build-time lint still catches real problems)
- `-LiteralPath` and the `--` separator keep unusual file paths from being interpreted as options
- Markdown intentionally excluded from the Prettier matcher (prose files keep their formatting)
- If the client project ever runs on macOS/Linux (collaborator), replace the hook command with this node equivalent (uses `execFileSync` with an argument array — no shell, so file paths can never inject commands) and drop the `"shell"` field:

```js
node -e "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{try{const f=JSON.parse(d).tool_input.file_path;if(/\.(ts|tsx|js|jsx|css|json)$/.test(f))require('child_process').execFileSync('npx',['prettier','--write','--ignore-unknown','--',f],{stdio:'ignore'})}catch(e){}})"
```
