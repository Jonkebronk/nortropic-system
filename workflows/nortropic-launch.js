export const meta = {
  name: 'nortropic-launch',
  description: 'Pre-launch gate for a Nortropic site: 7 parallel audit lenses, bounded fix-loop (legal always stops for human), Swedish handover doc, launch readiness report',
  whenToUse: 'Run when a Nortropic client site is believed ready to launch, before /vercel:deploy',
  phases: [
    { title: 'Gates', detail: '7 parallel audit lenses' },
    { title: 'Fix loop', detail: 'max 3 rounds via stack-builder; legal never auto-fixed' },
    { title: 'Eval', detail: 'non-blocking quality score via nortropic-eval (informs report only)' },
    { title: 'Handover', detail: 'GBP/GSC deliverables + Swedish client handover doc' },
    { title: 'Report', detail: 'launch readiness verdict' },
  ],
}

const GATE = {
  type: 'object',
  required: ['status', 'findings'],
  properties: {
    status: { type: 'string', enum: ['PASS', 'FAIL'] },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['severity', 'title', 'location', 'why', 'fix', 'category'],
        properties: {
          severity: { type: 'string', enum: ['CRITICAL', 'HIGH', 'MEDIUM'] },
          title: { type: 'string' },
          location: { type: 'string' },
          why: { type: 'string' },
          fix: { type: 'string' },
          category: { type: 'string', enum: ['technical', 'leadgen', 'visual', 'trust', 'seo', 'security', 'legal'] },
        },
      },
    },
  },
}

const EVAL = {
  type: 'object',
  required: ['total', 'faktatrohet', 'band'],
  properties: {
    total: { type: 'number' },
    faktatrohet: { type: 'string', enum: ['PASS', 'FAIL'] },
    band: { type: 'string' },
    version: { type: 'string' },
    topBrister: { type: 'array', items: { type: 'string' } },
    resultPath: { type: 'string' },
  },
}

const site = (args && args.url) ? `the Nortropic site in the current working directory (preview URL: ${args.url})` : 'the Nortropic site in the current working directory (find the preview/dev URL from vercel or start the dev server if needed)'
const structured = 'Return PASS only if every check passes. Every finding needs severity, exact location, why it matters, concrete fix, and category.'

