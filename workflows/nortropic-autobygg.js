export const meta = {
  name: 'nortropic-autobygg',
  description: 'Obemannat kund-flöde (v16): orkestrerar plan→init→innehåll→granskning→grind-torrkörning för en research.md märkt "Läge: obemannat", med tre villkorade stopp (bemannat / ohanterad-scope-nej-juridik-eller-STRATEGISK / CRITICAL-efter-en-fixloop) som lämnar över till människa. Deployar ALDRIG — nod 8 (juridik-signoff) och nod 9 (/vercel:deploy) förblir mänskliga.',
  whenToUse: 'Kör manuellt när en research.md bär raden "Läge: obemannat" och ägaren vill att systemet bygger sajten utan mänskligt nod-3-stopp — fram till FINAL-TOUCHES + grind-torrkörning. Faller ALLTID tillbaka till mänskligt stopp vid ohanterad/scope-nej juridikflagga, kvarstående STRATEGISK öppen fråga, eller CRITICAL efter EN fixloop. Bemannat (default, ingen Läge-rad) => kör /nortropic-plan manuellt i stället.',
  phases: [
    { title: 'Plan',                    detail: 'project-planner → PROJECT-BRIEF.md + maskinläsbart plan-utfall (schema)' },
    { title: 'Villkorat stopp (plan)',  detail: 'bemannat, ohanterad/scope-nej juridik eller STRATEGISK fråga => överlämna (inget byggt)' },
    { title: 'Init',                    detail: 'stack-builder skapar privat repo + Vercel-preview' },
    { title: 'Del-C static-first',      detail: 'Ring-1 stateless bekräftas; stateful/Ring 2-3-behov => överlämna (docs/06)' },
    { title: 'Content',                 detail: 'content-designer fyller TODO-COPY + Humanisera; TODO-FACT lämnas' },
    { title: 'Review',                  detail: 'full review → EN fixloop → diff-review → CRITICAL-parse' },
    { title: 'Villkorat stopp (review)',detail: 'CRITICAL kvar efter EN fixloop => överlämna med FINAL-TOUCHES' },
    { title: 'Grind-torrkörning',       detail: '7 linser read-only, INGEN deploy, INGEN fix-loop, INGEN handover' },
    { title: 'Avslut',                  detail: 'FINAL-TOUCHES + AUTOBYGG-LOG + slutstatusrad' },
  ],
}

/* ─────────── LOAD-BEARING PURE FUNCTIONS (isolerat testbara, inga globals, före allt await) ─────────── */

function obemannatGate(lage) {
  if (lage !== 'obemannat')
    return { stop: true, reason: `Läge=${lage || 'bemannat'} — obemannat ej begärt; briefen är klar, stoppar vid nod 3 (briefgodkännande) enligt dagens bemannade flöde` }
  return { stop: false }
}

function shouldStopAfterPlan(plan) {
  if (!plan) return { stop: true, reason: 'plan-steget returnerade inget utfall' }
  if (plan.inputGatePassed === false)
    return { stop: true, reason: `INPUT GATE: research saknar ${(plan.missingFields || []).join(', ') || 'obligatoriska fält'}` }
  const ohanterad = (plan.juridikflaggor || []).filter(f => f && f.status === 'ohanterad')
  if (ohanterad.length)   // hälsa/kropp/medicin m.fl. har registerstatus 'ohanterad' → fångas här
    return { stop: true, reason: `ohanterad juridikflagga (${ohanterad.map(f => f.flagga).join(', ')}) — beslut vid nod 3: bygg modulen som eget arbete eller tacka nej` }
  const scopeNej = (plan.juridikflaggor || []).filter(f => f && f.status === 'scope-nej')
  if (plan.scopeNej || scopeNej.length)
    return { stop: true, reason: `scope-nej-flagga (${scopeNej.map(f => f.flagga).join(', ') || 'scope-nej'}) — briefen rekommenderar hänvisning (docs/06 Ring 3)` }
  const strat = (plan.openQuestions || []).filter(q => q && q.kind === 'STRATEGISK')
  if (strat.length)
    return { stop: true, reason: `STRATEGISK öppen fråga kvarstår: ${strat.map(q => q.text).join(' | ')}` }
  return { stop: false }   // enbart FAKTA/BESLUT-frågor kvar → fortsätt (de skjuts till FINAL-TOUCHES)
}

