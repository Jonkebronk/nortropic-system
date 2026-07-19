export const meta = {
  name: 'nortropic-final-touches',
  description: 'Genererar FINAL-TOUCHES.md (v16) — operatörens avslutande punch-list för en (ofta obemannat) byggd Nortropic-sajt: Fakta att fylla (TODO-FACT), Beslut att fatta (öppna FAKTA/BESLUT-frågor), Att signera (juridik/Gate 6), Avslutsreceptet. Dubblerar ALDRIG HANDOVER.md; pekar på gbp-/gsc-checklistorna i stället för att återskapa dem.',
  whenToUse: 'Kallas av /nortropic-autobygg som sista steg (obemannat), ELLER körs manuellt av en bemannad ägare efter /nortropic-launch för samma avslutslista. Tar en klientmapp (repo-roten) via args.clientDir.',
  phases: [
    { title: 'Enumerate', detail: 'TODO-FACT-grep + öppna FAKTA/BESLUT-frågor + Gate 6-fynd' },
    { title: 'Write',     detail: 'FINAL-TOUCHES.md i klientmappen — fyra sektioner + avslutsreceptet' },
  ],
}

const clientDir = (args && args.clientDir) || 'the Nortropic site in the current working directory'

const TODOFACTS = {
  type: 'object', required: ['hits'],
  properties: { hits: { type: 'array', items: { type: 'object', required: ['location'],
    properties: { location: { type: 'string', description: 'file:line' }, field: { type: 'string' } } } } },
}
const DECISIONS = {
  type: 'object', required: ['openQuestions'],
  properties: { openQuestions: { type: 'array', items: { type: 'object', required: ['text', 'kind'],
    properties: { text: { type: 'string' }, kind: { type: 'string', enum: ['FAKTA', 'BESLUT'] } } } } },
}
const GATE6 = {
  type: 'object', required: ['findings'],
  properties: { findings: { type: 'array', items: { type: 'object',
    properties: { title: { type: 'string' }, location: { type: 'string' }, why: { type: 'string' } } } } },
}

// Sektion 4 — verbatim, stabilt avslutsrecept (const gör det ordagrant och diffbart; ordagrant ur leverabel 3).
const RECIPE = [
  '- [ ] **1. Fyll fakta** — fyll varje TODO-FACT i sektion 1 med verkliga uppgifter i content-filerna (aldrig gissa).',
  '- [ ] **2. Mini-content-pass** — kör ENDAST om pris-/copy-påverkande beslut (sektion 2) har ändrats.',
  '- [ ] **3. Granskning** — FULL `/nortropic-review` om nya commits skett efter senaste FULL (freshness-regeln), annars direkt vidare.',
  '- [ ] **4. Launch** — kör `/nortropic-launch <preview-url>`, åtgärda kvarvarande grind-fynd.',
  '- [ ] **5. Deploy + efterarbete** — signera juridiken (nod 8), kör `/vercel:deploy` (nod 9), kör sedan `gbp-checklist-klient.md` + `gsc-steg-klient.md` de första två veckorna (nod 10).',
]

phase('Enumerate')
const facts = await agent(
  `Mechanical TODO-FACT enumeration in ${clientDir}. cd there, run: grep -rn "TODO-FACT" src/content src/app. Return every hit as location "file:line" + the field/line text. Judge nothing, fix nothing.`,
  { label: 'enum:todo-fact', phase: 'Enumerate', schema: TODOFACTS }
)

let decisions
if (args && args.openQuestions) {
  // Från autobygg: redan klassade — behåll bara FAKTA/BESLUT (STRATEGISK stoppade redan flödet).
  decisions = (args.openQuestions || []).filter(q => q && (q.kind === 'FAKTA' || q.kind === 'BESLUT'))
} else {
  // Manuell körning efter /nortropic-launch: självinsamla ur briefen.
  const d = await agent(
    `Read PROJECT-BRIEF.md's open-questions list for the site at ${clientDir} (check the client folder and the sibling research/brief folder). Return ONLY the FAKTA- and BESLUT-tagged questions (skip STRATEGISK — those should already be resolved).`,
    { label: 'enum:decisions', phase: 'Enumerate', schema: DECISIONS }
  )
  decisions = (d && d.openQuestions) || []
}

let legal = (args && args.legalFindings) || null
if (!legal) {
  // Manuell körning: samla Gate 6 read-only (självständig).
  const g = await agent(
    `Run ONLY Gate 6 (Swedish/EU legal) of your prelaunch process against the Nortropic site at ${clientDir}, reading content/profile.ts juridikflaggor. OBSERVE AND REPORT ONLY — never fix, never sign off. Return findings.`,
    { label: 'enum:legal', phase: 'Enumerate', agentType: 'qa-launcher', schema: GATE6 }
  )
  legal = (g && g.findings) || []
}

phase('Write')
await agent(
  `Skriv FINAL-TOUCHES.md i ${clientDir}. cd there; kör \`git rev-parse HEAD\` + \`date +%F\` för stämpel högst upp. ` +
  `Detta är operatörens avslutslista — INTE HANDOVER.md (den varma kundöverlämningen); säg det uttryckligen i en inledande rad och dubblera aldrig HANDOVER:s innehåll. ` +
  `Skriv exakt dessa fyra sektioner i markdown:\n` +
  `## 1. Fakta att fylla\nEn checkbox-rad per TODO-FACT med \`file:rad\` och en tom "Svar:"-rad under. Rådata: ${JSON.stringify(facts.hits || [])}\n\n` +
  `## 2. Beslut att fatta\nEn checkbox-rad per fråga med taggen (FAKTA/BESLUT). Rådata: ${JSON.stringify(decisions)}\n\n` +
  `## 3. Att signera\nJuridik/Gate 6-fynd för mänskligt sign-off (nod 8; juridik auto-fixas aldrig) + ev. villkors-/juridikutkast som ligger i repot. En checkbox-rad per fynd. Rådata: ${JSON.stringify(legal)}\n\n` +
  `## 4. Avslutsreceptet\nOrdagrant, kryssa av uppifrån:\n${RECIPE.join('\n')}\n\n` +
  `Peka på gbp-checklist-klient.md/gsc-steg-klient.md där de nämns — återskapa dem ALDRIG. Skriv inget utöver detta.`,
  { label: 'write', phase: 'Write' }
)

return {
  finalTouchesPath: `${clientDir}/FINAL-TOUCHES.md`,
  factsCount: (facts.hits || []).length,
  decisionsCount: decisions.length,
  legalCount: (legal || []).length,
}