const GATES = [
  { key: 'technical', agentType: 'qa-launcher', prompt: `Run Gates 0, 2, 3 and 4 of your prelaunch process (build integrity; Lighthouse/Core Web Vitals with real median-of-3 numbers; responsive 375/390/768/1280/1920 + link crawl + SSL; accessibility — keyboard-only operability, focus visibility, skip-link, contrast ≥4.5:1, meaningful Swedish alt text, prefers-reduced-motion, heading order / one h1) against ${site}.\n\nINGÅR (din gate): build-integritet, Lighthouse/Core Web Vitals, responsivitet, länkcrawl, SSL, döda länkar, tillgänglighet (Gate 4).\nINGÅR INTE (annan gate äger): lead-kedjan formulär→mejl, tel-länkar, CTA → leadgen-gaten; visuellt utseende → visual-gaten.\nCategory for findings: technical. ${structured}` },
  { key: 'leadgen', agentType: 'qa-launcher', prompt: `Run Gate 1 (lead generation) of your prelaunch process against ${site}: tel: links at mobile viewport, phone in sticky header everywhere, floating call button, quote form submitted end-to-end with [TEST] data and EMAIL DELIVERY verified (Resend status — a 200 is not delivery), form error fallback shows phone, CTA above fold per page, phone_click/quote_submit events fire, 404/error pages show phone.\n\nINGÅR (din gate): HELA lead-kedjan — tel-länkar, sticky nummer, flytande ringknapp, offertformulär end-to-end + verifierad e-postleverans, CTA above fold, konverteringsevent, telefon på 404/error.\nINGÅR INTE (annan gate äger): prestanda/CWV → technical-gaten; visuellt utseende → visual-gaten; schema/meta → seo-gaten.\nCategory: leadgen. ${structured}` },
  { key: 'seo', agentType: 'seo-optimizer', prompt: `Final pre-launch SEO audit of ${site}: audit mode across all pages + launch readiness (sitemap/robots served, canonicals, schema validates, NAP consistency, GSC DNS verification status — ask nothing, report what you can verify).\n\nINGÅR (din gate): meta/titles/canonicals, schema-validitet, NAP-konsistens, sitemap/robots, GSC DNS-status.\nINGÅR INTE (annan gate äger): copykvalitet och slop → visual-gaten; prestanda → technical-gaten.\nCategory: seo. ${structured}` },
  { key: 'visual', agentType: 'design-reviewer', prompt: `Final visual QA of ${site}: run your anti-slop review as a launch gate. FAIL on any CRITICAL conversion blocker or instant-fail slop pattern.\n\nINGÅR (din gate): visuell layout/hierarki, responsivitet, typografi, bildrendering, slop/AI-mönster.\nINGÅR INTE (annan gate äger): INNEHÅLLET/sanningen i förtroendesignaler (stämmer omdömen/betyg/certifikat/NAP) → trust-gaten; meta/schema → seo-gaten.\nCategories: visual (design issues) or leadgen (conversion blockers). ${structured}` },
  { key: 'trust', agentType: 'design-reviewer', prompt: `Trust audit of ${site} — a distinct lens from visual QA: verify every trust element is real and consistent. Omdömen have namn+ort and match content/testimonials.ts, betyg matches content/business.ts rating, certifikat badges correspond to business.ts certifications, NAP in footer = business.ts exactly, garanti/jour/response-time claims appear only where the content files back them, org.nr + F-skatt present.\n\nINGÅR (din gate): INNEHÅLLET/sanningen i förtroendesignaler — omdömen (namn+ort, matchar testimonials.ts), betyg matchar business.ts, certifikat äkta, NAP=business.ts exakt, garanti/jour/restid-claims backade i content, org.nr+F-skatt.\nINGÅR INTE (annan gate äger): HUR de ser ut → visual-gaten; juridisk fullständighet (integritetspolicy/cookies) → legal-gaten.\nCategory: trust. ${structured}` },
  { key: 'security', agentType: 'qa-launcher', prompt: `Run Gate 7 (säkerhet) of your prelaunch process against ${site}: npm audit --omit=dev (FAIL on high/critical in PROD dependencies only); verify security headers ACTUALLY SERVED via curl -sI against the preview URL (Content-Security-Policy, Strict-Transport-Security, X-Content-Type-Options: nosniff, Referrer-Policy: strict-origin-when-cross-origin, frame-ancestors 'none' or X-Frame-Options: DENY — canonical fix is headers() in next.config.ts per your security-checklist reference); form-abuse protection on the quote endpoint (honeypot silent-200, time-trap on a client-measured elapsedMs duration (single clock, never a client timestamp vs the server clock; missing/0 fails open), server-side validation with length caps + email format, recipient hardcoded from env LEAD_TO_EMAIL — NEVER from request body = CRITICAL open spam relay, generic client errors with no env names/stacks/Resend responses; platform-level rate limiting is an optional NOTE, never a DB-based limiter); secrets (no key values in .next/static or repo/git history, .env* git-ignored, API keys server-code only).\n\nINGÅR (din gate): npm audit prod-beroenden, servade säkerhetsheaders, formulärmissbruk (honeypot/tidsfälla/validering/fast mottagare/generiska fel), hemligheter i bundle/repo.\nINGÅR INTE (annan gate äger): SSL/länkcrawl → technical-gaten; att formuläret LEVERERAR mejl → leadgen-gaten; cookies/samtycke → legal-gaten.\nCategory: security. ${structured}` },
  { key: 'legal', agentType: 'qa-launcher', prompt: `Run ONLY Gate 6 (Swedish/EU legal) of your prelaunch process against ${site}: Integritetspolicy completeness per your legal-requirements-se reference, cookie/consent situation (verify what actually loads — cookieless Vercel Analytics vs anything requiring consent), Företagsuppgifter in footer, Google Fonts CDN absence, claims verifiability, ångerrätt applicability. OBSERVE AND REPORT ONLY.\n\nINGÅR (din gate): integritetspolicy-fullständighet, cookie/samtycke (vad som faktiskt laddas), Företagsuppgifter, Google Fonts CDN-frånvaro, claims-verifierbarhet, ångerrätt.\nINGÅR INTE (annan gate äger): fixar (legal är ALLTID human-only — föreslå aldrig auto-fix); förtroende-utseende → visual/trust.\nCategory: legal for every finding. ${structured}` },
]