function shouldStopAfterReview(criticalCount) {
  if ((criticalCount || 0) > 0)
    return { stop: true, reason: `${criticalCount} CRITICAL kvarstår efter EN autonom fixloop — obemannat stannar och lämnar över till människa` }
  return { stop: false }
}

function scopeStr(dir) {
  return `the Nortropic site in the git repository at ${dir} — treat ${dir} as the project root: cd into it before every git/file command, review only files under it, and write any report file there`
}

/* ─────────── SCHEMAS ─────────── */

const PLAN_OUTCOME = {
  type: 'object',
  required: ['briefPath', 'lage', 'inputGatePassed', 'juridikflaggor', 'scopeNej', 'openQuestions'],
  properties: {
    briefPath:        { type: 'string' },
    repoNameSuggested:{ type: 'string' },
    lage:             { type: 'string', enum: ['obemannat', 'bemannat'] },
    klienttyp:        { type: 'string', enum: ['SKARP', 'TESTKLIENT'] },
    inputGatePassed:  { type: 'boolean' },
    missingFields:    { type: 'array', items: { type: 'string' } },
    juridikflaggor:   { type: 'array', items: { type: 'object', required: ['flagga', 'status'],
                          properties: { flagga: { type: 'string' },
                            status: { type: 'string', enum: ['hanterad', 'ohanterad', 'scope-nej'] } } } },
    scopeNej:         { type: 'boolean' },
    openQuestions:    { type: 'array', items: { type: 'object', required: ['text', 'kind'],
                          properties: { text: { type: 'string' },
                            kind: { type: 'string', enum: ['STRATEGISK', 'FAKTA', 'BESLUT'] } } } },
  },
}

const INIT_OUTCOME = {
  type: 'object', required: ['repoDir', 'buildPassed'],
  properties: {
    repoDir: { type: 'string', description: 'ABSOLUTE path to the cloned build repo' },
    repoUrl: { type: 'string' }, previewUrl: { type: 'string' },
    buildPassed: { type: 'boolean' },
    envPending: { type: 'array', items: { type: 'string' } },
    todoFacts:  { type: 'array', items: { type: 'string', description: 'file:line' } },
  },
}

const STATICGUARD = {
  type: 'object', required: ['stateful', 'evidence'],
  properties: { stateful: { type: 'boolean' },
    evidence: { type: 'array', items: { type: 'string' } }, note: { type: 'string' } },
}

const REVIEW_TRIAGE = {
  type: 'object', required: ['criticalCount', 'criticals'],
  properties: {
    criticalCount: { type: 'number' },
    criticals: { type: 'array', items: { type: 'object', required: ['title', 'location', 'fixAgent'],
      properties: { title: { type: 'string' }, location: { type: 'string' },
        fixAgent: { type: 'string', enum: ['stack-builder', 'seo-optimizer', 'content-designer'] } } } },
    highs: { type: 'array', items: { type: 'object', required: ['title', 'location', 'fixAgent'],
      properties: { title: { type: 'string' }, location: { type: 'string' },
        fixAgent: { type: 'string', enum: ['stack-builder', 'seo-optimizer', 'content-designer'] } } } },
  },
}

const GATE = {
  type: 'object', required: ['status', 'findings'],
  properties: { status: { type: 'string', enum: ['PASS', 'FAIL'] },
    findings: { type: 'array', items: { type: 'object',
      required: ['severity', 'title', 'location', 'why', 'fix', 'category'],
      properties: { severity: { type: 'string', enum: ['CRITICAL', 'HIGH', 'MEDIUM'] },
        title: { type: 'string' }, location: { type: 'string' }, why: { type: 'string' }, fix: { type: 'string' },
        category: { type: 'string', enum: ['technical','leadgen','visual','trust','seo','security','legal'] } } } } },
}

