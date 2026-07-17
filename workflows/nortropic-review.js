export const meta = {
  name: 'nortropic-review',
  description: 'Parallel design + SEO + code review of a Nortropic site with adversarial verification of every finding',
  whenToUse: 'Run during the build phase of a Nortropic client site to get one consolidated, verified review report',
  phases: [
    { title: 'Review', detail: 'design-reviewer, seo-optimizer and a code reviewer in parallel' },
    { title: 'Verify', detail: 'two adversarial skeptics attempt to refute each finding' },
    { title: 'Report', detail: 'consolidated CRITICAL/HIGH/MEDIUM report' },
  ],
}

const FINDINGS = {
  type: 'object',
  required: ['findings'],
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['severity', 'title', 'location', 'why', 'fix'],
        properties: {
          severity: { type: 'string', enum: ['CRITICAL', 'HIGH', 'MEDIUM'] },
          title: { type: 'string' },
          location: { type: 'string', description: 'file:line or page@viewport' },
          why: { type: 'string', description: 'why this costs leads/trust/rank' },
          fix: { type: 'string', description: 'concrete fix' },
        },
      },
    },
  },
}

const VERDICT = {
  type: 'object',
  required: ['refuted', 'reason'],
  properties: {
    refuted: { type: 'boolean', description: 'true if the finding is wrong, already handled, or not worth fixing' },
    reason: { type: 'string' },
  },
}

const scope = (args && args.scope) || 'the Nortropic site in the current working directory'
// v5 calibration flag: /nortropic-review --no-verify skips the adversarial skeptic step so a run can be
// A/B-compared against a verified run (protocol: nortropic-retro/references/verify-kalibrering.md).
// Defensive read — the flag may arrive as noVerify or 'no-verify' depending on how args are populated.
const noVerify = !!(args && (args.noVerify || args['no-verify']))

const REVIEWERS = [
  {
    key: 'design',
    agentType: 'design-reviewer',
    prompt: `Review ${scope}. Run your full anti-slop design review process (score, conversion-critical checks, viewport pass if a dev/preview URL is reachable). Return your findings as structured data only — severity CRITICAL for anything that blocks conversion (phone/CTA/form problems), HIGH for trust erosion, MEDIUM for polish.`,
  },
  {
    key: 'seo',
    agentType: 'seo-optimizer',
    prompt: `Audit ${scope} in audit mode. Check meta templates, H1s, schema validity, NAP consistency against content/business.ts, internal linking, thin area pages, sitemap/robots. Return findings as structured data only — severity CRITICAL for NAP divergence, missing/broken schema on money pages, or noindex accidents; HIGH for template violations; MEDIUM for improvements.`,
  },
  {
    key: 'code',
    agentType: null,
    prompt: `You are a strict code-correctness reviewer. Review ${scope} (a Next.js 15 App Router + TypeScript strict + Tailwind 4 site) for real bugs only: broken imports, server/client component violations, unvalidated form input reaching the lead server action, missing error handling in app/actions/lead.ts, hydration hazards, misconfigured generateStaticParams/metadata, accessibility violations in interactive components. No style opinions — bugs and correctness only. Return findings as structured data.`,
  },
]

phase('Review')
const results = await pipeline(
  REVIEWERS,
  r => {
    const opts = { label: `review:${r.key}`, phase: 'Review', schema: FINDINGS }
    if (r.agentType) opts.agentType = r.agentType
    return agent(r.prompt, opts)
  },
  (review, r) => {
    const found = (review && review.findings) || []
    if (!found.length) return []
    if (noVerify) {
      log(`${r.key}: ${found.length} findings — verify SKIPPED (calibration run)`)
      return found.map(f => ({ ...f, source: r.key, verdict: 'UNVERIFIED' }))
    }
    log(`${r.key}: ${found.length} findings — verifying`)
    return parallel(found.map(f => () =>
      parallel([0, 1].map(i => () =>
        agent(
          `You are an adversarial verifier with a distinct lens (${i === 0 ? 'is this factually true in the code? Read the actual files at the stated location' : 'does this actually matter for a Swedish local-service lead-gen site, or is it pedantry/already mitigated elsewhere?'}). Try to REFUTE this ${r.key} review finding about ${scope}:\n\nTitle: ${f.title}\nLocation: ${f.location}\nClaim: ${f.why}\nProposed fix: ${f.fix}\n\nInvestigate the code yourself. Default to refuted=true if you cannot confirm it.`,
          { label: `verify:${f.title.slice(0, 40)}`, phase: 'Verify', schema: VERDICT }
        )
      )).then(votes => {
        const refutations = votes.filter(Boolean).filter(v => v.refuted)
        return { ...f, source: r.key, refutedBy: refutations.length, verdict: refutations.length === 0 ? 'CONFIRMED' : refutations.length === 1 ? 'PLAUSIBLE' : 'DROPPED', refuteReasons: refutations.map(v => v.reason) }
      })
    ))
  }
)

const all = results.filter(Boolean).flat().filter(Boolean)
const kept = all.filter(f => f.verdict !== 'DROPPED')
const dropped = all.filter(f => f.verdict === 'DROPPED')
log(noVerify
  ? `Calibration run: ${kept.length} findings, UNVERIFIED (skeptic step skipped)`
  : `Verified: ${kept.length} kept (${kept.filter(f => f.verdict === 'CONFIRMED').length} confirmed), ${dropped.length} dropped`)

phase('Report')
const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2 }
kept.sort((a, b) => (order[a.severity] ?? 3) - (order[b.severity] ?? 3))

const reviewHeader = noVerify
  ? 'START THE REPORT WITH A BOLD BANNER LINE: "⚠️ OVERIFIERAD KÖRNING — endast för kalibrering". The findings below were NOT adversarially verified (the skeptic step was skipped); treat every finding as UNVERIFIED, say so explicitly, and do not present any as CONFIRMED.'
  : 'Findings below are already adversarially verified (CONFIRMED = both skeptics failed to refute; PLAUSIBLE = one skeptic doubted it, note that).'
const report = await agent(
  `Write a consolidated Nortropic review report in markdown for ${scope}. ${reviewHeader} Group by severity CRITICAL/HIGH/MEDIUM, keep each finding to location + one-line problem + one-line fix + which agent fixes it (technical/code → stack-builder, copy → content-designer, SEO → seo-optimizer, design → stack-builder with design guidance). End with a 3-line summary and the recommended fix order. Do not invent findings beyond this list:\n\n${JSON.stringify(kept, null, 2)}\n\nDropped by verification (mention only the count): ${dropped.length}`,
  { label: 'report', phase: 'Report' }
)

return { report, mode: noVerify ? 'calibration-unverified' : 'verified', counts: { kept: kept.length, confirmed: kept.filter(f => f.verdict === 'CONFIRMED').length, dropped: dropped.length } }