phase('Gates')
log('Running 7 audit lenses in parallel')
let gateResults = await parallel(GATES.map(g => () =>
  agent(g.prompt, { label: `gate:${g.key}`, phase: 'Gates', schema: GATE })
))
let gates = Object.fromEntries(GATES.map((g, i) => [g.key, gateResults[i] || { status: 'FAIL', findings: [{ severity: 'CRITICAL', title: `${g.key} gate did not complete`, location: 'workflow', why: 'auditor agent failed or was skipped', fix: 'rerun /nortropic-launch', category: g.key === 'legal' ? 'legal' : 'technical' }] }]))

const legalFindings = gates.legal.findings || []

phase('Fix loop')
let round = 0
const fixLog = []
while (round < 3) {
  const failing = GATES.filter(g => g.key !== 'legal' && gates[g.key].status === 'FAIL')
  if (!failing.length) break
  round += 1
  const fixable = failing.flatMap(g => (gates[g.key].findings || []).filter(f => f.category !== 'legal'))
  if (!fixable.length) break
  log(`Fix round ${round}/3: ${fixable.length} findings across ${failing.map(g => g.key).join(', ')}`)
  // D1: route by category — seo findings to seo-optimizer (it can Edit meta/schema), the rest to stack-builder.
  // Sequential (not parallel) so two fixers never write the repo at once.
  const seoFixable = fixable.filter(f => f.category === 'seo')
  const buildFixable = fixable.filter(f => f.category !== 'seo')
  const fixReports = []
  if (buildFixable.length) {
    const r = await agent(
      `Fix mode. Fix ONLY these verified launch-gate findings in the Nortropic site in the current working directory, minimally, then run pnpm build and confirm zero errors. Report per finding: fixed / needs-human (with reason).\n\n${JSON.stringify(buildFixable, null, 2)}`,
      { label: `fix:build:round${round}`, phase: 'Fix loop', agentType: 'stack-builder' }
    )
    fixReports.push({ agent: 'stack-builder', report: typeof r === 'string' ? r.slice(0, 1500) : r })
  }
  if (seoFixable.length) {
    const r = await agent(
      `Fix mode (SEO). Fix ONLY these verified SEO launch-gate findings (meta/titles/schema/NAP/sitemap) in the Nortropic site in the current working directory, minimally, then confirm the build. Report per finding: fixed / needs-human (with reason).\n\n${JSON.stringify(seoFixable, null, 2)}`,
      { label: `fix:seo:round${round}`, phase: 'Fix loop', agentType: 'seo-optimizer' }
    )
    fixReports.push({ agent: 'seo-optimizer', report: typeof r === 'string' ? r.slice(0, 1500) : r })
  }
  fixLog.push({ round, findings: fixable.length, reports: fixReports })
  const recheck = await parallel(failing.map(g => () =>
    agent(GATES.find(x => x.key === g.key).prompt + ' This is a RE-CHECK after fixes: verify the previously failing checks first.', { label: `recheck:${g.key}:r${round}`, phase: 'Fix loop', agentType: g.agentType, schema: GATE })
  ))
  failing.forEach((g, i) => { if (recheck[i]) gates[g.key] = recheck[i] })
}

const nonLegalPass = GATES.filter(g => g.key !== 'legal').every(g => gates[g.key].status === 'PASS')