/* ─────────── ARGS ─────────── */
// args.research = absolut sökväg till research.md (obligatoriskt); Läge läses av plannern ur research-raden.
const researchPath = (args && args.research) || 'research.md in the current working directory'

/* ─────────── helper: AUTOBYGG-LOG (agenten shellar git + date; Date.now() kastar i DSL:en) ─────────── */
async function writeAutobyggLog(buildDir, fields) {
  if (!buildDir) return null
  return agent(
    `Uppdatera AUTOBYGG-LOG.md i ${buildDir}. Kör FÖRST \`cd "${buildDir}" && git rev-parse HEAD\` och \`date +%F\`. ` +
    `Om filen saknas: skapa den och INLED med detta meta-block; om den finns: appenda en ny fas-rad och uppdatera status-raden i meta-blocket:\n` +
    `<!-- nortropic-autobygg-meta\ncommit: <hash>\ndate: <YYYY-MM-DD>\nlage: obemannat\nstatus: ${fields.status}\nstage: ${fields.stage}\n-->\n` +
    `Därefter, i markdown: en fas-för-fas-spårningstabell (tidsstämpel via date, fas, utfall, ev. stopporsak) och slutstatusraden. Rådata (hitta inte på något utöver detta):\n\n` +
    JSON.stringify(fields, null, 2),
    { label: 'autobygg-log', phase: 'Avslut' }
  )
}

/* ═════════════════════════ NODKEDJAN ═════════════════════════ */

phase('Plan')
// Plannern kör sin egen INPUT GATE, läser research-radens Läge (saknas ⇒ bemannat) och returnerar utfallet maskinläsbart.
const plan = await agent(
  `Follow your FULL project-planner process against the research file at ${researchPath}. Write PROJECT-BRIEF.md next to it (all 7 sections). ` +
  `Read the research row \`Läge:\` (missing => bemannat) and write it into §6 next to Klienttyp — never into content/profile.ts. ` +
  `Run your INPUT GATE first; if fields are missing, set inputGatePassed=false + missingFields and do not plan further. ` +
  `Klassa VARJE öppen fråga STRATEGISK/FAKTA/BESLUT per your Rules; a ohanterad/scope-nej juridikflagga is ALWAYS STRATEGISK. ` +
  `Return the machine-readable outcome per the schema.`,
  { label: 'plan', phase: 'Plan', agentType: 'project-planner', schema: PLAN_OUTCOME }
)

phase('Villkorat stopp (plan)')
const modeStop = obemannatGate(plan && plan.lage)
const planStop = modeStop.stop ? modeStop : shouldStopAfterPlan(plan)
if (planStop.stop) {
  log(`ÖVERLÄMNAD vid plan: ${planStop.reason}`)
  // Inget repo skapat ännu — rent stopp; ingen AUTOBYGG-LOG (byggrepot finns inte).
  return { status: 'ÖVERLÄMNAD', stage: 'plan', reason: planStop.reason,
    briefPath: plan && plan.briefPath, openQuestions: (plan && plan.openQuestions) || [], buildDir: null, gates: [] }
}

phase('Init')
const init = await agent(
  `Execute your FULL nortropic-init/stack-builder build from the approved brief at ${plan.briefPath}. ` +
  `gh repo create <repo-name-from-§6> --private --clone into ~/Workflow/, scaffold Next.js 15 + TS strict + Tailwind 4 + shadcn/ui, ` +
  `write content/ (incl. business.ts + profile.ts from §7), all pages, app/actions/lead.ts, schema, sitemap/robots, Swedish 404/error, vercel link + deploy a preview. ` +
  `Return per schema: repoDir (ABSOLUTE path to the clone), repoUrl, previewUrl, buildPassed, envPending, todoFacts (file:line).`,
  { label: 'init', phase: 'Init', agentType: 'stack-builder', schema: INIT_OUTCOME }
)
const buildDir = init.repoDir
const previewUrl = init.previewUrl || null

