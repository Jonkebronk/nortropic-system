---
name: nortropic-plan
description: Step 1 of the Nortropic pipeline — turns a client research.md into a complete PROJECT-BRIEF.md via the project-planner agent. User-triggered only.
argument-hint: "[path-to-research.md]"
disable-model-invocation: true
context: fork
agent: project-planner
---

Create a complete Nortropic PROJECT-BRIEF.md from the client research file: **$ARGUMENTS**

1. Read the research file at the path above. If no path was given, look for `research.md` in the current directory; if none exists, stop and say exactly which file you need.
2. **Run your INPUT GATE first**: verify the research contains business name, phone number, at least one service, at least one ort/service area, and a usable USP. If anything is missing, STOP and return only the numbered list of missing items — do not plan on guesses.
3. Apply your full planning process (site-architecture, seo-plan, cro on demand) and write `PROJECT-BRIEF.md` in the same directory as the research file, with all 6 sections per your system prompt.
4. Return to the user: a 5-line executive summary of the brief (business, conversion goal, page count, keyword focus, design direction), the list of open questions that need the user's answers, and the reminder that the next step is `/nortropic-init <path-to-PROJECT-BRIEF.md>` once the brief is approved.

Do not create any repository or scaffold anything — this step produces the brief only.