// v5: non-blocking quality eval. Runs only once the non-legal gates pass — the GATES block launch,
// the eval only measures. Its score informs the report and feeds retro's cross-client comparison.
let evalResult = null
if (nonLegalPass) {
  phase('Eval')
  evalResult = await agent(
    `Run the nortropic-eval quality rubric against ${site}. Read ~/.claude/skills/nortropic-eval/SKILL.md and its references/eval-rubric.md, then score all 10 criteria in ONE coherent judgment, apply the Faktatrohet hard-gate, and WRITE the scorecard to EVAL-RESULT.md in the project root (stamped with today's date and the rubric version). This is INFORMATIONAL — it does not gate the launch. Return the structured result (total, faktatrohet PASS/FAIL, band, version, top brister, resultPath).`,
    { label: 'eval:rubric', phase: 'Eval', schema: EVAL }
  )
}

phase('Handover')
let handover = null
if (nonLegalPass || round >= 3) {
  const seoDeliverables = await agent(
    `Deliverables mode for the Nortropic site in the current working directory: produce the per-client Google Företagsprofil checklist (filled with THIS client's data from content/business.ts and the services) and the concrete Google Search Console launch steps. Write them to gbp-checklist-klient.md and gsc-steg-klient.md in the project root and return a short summary of both.`,
    { label: 'handover:seo-deliverables', phase: 'Handover', agentType: 'seo-optimizer' }
  )
  handover = await agent(
    `Write the Swedish client handover document for the Nortropic site in the current working directory as HANDOVER.md in the project root. Audience: the business owner (not technical). Sections: 1) Din nya webbplats (pages, what each does), 2) Så får du dina leads (where quote emails arrive, what a lead looks like, what to do), 3) Uppdatera innehåll (how to request changes via Nortropic; which facts live where), 4) Google Företagsprofil — din checklista (incorporate gbp-checklist-klient.md), 5) Google Search Console — de första 2 veckorna (incorporate gsc-steg-klient.md), 6) Support & kontakt. Voice: clear, warm, zero jargon. Context from SEO deliverables: ${typeof seoDeliverables === 'string' ? seoDeliverables.slice(0, 3000) : JSON.stringify(seoDeliverables).slice(0, 3000)}`,
    { label: 'handover:doc', phase: 'Handover', agentType: 'content-designer' }
  )
}

phase('Report')
const rows = GATES.map(g => {
  const r = gates[g.key]
  const status = g.key === 'legal' ? (legalFindings.length ? '⚠️ HUMAN REVIEW' : '⚠️ HUMAN SIGN-OFF (no findings, still requires sign-off)') : (r.status === 'PASS' ? '✅ PASS' : '❌ FAIL')
  return { gate: g.key, status, findings: (r.findings || []).length }
})
const evalNote = evalResult
  ? ` | Kvalitetseval: ${evalResult.total}/100${evalResult.faktatrohet === 'FAIL' ? ' — FAKTATROHET FAIL (granska innan lansering)' : ` (${evalResult.band})`}`
  : ''
const verdict = (nonLegalPass
  ? (legalFindings.length ? 'BLOCKED — technical gates pass, LEGAL FINDINGS REQUIRE HUMAN JUDGMENT before launch' : 'READY — pending human legal sign-off, then run /vercel:deploy')
  : `BLOCKED — gates still failing after ${round} fix round(s); remaining findings need human attention`) + evalNote

// v5: merge identical findings flagged by more than one gate — count once, record which gates flagged
const remainingRaw = GATES.filter(g => g.key !== 'legal' && gates[g.key].status === 'FAIL').flatMap(g => (gates[g.key].findings || []).map(f => ({ ...f, gate: g.key })))
const remMap = new Map()
for (const f of remainingRaw) {
  const k = `${(f.location || '').trim().toLowerCase()}|${(f.title || '').trim().toLowerCase()}`
  const e = remMap.get(k)
  if (e) e.gates = Array.from(new Set([...(e.gates || [e.gate]), f.gate]))
  else remMap.set(k, { ...f, gates: [f.gate] })
}
const remainingFindings = Array.from(remMap.values())

return {
  verdict,
  gates: rows,
  eval: evalResult,
  legalFindings,
  remainingFindings,
  fixRounds: fixLog,
  handoverWritten: Boolean(handover),
}