phase('Del-C static-first')  // docs/06 Ring 3-guard — obemannat får aldrig tyst bygga stateful/Railway-klass infra
const guard = await agent(
  `Mechanical static-first guard in ${buildDir}. cd there. Confirm the scaffold is Ring-1 stateless per docs/06-scope: the ONLY server code is app/actions/lead.ts; NO database client (prisma/drizzle/pg/mongoose), NO auth, NO railway/render config, NO stateful booking built in-repo (external booking via link/embed is OK). ` +
  `Also flag if the approved brief §6 states an UNMET Del-C/Railway/cutover prerequisite. grep the repo. Return stateful=true with evidence if anything stateful slipped in or a Del-C prerequisite is unmet; else stateful=false.`,
  { label: 'del-c', phase: 'Del-C static-first', schema: STATICGUARD }
)
if (guard.stateful) {
  const reason = `Ring 2/3-behov (stateful eller ouppfyllt Del-C/Railway-krav): ${(guard.evidence || []).join('; ')} — obemannat överlämnar (offereras som eget arbete, docs/06 Ring 3)`
  await writeAutobyggLog(buildDir, { status: 'ÖVERLÄMNAD', stage: 'del-c', reason, previewUrl })
  return { status: 'ÖVERLÄMNAD', stage: 'del-c', reason, buildDir, previewUrl, gates: [] }
}

phase('Content')
await agent(
  `Fill every TODO-COPY in the Nortropic site at ${buildDir} in Swedish per the brief §7 voice register, then run the mandatory content-humanizer pass. cd into ${buildDir}. ` +
  `Facts ONLY from content/business.ts + content/profile.ts; anything unknown stays a TODO-FACT (never invented; keep the marker inside FAQ answers so FaqSchema drops them).`,
  { label: 'content', phase: 'Content', agentType: 'content-designer' }
)

phase('Review')
const scope = scopeStr(buildDir)
const triagePrompt = report =>
  `Read this Nortropic review report and extract ONLY the CRITICAL findings (and HIGH separately). Route each to a fixAgent: seo→seo-optimizer, copy→content-designer, everything else→stack-builder. Return criticalCount + criticals[] + highs[]. Report:\n\n${report}`

const full = await workflow('nortropic-review', { scope })   // FULL review (freshness-krav: färsk full rapport på current commit)
let triage = await agent(triagePrompt(full.report), { label: 'triage:full', phase: 'Review', schema: REVIEW_TRIAGE })

if ((triage.criticalCount || 0) > 0 || (triage.highs || []).length) {
  // EXAKT EN autonom fixloop, routad som launch.js D1, sekventiell så två agenter aldrig skriver samtidigt.
  const fixes = [...(triage.criticals || []), ...(triage.highs || [])]
  for (const ag of ['stack-builder', 'seo-optimizer', 'content-designer']) {
    const mine = fixes.filter(f => f.fixAgent === ag)
    if (!mine.length) continue
    await agent(
      `Fix mode in ${buildDir} (cd there). Fix ONLY these verified findings, minimally, then run pnpm build to zero errors, then git add -A && commit with a descriptive message. Findings: ${JSON.stringify(mine)}`,
      { label: `fix:${ag}`, phase: 'Review', agentType: ag }
    )
  }
  const diff = await workflow('nortropic-review', { scope, diff: true })  // omkontroll av endast ändrade filer
  triage = await agent(triagePrompt(diff.report), { label: 'triage:diff', phase: 'Review', schema: REVIEW_TRIAGE })
}

