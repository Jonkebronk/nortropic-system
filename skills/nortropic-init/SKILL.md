---
name: nortropic-init
description: Step 2 of the Nortropic pipeline — creates the GitHub repo and scaffolds the full site from an approved PROJECT-BRIEF.md via the stack-builder agent. User-triggered only (creates real GitHub/Vercel resources).
argument-hint: "[path-to-PROJECT-BRIEF.md]"
disable-model-invocation: true
context: fork
agent: stack-builder
---

Initialize a new Nortropic client site from the approved brief: **$ARGUMENTS**

1. Read the PROJECT-BRIEF.md at the path above (if no path given, look for `PROJECT-BRIEF.md` in the current directory; if none exists, stop and say so — this step requires an approved brief from `/nortropic-plan`).
2. Execute your full build process from the brief:
   - **Repo-GRIND (verifiera, skapa ALDRIG):** du ska redan stå i en klon av ett PRIVAT `kund-<slug>`-repo (Verkstadsgolvet-onboardingen skapade det med research.md). Verifiera: cwd är git-repo med remote, namnet matchar `kund-<slug>`, `gh repo view --json visibility` = `PRIVATE`, `research.md` finns. Avvikelse → **STOPP** med exakt fel + att man kör Verkstadsgolvet-onboardingen först (init skapar aldrig kund-repot, aldrig `-se`-suffix; se retro Y1)
   - Scaffold Next.js 15 + TS strict + Tailwind 4 + shadcn/ui per `nortropic-stack`
   - All content files (`business.ts` with the brief's exact NAP, `profile.ts` from the brief's §7 Kalibreringsprofil, services, areas, testimonials, faq)
   - Every page in the brief's architecture with the conversion trio (PhoneLink, CtaBanner, floating call button)
   - Lead pipeline: `app/actions/lead.ts` with Zod + honeypot + Resend. If `RESEND_API_KEY` is not available, wire everything and mark the env var as pending in your report — do not invent keys
   - Schema markup, sitemap, robots, Swedish 404/error pages, analytics per brief
   - Copy `references/hooks-template.md` (in this skill's directory) into the project as `.claude/settings.local.json`
   - `vercel link`, granular commits, push to `main`
3. Verify `pnpm build` passes with zero errors before reporting.
4. Report: repo URL, Vercel link status, env vars set/pending, `TODO-COPY` inventory, and `TODO-FACT` presented as an explicit **"Blocking — needs client answer before `/nortropic-launch`"** list (separate from the TODO-COPY inventory), and the reminder that the next steps are content (`content-designer` fills TODO-COPY) and `/nortropic-review`.
