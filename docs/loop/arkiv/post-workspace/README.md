> **ARKIVERAT 2026-08-07. Kravinput till skiva 6–7. Installeras ej.**
> Källa: remediation-15, verifierad mot uppackad katalog. Fullt paket: ~/Arkiv/post-workspace-2026-08-07.tar.gz

# Nortropic — Post-Workspace Preparation Package

**Purpose:** Let Claude Code prepare the architecture, contracts, schemas, tests, and runbooks for the phases after workspace activation, without touching the live workspace or global trust chain.

**Status:** `PREPARED_NOT_BOUND_NOT_INSTALLED`

## Core rule

Claude Code may prepare future components in an isolated development area, but must not:

- modify the active Nortropic workspace,
- modify `/usr/local/libexec/nortropic`,
- modify `toolchain-lock.json`,
- modify `system-manifest.json`,
- modify `check-system-state`,
- create or consume authorization,
- create or modify claims or seals,
- stage, commit, push, open a PR, merge, or deploy,
- claim that the workspace is terminally complete.

All workspace-specific identities remain unbound placeholders until the live workspace track reaches terminal PASS.

## Recommended execution order

1. Read `CLAUDE_CODE_HANDOFF.md`
2. Run `prompts/PW0_REPOSITORY_DISCOVERY.md`
3. Run `prompts/PW1_POST_WORKSPACE_ARCHITECTURE.md`
4. Run `prompts/PW2_CONTRACTS_AND_SCHEMAS.md`
5. Run `prompts/PW3_NEGATIVE_TESTS_AND_FIXTURES.md`
6. Run `prompts/PW4_RUNBOOKS_AND_REVIEW_PACKAGE.md`
7. Run `prompts/PW5_PRE_BINDING_REVIEW.md`

## Final state

All output must end in:

```text
PREPARED_NOT_BOUND_NOT_INSTALLED
```