phase('Villkorat stopp (review)')
const reviewStop = shouldStopAfterReview(triage.criticalCount || 0)
if (reviewStop.stop) {
  await workflow('nortropic-final-touches', { clientDir: buildDir, openQuestions: plan.openQuestions })
  await writeAutobyggLog(buildDir, { status: 'ÖVERLÄMNAD', stage: 'review', reason: reviewStop.reason,
    criticals: triage.criticals, previewUrl })
  return { status: 'ÖVERLÄMNAD', stage: 'review', reason: reviewStop.reason, buildDir, previewUrl,
    criticals: triage.criticals, gates: [] }
}

phase('Grind-torrkörning')  // reproducerar launch.js:s 7 linser READ-ONLY: ingen deploy, ingen fix-loop, ingen handover
const GATE_LENSES = [
  { key: 'technical', agentType: 'qa-launcher',     lens: 'Gates 0/2/3/4 (build, Lighthouse, responsive+SSL+links, a11y)' },
  { key: 'leadgen',   agentType: 'qa-launcher',     lens: 'Gate 1 primärhandlingsgrinden — läs content/profile.ts FÖRST; SAKNAS => FAIL' },
  { key: 'seo',       agentType: 'seo-optimizer',   lens: 'audit mode + launch readiness (sitemap/robots/canonicals/schema/NAP mot business.ts)' },
  { key: 'visual',    agentType: 'design-reviewer', lens: 'anti-slop visuell QA som launch-grind' },
  { key: 'trust',     agentType: 'design-reviewer', lens: 'trust: kvitton per profile.ts, omdömen/betyg/NAP mot content' },
  { key: 'security',  agentType: 'qa-launcher',     lens: 'Gate 7 (npm audit, servade headers via curl, formulärmissbruk, hemligheter)' },
  { key: 'legal',     agentType: 'qa-launcher',     lens: 'Gate 6 svensk/EU-juridik — OBSERVE AND REPORT ONLY, läs §7-juridikflaggor' },
]
const gateArr = await parallel(GATE_LENSES.map(g => () =>
  agent(
    `${g.lens}. Run against the Nortropic site at ${buildDir}${previewUrl ? ` (preview: ${previewUrl})` : ''}. cd into ${buildDir}. ` +
    `This is a READ-ONLY GRIND-TORRKÖRNING inside /nortropic-autobygg — DO NOT fix, DO NOT deploy, DO NOT write a handover. Report PASS/FAIL + findings (category ${g.key}). ` +
    `Gate definitions come from your prelaunch skill (skills/nortropic-prelaunch) — use them as-is.`,
    { label: `gate:${g.key}`, phase: 'Grind-torrkörning', agentType: g.agentType, schema: GATE }
  )
))
const gates = Object.fromEntries(GATE_LENSES.map((g, i) => [g.key, gateArr[i] || { status: 'FAIL', findings: [] }]))
const legalFindings = (gates.legal && gates.legal.findings) || []

phase('Avslut')
await workflow('nortropic-final-touches', { clientDir: buildDir, legalFindings, openQuestions: plan.openQuestions })
const gateRows = GATE_LENSES.map(g => ({ gate: g.key,
  status: g.key === 'legal' ? '⚠️ HUMAN SIGN-OFF' : (gates[g.key].status === 'PASS' ? '✅' : '❌'),
  findings: (gates[g.key].findings || []).length }))
await writeAutobyggLog(buildDir, { status: 'BYGGD-OBEMANNAD', stage: 'complete', gateRows, previewUrl,
  deferredQuestions: (plan.openQuestions || []).filter(q => q.kind !== 'STRATEGISK') })

log(`Preview klar: ${previewUrl || '(ingen preview-url returnerad)'}. FINAL-TOUCHES.md väntar. Deploy sker aldrig obemannat.`)
return {
  status: 'BYGGD-OBEMANNAD — väntar på människa: FINAL-TOUCHES (fakta, beslut, juridik-signoff nod 8), sedan /nortropic-launch + /vercel:deploy (nod 9)',
  buildDir, previewUrl, gates: gateRows, legalFindings,
}
