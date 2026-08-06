export const meta = {
  name: 'nortropic-launch',
  description: 'Pre-launch gate for a Nortropic site: 7 parallel audit lenses, bounded fix-loop (legal always stops for human), Swedish handover doc, launch readiness report',
  whenToUse: 'Run when a Nortropic client site is believed ready to launch, before /vercel:deploy',
  phases: [
    { title: 'Freshness', detail: 'block launch if the last FULL review predates changes on the main pages' },
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

// ─────────── BATCH-005-fixkontrakt (DEL 1, launch): returkontrakt för ändrade filer ───────────
// Fixagenterna deklarerar sin ändrade-fil-lista per schema (DIFFSCOPE-formen ur nortropic-review.js:
// files: string[] + mekanisk rapportdisciplin) och release-steget stagear EXAKT den mängden —
// aldrig svepande staging (-A/-u; -u missar dessutom nya filer → rorjour-buggen). Alla kontrakts-
// beslut fattas i ren JS nedan, aldrig i agentprosa. Delta-snapshoten (git status --porcelain -uall
// före/efter rundan) gör alla fyra felmoder mekaniskt kontrollerbara. Kontraktsbrott BLOCKERAR
// rundan utan commit — aldrig tyst degradering (samma klass som INV-005 INVALID→FAIL och
// verify-suitens "en död probe är odömbar → OGILTIG, aldrig tyst grön"). Stageningen använder
// snittet declared ∩ efter-snapshot (endast delta-verifierade VERKLIGA filer når git; kataloger,
// globs och fantomsökvägar kan per definition inte stå i porcelain-utdata), pathspecs literaliseras
// (--literal-pathspecs — [slug]-routes är literala filnamn, inte mönster), committen är pathspec:ad
// (för-stagat främmande innehåll åker aldrig med) och commit-UTFALLET efterkontrolleras mekaniskt
// mot den stageade mängden — sista ledet vilar inte på prosa (adversariell granskning 2026-08-06).
// Kärnan nedan är delad med nortropic-autobygg.js (DEL 2) — DSL-filer kan inte importera varandra,
// så den är MEDVETET duplicerad och hålls byte-identisk; INV-006 hashar båda blocken.

// ─────────── FIXKONTRAKT-KÄRNA (BATCH-005) — BYTE-IDENTISK i nortropic-autobygg.js och nortropic-launch.js; INV-006 hashar båda blocken och flaggar avvikelse ───────────

const FILELIST = {
  type: 'object',
  required: ['files'],
  properties: {
    files: { type: 'array', items: { type: 'string' }, description: 'repo-relativa sökvägar' },
    head: { type: 'string', description: 'full git HEAD-hash (40 hex) när prompten begär den' },
    note: { type: 'string' },
  },
}

// HEAD-spårningen är kontraktets ankare mot två felmoder som ligger UTANFÖR porcelain-deltat:
// en agent som committar SJÄLV (HEAD flyttar under fasen → trädet ser rent ut och deltat blir
// blint) och ett commit-steg som aldrig committade (HEAD står stilla → efterkontrollen jämför
// mot FEL commit). Adversariell granskning DEL 2, 2026-08-06.
function validHead(h) {
  return /^[0-9a-f]{40}$/.test(String(h || '').trim())
}

// Normalisering före mängdjämförelse: porcelain ger alltid framåtslash; en agent på Windows kan
// returnera backslash eller ledande "./" — samma fil får inte räknas som två. Case röras aldrig
// (skulle dölja verkliga avvikelser).
function normPath(p) {
  return String(p || '').trim().replace(/\\/g, '/').replace(/^\.\//, '')
}

// Felmod 3: fil utanför byggkatalogen. Endast repo-relativa sökvägar — absolut sökväg (POSIX eller
// enhetsbokstav), '..'-segment, citattecken/radbrytning eller tom sträng avvisas; likaså $ och
// backtick (shell-aktiva ÄVEN inom dubbelcitat — deklarationen interpoleras i stagingkommandot,
// och agentreturer är opålitlig data). Legitima Next.js-sökvägar (app/[stad]/, app/(grupp)/, @modal)
// bär inget av tecknen. Deterministiskt, aldrig prosa.
function badRepoPaths(files) {
  return (files || []).filter(raw => {
    const p = normPath(raw)
    return !p || p.startsWith('/') || /^[A-Za-z]:/.test(p) || p.split('/').includes('..') || /["\n\r$`]/.test(p)
  })
}

// Delta-jämförelsen som gör felmod 1/2 kontrollerbara:
//   undeclared    = smutsig EFTER rundan, ren FÖRE, ej deklarerad → utelämnad fil (felmod 1, BLOCKERA)
//   foreign       = deklarerad men redan smutsig FÖRE rundan → commit skulle smuggla in främmande
//                   ändringar (felmod 2b, BLOCKERA)
//   cleanDeclared = deklarerad men aldrig smutsig → överdeklaration (felmod 2a, WARN — posten
//                   utesluts ur stageningen via snittet declared ∩ post; den når aldrig git)
// Känd begränsning (registrerad i programregistret): en fil som var smutsig FÖRE rundan och ändras
// IGEN av fixern kan inte särskiljas mekaniskt — deklareras den blockeras rundan som foreign (säkra sidan).
function fixDelta(preFiles, postFiles, declaredFiles) {
  const pre = new Set((preFiles || []).map(normPath))
  const post = new Set((postFiles || []).map(normPath))
  const declared = (declaredFiles || []).map(normPath)
  return {
    undeclared: [...post].filter(f => !pre.has(f) && !declared.includes(f)),
    foreign: declared.filter(f => pre.has(f)),
    cleanDeclared: declared.filter(f => !post.has(f)),
  }
}

// Z1-arbetsloggen (AGENT-LOG.md) är undantagen kontraktet: agentdefinitionerna beordrar friktions-
// loggning MITT i arbetet (stack-builder/seo-optimizer/content-designer Z1-regeln), och tidigare
// faser kan redan ha lämnat ett ocommittat block — utan namngivet undantag fäller systemets EGEN
// loggdisciplin rundan som falsk felmod 1/2b. Loggen commitas aldrig av kontraktets commit-steg
// (efterkontrollen fäller en commit som ändå innehåller den); dess hemvist avgörs utanför workflowet.
const CONTRACT_EXEMPT = f => normPath(f) === 'AGENT-LOG.md'

// -uall är bärande: utan den listar porcelain en NY katalog som "dir/" i stället för filerna i den,
// och en ärligt deklarerad ny fil skulle falskblockeras som undeclared-mismatch. quotepath=off är
// lika bärande: med gits default oktalescapas åäö-sökvägar ('"tj\303\244nster.ts"') och kan då
// aldrig matcha fixarens deklarerade UTF-8-form → deterministisk falsk felmod-1 i en svensk pipeline.
// OBS (par-regeln): commit-stegens och commit-inspektionens promptar är FLÖDESSPECIFIKA och ligger
// UTANFÖR denna hashade kärna — INV-006 vaktar dem INTE; de ändras alltid i PAR i båda filerna.
const porcelainPrompt = (when, where) =>
  `Mechanical working-tree snapshot (${when}) in the project root of ${where}. Run exactly: git -c core.quotepath=off status --porcelain -uall. Return every repo-relative path it lists (modified, staged, deleted and untracked; for a rename list BOTH the old and the new path). Return BARE paths only: strip the two-character status prefix and the space after it, and strip any surrounding double quotes around paths that git still quotes. Also run exactly: git rev-parse HEAD — return the full 40-character hash as head. Do not filter or judge — report mechanically. A clean tree returns files: []. If a git command fails or you are not in a git project root, do NOT guess and do NOT report a clean tree — put exactly what failed in note.`

// ─────────── SLUT FIXKONTRAKT-KÄRNA (BATCH-005) ───────────

const site = (args && args.url) ? `the Nortropic site in the current working directory (preview URL: ${args.url})` : 'the Nortropic site in the current working directory (find the preview/dev URL from vercel or start the dev server if needed)'
const structured = 'Return PASS only if every check passes. Every finding needs severity, exact location, why it matters, concrete fix, and category.'
// Deployment Protection-bypass: Gate 7 kräver att preview har Vercel Deployment Protection på (naken .vercel.app → 401). Alla URL-baserade grindar UTOM Gate 7:s egen protection-assertion måste därför bära bypass-hemligheten, annars FAILar de av fel skäl. En hemvist — appendas på varje gate-prompt (initial + recheck).
const bypass = ' DEPLOYMENT PROTECTION: om preview-deployen har Vercel Deployment Protection på (Gate 7 kräver det) svarar en naken .vercel.app-förfrågan 401 — varje URL-baserad kontroll UTOM Gate 7:s egen protection-assertion måste autentisera via Protection Bypass for Automation: hemligheten VERCEL_AUTOMATION_BYPASS_SECRET som headern x-vercel-protection-bypass (curl/fetch) eller query ?x-vercel-protection-bypass=<secret>&x-vercel-set-bypass-cookie=true (webbläsare/Lighthouse/Playwright — cookien håller bypassen genom sessionen). LÄCKSKYDD (obligatoriskt där query-formen används): hemligheten får ALDRIG återges i en URL i rapporter, loggar, konsolutskrift, skärmdumpar eller filnamn — query-formen används ENDAST i själva verktygsanropet som sätter bypass-cookien, därefter bär cookien bypassen. Header-formen går inte att sätta i kedjans verktyg och cookien går inte att försätta direkt (verifierat mot MCP-schemana), så query-formen är nödvändig — men dess URL återanvänds aldrig i utdata. Ett 401 på någon ANNAN kontroll = saknad/fel bypass-hemlighet i verktyget, inte ett sajtfel.'

// v8 freshness gate: launch refuses to run if the last FULL review predates changes on the main pages.
const FRESH = {
  type: 'object',
  required: ['status'],
  properties: {
    status: { type: 'string', enum: ['FRESH', 'STALE', 'MISSING'] },
    scope: { type: 'string' },
    commit: { type: 'string' },
    newerCommits: { type: 'number' },
    detail: { type: 'string' },
  },
}

phase('Freshness')
const fresh = await agent(
  `Mechanical pre-launch freshness check in the project root of the Nortropic site in the current working directory. Do exactly this:\n` +
  `1) Read REVIEW-REPORT.md. If the file is missing → return status MISSING with detail "ingen granskningsrapport — kör en FULL /nortropic-review först".\n` +
  `2) Parse commit and scope from its <!-- nortropic-review-meta --> comment block. Unparseable → MISSING.\n` +
  `3) If scope is not "full" → return STALE with detail "senaste granskningen var DIFF-SKOPAD — pre-launch kräver en FULL /nortropic-review".\n` +
  `4) Run git log --oneline <commit>..HEAD -- src content. Any commits listed → STALE with the count in newerCommits and a one-line detail. Otherwise → FRESH.\n` +
  `Judge nothing; report mechanically.`,
  { label: 'freshness', phase: 'Freshness', schema: FRESH }
)
if (!fresh || fresh.status !== 'FRESH') {
  return {
    verdict: `BLOCKED-STALE — ${fresh && fresh.detail ? fresh.detail : 'freshness-checken kunde inte köras'}. Kör en FULL /nortropic-review på nuvarande commit, sedan /nortropic-launch igen.`,
    freshness: fresh || null,
    gates: [],
    eval: null,
    legalFindings: [],
    remainingFindings: [],
    fixRounds: [],
    contractStop: null,
    handoverWritten: false,
  }
}

const GATES = [
  { key: 'technical', agentType: 'qa-launcher', prompt: `Run Gates 0, 2, 3 and 4 of your prelaunch process (build integrity; Lighthouse/Core Web Vitals with real median-of-3 numbers; responsive 375/390/768/1280/1920 + link crawl + SSL; accessibility — keyboard-only operability, focus visibility, skip-link, contrast ≥4.5:1, meaningful Swedish alt text, prefers-reduced-motion, heading order / one h1; klickytor/target size ≥24×24 px per WCAG 2.2, helst 44×44 på mobil; axe-core noll violations mot wcag2a/wcag2aa/wcag21aa/wcag22aa som mekanisk komplettering, ersätter inte de manuella punkterna) against ${site}.\n\nINGÅR (din gate): build-integritet, Lighthouse/Core Web Vitals, responsivitet, länkcrawl, SSL, döda länkar, tillgänglighet (Gate 4, inkl. target size ≥24×24 + axe-core noll violations).\nINGÅR INTE (annan gate äger): lead-kedjan formulär→mejl, tel-länkar, CTA → leadgen-gaten; visuellt utseende → visual-gaten.\nCategory for findings: technical. ${structured}` },
  { key: 'leadgen', agentType: 'qa-launcher', prompt: `Run Gate 1 (primärhandlingsgrinden) of your prelaunch process against ${site}. Läs FÖRST content/profile.ts i byggrepot: primaraktion + gate1Test definierar exakt vad som testas end-to-end. SAKNAS content/profile.ts = Gate 1 FAIL med tydligt meddelande — kör aldrig på gissad default. Invarianter oavsett primärhandling: primärhandlingen nåbar above fold på varje sida, mobilergonomisk, testad PÅ RIKTIGT end-to-end, fallback vid fel, konverteringsevent avfyras. OFFERT/SAMTAL-FALLET (hantverkar-defaulten) = exakt: tel: links at mobile viewport, phone in sticky header everywhere, floating call button, quote form submitted end-to-end with [TEST] data and EMAIL DELIVERY verified (Resend status — a 200 is not delivery), form error fallback shows phone, CTA above fold per page, phone_click/quote_submit events fire, 404/error pages show phone. BOKA/PLATSFÖRFRÅGAN/BESÖK: motsvarande kedja per gate1Test (t.ex. boka-flödet når extern bokning och fungerar, event spåras, felväg visar kontaktväg) — kravnivån identisk, genomförandet är testet.\n\nINGÅR (din gate): HELA primärhandlingskedjan per profile.ts — för offert/samtal: tel-länkar, sticky nummer, flytande ringknapp, offertformulär end-to-end + verifierad e-postleverans, CTA above fold, konverteringsevent, telefon på 404/error.\nINGÅR INTE (annan gate äger): prestanda/CWV → technical-gaten; visuellt utseende → visual-gaten; schema/meta → seo-gaten.\nCategory: leadgen. ${structured}` },
  { key: 'seo', agentType: 'seo-optimizer', prompt: `Final pre-launch SEO audit of ${site}: audit mode across all pages + launch readiness (sitemap/robots served, canonicals, schema validates, NAP consistency, GSC DNS verification status; robots.txt blockerar inte AI-crawlers på skarp klient (GPTBot/PerplexityBot/ClaudeBot/OAI-SearchBot under Disallow = HIGH; TESTKLIENT undantaget); address.publik→PostalAddress-konsistens och postalCode-format enligt dina hårda regler (false+PostalAddress=CRITICAL, true-utan-PostalAddress=HIGH, fel postalCode-format=CRITICAL); Bing Webmaster-property importerad från GSC med sitemap inskickad; IndexNow-nyckelfil svarar 200 i webbroten — ask nothing, report what you can verify).\n\nINGÅR (din gate): meta/titles/canonicals, schema-validitet, NAP-konsistens, sitemap/robots, GSC DNS-status, AI-crawler-robots, address.publik→PostalAddress + postalCode-format, Bing Webmaster, IndexNow.\nINGÅR INTE (annan gate äger): copykvalitet och slop → visual-gaten; prestanda → technical-gaten.\nCategory: seo. ${structured}` },
  { key: 'visual', agentType: 'design-reviewer', prompt: `Final visual QA of ${site}: run your anti-slop review as a launch gate. FAIL on any CRITICAL conversion blocker or instant-fail slop pattern.\n\nINGÅR (din gate): visuell layout/hierarki, responsivitet, typografi, bildrendering, slop/AI-mönster.\nINGÅR INTE (annan gate äger): INNEHÅLLET/sanningen i förtroendesignaler (stämmer omdömen/betyg/certifikat/NAP) → trust-gaten; meta/schema → seo-gaten.\nCategories: visual (design issues) or leadgen (conversion blockers). ${structured}` },
  { key: 'trust', agentType: 'design-reviewer', prompt: `Trust audit of ${site} — a distinct lens from visual QA: verify every trust element is real and consistent. KVITTOLISTAN i content/profile.ts är facit för VILKA förtroendekvitton denna kund har (F-skatt/certifikat, utbildningar, portfolio, omdömen, försäkring, fysisk plats) och dess attributionsregler styr bedömningen (t.ex. utbildning redovisas som utbildning, aldrig som utfall). Verifiera: omdömen have namn+ort and match content/testimonials.ts, betyg matches content/business.ts rating, certifikat/kvitton badges correspond to business.ts/profile.ts, NAP in footer = business.ts exactly, garanti/tillgänglighets-/tidsclaims appear only where the content files back them, org.nr + F-skatt present (invariant för näringsidkare).\n\nINGÅR (din gate): INNEHÅLLET/sanningen i förtroendesignaler — kvitton per profile.ts kvittolista + attributionsregler, omdömen (namn+ort, matchar testimonials.ts), betyg matchar business.ts, NAP=business.ts exakt, claims backade i content, org.nr+F-skatt.\nINGÅR INTE (annan gate äger): HUR de ser ut → visual-gaten; juridisk fullständighet (integritetspolicy/cookies) → legal-gaten.\nCategory: trust. ${structured}` },
  { key: 'security', agentType: 'qa-launcher', prompt: `Run Gate 7 (säkerhet) of your prelaunch process against ${site}: npm audit --omit=dev (FAIL on high/critical in PROD dependencies only); verify security headers ACTUALLY SERVED via curl -sI against the preview URL (Content-Security-Policy, Strict-Transport-Security, X-Content-Type-Options: nosniff, Referrer-Policy: strict-origin-when-cross-origin, frame-ancestors 'none' or X-Frame-Options: DENY — canonical fix is headers() in next.config.ts per your security-checklist reference); form-abuse protection on the quote endpoint (honeypot silent-200, time-trap on a client-measured elapsedMs duration (single clock, never a client timestamp vs the server clock; missing/0 fails open), server-side validation with length caps + email format, recipient hardcoded from env LEAD_TO_EMAIL — NEVER from request body = CRITICAL open spam relay, generic client errors with no env names/stacks/Resend responses; platform-level rate limiting is an optional NOTE, never a DB-based limiter); secrets (no key values in .next/static or repo/git history, .env* git-ignored, API keys server-code only); Deployment Protection på preview: en NAKEN .vercel.app-URL (ingen bypass) ger 401 — noindex räcker inte, en indexerbar preview-URL kan ranka mot kundens riktiga domän (denna check gör medvetet en naken förfrågan; alla andra URL-kontroller använder bypass per noten); /api/puls-kontraktet: mottagare LEAD_TEST_TO ur env (aldrig request body), token PULS_TOKEN ur env, saknad/fel token → 404 (samma öppna-spamrelä-krav som lead-endpointen).\n\nINGÅR (din gate): npm audit prod-beroenden, servade säkerhetsheaders, formulärmissbruk (honeypot/tidsfälla/validering/fast mottagare/generiska fel), hemligheter i bundle/repo, Deployment Protection-401 på preview, /api/puls-kontraktet.\nINGÅR INTE (annan gate äger): SSL/länkcrawl → technical-gaten; att formuläret LEVERERAR mejl → leadgen-gaten; cookies/samtycke → legal-gaten.\nCategory: security. ${structured}` },
  { key: 'legal', agentType: 'qa-launcher', prompt: `Run ONLY Gate 6 (Swedish/EU legal) of your prelaunch process against ${site}: Integritetspolicy completeness per your legal-requirements-se reference, cookie/consent situation (verify what actually loads — cookieless Vercel Analytics vs anything requiring consent), Företagsuppgifter in footer, Google Fonts CDN absence, claims verifiability, ångerrätt applicability. LÄS DESSUTOM juridikflaggor ur content/profile.ts och rapportera per aktiv flaggas kravlista (nortropic-plan/references/juridikflaggor.md) utöver basen. OBSERVE AND REPORT ONLY.\n\nINGÅR (din gate): integritetspolicy-fullständighet, cookie/samtycke (vad som faktiskt laddas), Företagsuppgifter, Google Fonts CDN-frånvaro, claims-verifierbarhet, ångerrätt.\nINGÅR INTE (annan gate äger): fixar (legal är ALLTID human-only — föreslå aldrig auto-fix); förtroende-utseende → visual/trust.\nCategory: legal for every finding. ${structured}` },
]

phase('Gates')
log('Running 7 audit lenses in parallel')
let gateResults = await parallel(GATES.map(g => () =>
  agent(g.prompt + bypass, { label: `gate:${g.key}`, phase: 'Gates', schema: GATE })
))
let gates = Object.fromEntries(GATES.map((g, i) => [g.key, gateResults[i] || { status: 'FAIL', findings: [{ severity: 'CRITICAL', title: `${g.key} gate did not complete`, location: 'workflow', why: 'auditor agent failed or was skipped', fix: 'rerun /nortropic-launch', category: g.key === 'legal' ? 'legal' : 'technical' }] }]))

const legalFindings = gates.legal.findings || []

phase('Fix loop')
let round = 0
let freshUrl = (args && args.url) ? args.url : null   // repointed to each round's redeploy
const fixLog = []
let contractStop = null   // BATCH-005: brutet fixkontrakt → rundan blockeras utan commit, loopen avslutas
// Bemannat: upp till 3 autonoma fixrundor med en människa som övervakar. Obemannat (nortropic-autobygg.js) gör MEDVETET bara EN runda och lämnar sedan över — ingen vaktar där, så det är försiktigare. 1-vs-3 är avsiktligt; harmonisera aldrig. Gränsen 3 är §A-skyddad (docs/07 §A3) — ändras bara av människa.
while (round < 3) {
  const failing = GATES.filter(g => g.key !== 'legal' && gates[g.key].status === 'FAIL')
  if (!failing.length) break
  round += 1
  const fixable = failing.flatMap(g => (gates[g.key].findings || []).filter(f => f.category !== 'legal'))
  if (!fixable.length) break
  log(`Fix round ${round}/3: ${fixable.length} findings across ${failing.map(g => g.key).join(', ')}`)
  // BATCH-005: snapshot FÖRE rundan — utan den är deltat odömbart → blockera innan fixarbete slösas.
  const preSnap = await agent(porcelainPrompt(`before fix round ${round}`, 'the Nortropic site in the current working directory'), { label: `snapshot:pre:r${round}`, phase: 'Fix loop', schema: FILELIST })
  if (!preSnap) { contractStop = { round, rule: 'snapshot', detail: 'före-snapshoten kunde inte tas — deltat är odömbart' }; break }
  if (!validHead(preSnap.head)) { contractStop = { round, rule: 'snapshot', detail: `före-snapshoten saknar giltig HEAD-hash — odömbart${preSnap.note ? ` (note: ${preSnap.note})` : ''}` }; break }
  // D1: route by category — seo findings to seo-optimizer (it can Edit meta/schema), the rest to stack-builder.
  // Sequential (not parallel) so two fixers never write the repo at once.
  const seoFixable = fixable.filter(f => f.category === 'seo')
  const buildFixable = fixable.filter(f => f.category !== 'seo')
  const fixReturns = []
  if (buildFixable.length) {
    const r = await agent(
      `Fix mode. Fix ONLY these verified launch-gate findings in the Nortropic site in the current working directory, minimally, then run pnpm build and confirm zero errors. Do NOT commit and do NOT stage anything — the release step commits a known set. Return per schema the complete list of repo-relative paths of every file you created, modified or deleted (including package.json and pnpm-lock.yaml if you install or upgrade anything) — report the list mechanically, do not filter or judge it.\n\n${JSON.stringify(buildFixable, null, 2)}`,
      { label: `fix:build:round${round}`, phase: 'Fix loop', agentType: 'stack-builder', schema: FILELIST }
    )
    fixReturns.push({ agent: 'stack-builder', result: r })
  }
  if (seoFixable.length) {
    const r = await agent(
      `Fix mode (SEO). Fix ONLY these verified SEO launch-gate findings (meta/titles/schema/NAP/sitemap) in the Nortropic site in the current working directory, minimally, then confirm the build. Do NOT commit and do NOT stage anything — the release step commits a known set. Return per schema the complete list of repo-relative paths of every file you created, modified or deleted — report the list mechanically, do not filter or judge it.\n\n${JSON.stringify(seoFixable, null, 2)}`,
      { label: `fix:seo:round${round}`, phase: 'Fix loop', agentType: 'seo-optimizer', schema: FILELIST }
    )
    fixReturns.push({ agent: 'seo-optimizer', result: r })
  }
  // BATCH-005: kontraktet prövas MEKANISKT (ren JS, aldrig agentprosa) innan något stageas.
  const dead = fixReturns.filter(x => !x.result)
  if (dead.length) { contractStop = { round, rule: 'felmod-4', detail: `${dead.map(x => x.agent).join(', ')} returnerade ingen fillista — blockerat; aldrig svepande staging (-A/-u) som fallback` }; break }
  const declared = [...new Set(fixReturns.flatMap(x => (x.result.files || []).map(normPath)))].filter(f => !CONTRACT_EXEMPT(f))
  const bad = badRepoPaths(declared)
  if (bad.length) { contractStop = { round, rule: 'felmod-3', detail: `sökväg utanför byggkatalogen/ogiltig: ${bad.join(', ')}` }; break }
  const postSnap = await agent(porcelainPrompt(`after fix round ${round}`, 'the Nortropic site in the current working directory'), { label: `snapshot:post:r${round}`, phase: 'Fix loop', schema: FILELIST })
  if (!postSnap) { contractStop = { round, rule: 'snapshot', detail: 'efter-snapshoten kunde inte tas — deltat är odömbart' }; break }
  if (!validHead(postSnap.head)) { contractStop = { round, rule: 'snapshot', detail: `efter-snapshoten saknar giltig HEAD-hash — odömbart${postSnap.note ? ` (note: ${postSnap.note})` : ''}` }; break }
  if (preSnap.head.trim() !== postSnap.head.trim()) { contractStop = { round, rule: 'head-flytt', detail: `HEAD flyttades under fixrundan (${preSnap.head.trim().slice(0, 8)} → ${postSnap.head.trim().slice(0, 8)}) — en agent committade själv; endast release-steget får committa` }; break }
  const preFiles = (preSnap.files || []).filter(f => !CONTRACT_EXEMPT(f))
  const postFiles = (postSnap.files || []).filter(f => !CONTRACT_EXEMPT(f))
  if (declared.length && !postFiles.length) { contractStop = { round, rule: 'snapshot', detail: 'deklarationen är icke-tom men efter-snapshoten tom — motsägelse, odömbart (aldrig tyst överhoppad commit)' }; break }
  const delta = fixDelta(preFiles, postFiles, declared)
  if (delta.foreign.length) { contractStop = { round, rule: 'felmod-2b', detail: `deklarerade filer var redan smutsiga FÖRE rundan (commit skulle smuggla in främmande ändringar): ${delta.foreign.join(', ')}` }; break }
  if (delta.undeclared.length) { contractStop = { round, rule: 'felmod-1', detail: `ändrade men EJ deklarerade filer: ${delta.undeclared.join(', ')} — partiell commit återinför rorjour-buggen för exakt dem` }; break }
  if (delta.cleanDeclared.length) log(`WARN (felmod 2a): deklarerade men aldrig ändrade — utesluts ur stageningen (endast delta-verifierade filer når git): ${delta.cleanDeclared.join(', ')}`)
  // Stagea SNITTET declared ∩ efter-snapshot: varje post är en verklig smutsig FIL ur porcelain —
  // kataloger, globs ('content/*.ts'), '.' och fantomsökvägar kan inte förekomma här.
  const postSet = new Set(postFiles.map(normPath))
  const stageSet = declared.filter(f => postSet.has(f))
  if (!stageSet.length) { log('Fixagenterna ändrade ingenting — inget att committa; kvarvarande fynd behöver människa.'); break }
  fixLog.push({ round, findings: fixable.length, files: stageSet, byAgent: fixReturns.map(x => ({ agent: x.agent, files: (x.result.files || []).map(normPath) })) })
  // Commit + redeploy BEFORE re-checking so URL-based gates (Lighthouse, curl-headers,
  // end-to-end lead, SSL) audit the FIXED build — not the stale origin/main preview.
  // rorjour: fixes sat uncommitted → the preview served pre-fix values → rounds were wasted
  // re-finding fixed issues. This step NEVER edits code: legal is still excluded from `fixable`,
  // the 3-round bound and D1 routing are unchanged. BATCH-005: stageningen är nu den delta-
  // verifierade KÄNDA mängden stageSet (NRT-003) — aldrig git add -A, aldrig git add -u.
  const pathArgs = stageSet.map(f => `"${f}"`).join(' ')
  const release = await agent(
    `Release step for the Nortropic site in the current working directory — do NOT change any code. (1) Stage EXACTLY this known set and nothing else by running exactly: git --literal-pathspecs add -- ${pathArgs} — then commit ONLY that same set by running exactly: git --literal-pathspecs commit -m "<descriptive message about the round-${round} launch-gate fixes>" -- ${pathArgs} — the pathspec'd commit is deliberate: it keeps any previously staged unrelated content OUT of this commit, and --literal-pathspecs is deliberate: paths like app/[stad]/page.tsx are literal file names, never glob patterns. NEVER stage sweepingly (no "-A", no "-u", no "git add ."), never add any path outside the list. If a git step fails: do NOT improvise and do NOT widen the staging — stop, report the error, and return PREVIEW_URL=none. (2) Redeploy a fresh preview of THIS commit (vercel deploy) and return the new preview URL on the final line as exactly PREVIEW_URL=<url>. If no deploy is possible, run pnpm build to prove the fixed tree compiles and return PREVIEW_URL=none.`,
    { label: `release:round${round}`, phase: 'Fix loop', agentType: 'stack-builder' }
  )
  if (!release) { contractStop = { round, rule: 'release', detail: 'release-steget returnerade ingenting — commit-utfallet är odömbart' }; break }
  const um = typeof release === 'string' ? release.match(/PREVIEW_URL=(\S+)/) : null
  if (um && um[1] && um[1] !== 'none') freshUrl = um[1]
  // BATCH-005: mekanisk EFTERKONTROLL av commit-utfallet — sista ledet vilar aldrig på prosa.
  // Detektion, inte prevention: committen finns när avvikelsen upptäcks, men rundan blockeras
  // FÖRE omkontrollen och människan får revert-underlaget i klartext.
  const commitSnap = await agent(
    `Mechanical commit inspection in the project root of the Nortropic site in the current working directory. Run exactly: git -c core.quotepath=off -c diff.renames=false show --name-only --format= HEAD — diff.renames=false is deliberate: a rename must list BOTH paths, matching the staged set. Return every path listed as BARE repo-relative paths (strip any surrounding double quotes). Also run exactly: git rev-parse HEAD — return the full 40-character hash as head. Do not filter or judge — report mechanically. If a command fails, return files: [] and say exactly why in note.`,
    { label: `commitset:r${round}`, phase: 'Fix loop', schema: FILELIST }
  )
  if (!commitSnap) { contractStop = { round, rule: 'release-efterkontroll', detail: 'commit-inspektionen kunde inte tas — utfallet är odömbart' }; break }
  if (!validHead(commitSnap.head)) { contractStop = { round, rule: 'release-efterkontroll', detail: `commit-inspektionen saknar giltig HEAD-hash — odömbart${commitSnap.note ? ` (note: ${commitSnap.note})` : ''}` }; break }
  if (commitSnap.head.trim() === postSnap.head.trim()) { contractStop = { round, rule: 'release-efterkontroll', detail: 'ny commit saknas — HEAD står kvar; release-stegets commit fallerade (ingenting att reverta, fixarna står ocommittade)' }; break }
  const committed = new Set((commitSnap.files || []).map(normPath))
  if (committed.size !== stageSet.length || !stageSet.every(f => committed.has(f))) {
    contractStop = { round, rule: 'release-efterkontroll', detail: `committad mängd ≠ stagead känd mängd (committat: ${[...committed].join(', ') || 'inget'}; förväntat: ${stageSet.join(', ')}) — committen finns redan; mänsklig granskning/revert krävs före ny körning` }
    break
  }
  const recheck = await parallel(failing.map(g => () =>
    agent(GATES.find(x => x.key === g.key).prompt + ` This is a RE-CHECK after fixes. The working-tree fixes are now COMMITTED and REDEPLOYED${freshUrl ? ` — run every check against this fresh preview: ${freshUrl}` : ''}. Verify the previously failing checks first; before reporting any issue, confirm it still reproduces on THIS build (not a cached/stale one).` + bypass, { label: `recheck:${g.key}:r${round}`, phase: 'Fix loop', agentType: g.agentType, schema: GATE })
  ))
  failing.forEach((g, i) => { if (recheck[i]) gates[g.key] = recheck[i] })
}
if (contractStop) log(`FIXKONTRAKT BRUTET (runda ${contractStop.round}, ${contractStop.rule}): ${contractStop.detail} — fixloopen avbröts före omkontrollen; kvarvarande fynd behöver människa.`)

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
  contractStop,
  handoverWritten: Boolean(handover),
}
