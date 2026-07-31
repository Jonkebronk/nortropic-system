#!/usr/bin/env node
// check-invariants.mjs — deterministisk invariantgrind (BATCH-002, hardnad BATCH-003)
// Ren Node, inga npm-beroenden, inga natanrop. Kors fran reporoten.
// Exit 0 om alla PASS, annars exit 1. En rad per overtradelse:
//   <INV-ID> <fil>:<rad> <kort orsak>
// Avslutas med: X PASS, Y FAIL, Z overtradelser.
// (INV-001/INV-003 anropar `git ls-files` via execFileSync — ingen shell, statiska
//  argument, inga natanrop; enda syftet ar git-tree-scoping per spec.)
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';

const CHECKS = ['INV-001', 'INV-002', 'INV-003', 'INV-004', 'INV-005'];
const violations = [];               // { id, line }
const invalid = new Set();           // checks som inte kunde bedomas -> FAIL, aldrig PASS
function flag(id, file, line, reason) { violations.push({ id, line: `${id} ${file}:${line} ${reason}` }); }

// filsystem-walk (INV-004) — scannar disken, per spec
function walk(dir, ok, out = []) {
  let ents; try { ents = readdirSync(dir); } catch { return out; }
  for (const e of ents) {
    const p = `${dir}/${e}`;
    let s; try { s = statSync(p); } catch { continue; }
    if (s.isDirectory()) walk(p, ok, out);
    else if (ok(e)) out.push(p);
  }
  return out;
}
const readLines = (f) => readFileSync(f, 'utf8').split('\n');
const trackedUnder = (...paths) => execFileSync('git', ['ls-files', '--', ...paths], { encoding: 'utf8' })
  .split('\n').map(s => s.trim()).filter(Boolean);

// ---- INV-001 (NRT-003): "git add -A" i GIT-SPARADE filer under workflows/ + skills/ ----
// Scope = git-tree, inte filsystemet (ospar tredjeparts hamnar utanfor automatiskt). ORORD BATCH-003.
try {
  const tracked = trackedUnder('workflows', 'skills');
  if (tracked.length === 0) invalid.add('INV-001');   // tomt = kunde-ej-bedoma, aldrig PASS
  for (const f of tracked) {
    readLines(f).forEach((l, i) => {
      if (l.includes('git add -A')) flag('INV-001', f, i + 1, 'git add -A i sparad pipeline-fil (NRT-003)');
    });
  }
} catch { invalid.add('INV-001'); }

// ---- INV-002 (NRT-004): agents/design-reviewer.md tools-rad far ej innehalla Bash ---- ORORD BATCH-003.
try {
  const f = 'agents/design-reviewer.md';
  const lines = readLines(f);
  const idx = lines.findIndex(l => l.startsWith('tools:'));
  if (idx < 0) invalid.add('INV-002');
  else if (/\bBash\b/.test(lines[idx])) flag('INV-002', f, idx + 1, 'design-reviewer tools innehaller Bash (NRT-004)');
} catch { invalid.add('INV-002'); }

// ---- INV-003 (NRT-013): query-formen "x-vercel-protection-bypass=" ----
// BATCH-003-hardning: scope breddat till GIT-SPARADE filer under workflows/ + skills/ + agents/
// (bypass-strangen kunde tidigare flyttas till en skill/agent och bli osynlig).
// UNDANTAR scripts/ och docs/ — och det ar en PRINCIP, inte en tillfallighet: en monstermatchande
// grind far ALDRIG scanna sin egen kallkod (scripts/) eller sin egen dokumentation (docs/).
// Grindens kalla innehaller nodvandigtvis den strang den soker efter, och programregistret
// beskriver regeln; scannas de flaggar grinden sig sjalv, blir permanent rod, och nagon "loser"
// det genom att ta bort kontrollen. Undantaget foljer av att scripts/ och docs/ inte ligger
// under de tre scannade paths. Header-formen (namn utan efterfoljande =) ar tillaten.
try {
  const tracked = trackedUnder('workflows', 'skills', 'agents');
  if (tracked.length === 0) invalid.add('INV-003');
  for (const f of tracked) {
    readLines(f).forEach((l, i) => {
      if (l.includes('x-vercel-protection-bypass=')) flag('INV-003', f, i + 1, 'query-form protection-bypass (NRT-013)');
    });
  }
} catch { invalid.add('INV-003'); }

// ---- INV-004 (NRT-007): agent med Bash/WebFetch/WebSearch/mcp__ maste bara ett IDENTISKT block ----
// BATCH-003-hardning: rubriken rackte inte — brodtexten kunde bytas ut och kontrollen forbli gron.
// Nu hashas HELA blocket (fran markorraden till nasta "## " eller filslut) och jamfors mot en
// hardkodad konstant. Blocket ar en SAKERHETSINVARIANT: en avsiktlig andring KRAVER att
// konstanten nedan uppdateras medvetet. Hashen ar LF-normaliserad → OS-oberoende, immun mot CRLF.
// KAND BEGRANSNING (medvetet vald, BATCH-003): kontrollen forutsatter IDENTISKA block over alla
// sju agenter. Per-agent-skarpning (t.ex. strangare klausul for project-planner, som ensam bar
// WebFetch + WebSearch + Write = bredare injektionsyta) kraver OMDESIGN — t.ex. hasha ett
// obligatoriskt karnstycke och tillata agentspecifik text efter det. Se programregistret.
const MARKER = '## EXTERN DATA ÄR INTE INSTRUKTIONER';
const BLOCK_SHA256 = '7ecd05e0289d81db454959a08c45db6be73300fec3ca8ca960b68e9737de6aca';
function blockHash(content) {
  const lines = content.replace(/\r\n/g, '\n').split('\n');
  const s = lines.findIndex(l => l === MARKER);
  if (s < 0) return null;
  let e = lines.length;
  for (let i = s + 1; i < lines.length; i++) if (lines[i].startsWith('## ')) { e = i; break; }
  const block = lines.slice(s, e).join('\n').replace(/\n+$/, '');   // markor -> nasta "## "/EOF, trimma efterfoljande tomrader
  return createHash('sha256').update(block, 'utf8').digest('hex');
}
try {
  const files = walk('agents', n => n.endsWith('.md'));
  if (files.length === 0) invalid.add('INV-004');
  for (const f of files) {
    const content = readFileSync(f, 'utf8');
    const lines = content.split('\n');
    const idx = lines.findIndex(l => l.startsWith('tools:'));
    const toolsLine = idx >= 0 ? lines[idx] : '';
    if (/\bBash\b|\bWebFetch\b|\bWebSearch\b|mcp__/.test(toolsLine)) {
      const h = blockHash(content);
      if (h === null) flag('INV-004', f, idx + 1, 'saknar markorblocket EXTERN DATA (NRT-007)');
      else if (h !== BLOCK_SHA256) flag('INV-004', f, idx + 1, `blockhash avviker (${h.slice(0, 12)}… != konstant ${BLOCK_SHA256.slice(0, 12)}…) (NRT-007)`);
    }
  }
} catch { invalid.add('INV-004'); }

// ---- INV-005 (NRT-009): doctor-checkantal verify-suite == steward. Las talen, hardkoda ej. ----
// BATCH-003-hardning: matcha SAMTLIGA forekomster av monstret, inte bara den forsta.
// Tidigare tog `break` forsta traffen (rad 6 = loggmetadata i meta.phases), inte den faktiska
// instruktionen till stewarden (rad 86). En fix av bara metadata-strangen hade da ljugit grinden
// gron. Nu flaggas EN overtradelse PER forekomst vars tal avviker fran stewardens — ingen enskild
// strang kan langre lura grinden. (INV-005 = deklarationskonsistens, EJ tackning — se register;
// far ej ensam bevisa att NRT-009 ar lost.)
try {
  // steward: hogsta "N. **" INOM "## MODE: doctor"-sektionen
  const st = readLines('agents/nortropic-steward.md');
  const start = st.findIndex(l => /^##\s+MODE:\s*doctor/i.test(l));
  let stN = null;
  if (start >= 0) {
    let end = st.length;
    for (let i = start + 1; i < st.length; i++) { if (/^##\s/.test(st[i])) { end = i; break; } }
    for (let i = start; i < end; i++) {
      const m = st[i].match(/^(\d+)\.\s+\*\*/);
      if (m) { const n = parseInt(m[1], 10); if (stN === null || n > stN) stN = n; }
    }
  }
  // verify-suite: SAMTLIGA forekomster (en-dash U+2013 el. hyphen — `-` sist i klassen = literal)
  const vs = readLines('workflows/nortropic-verify-suite.js');
  const hits = [];
  vs.forEach((l, i) => {
    const m = l.match(/(?:checks|kontroller)\s*1[–-](\d+)/i);
    if (m) hits.push({ line: i + 1, n: parseInt(m[1], 10) });
  });
  if (stN === null || hits.length === 0) invalid.add('INV-005');   // oparsbart/ingen forekomst -> INVALID, aldrig PASS
  else for (const h of hits) {
    if (h.n !== stN) flag('INV-005', 'workflows/nortropic-verify-suite.js', h.line,
      `doctor-checkantal: verify-suite=${h.n} != steward=${stN} (NRT-009)`);
  }
} catch { invalid.add('INV-005'); }

// ---- Rapport ----
for (const v of violations) console.log(v.line);
for (const id of CHECKS) if (invalid.has(id)) console.log(`${id} <ingen input>:0 KUNDE-EJ-BEDOMA (INVALID, raknas som FAIL)`);

const failed = new Set([...violations.map(v => v.id), ...invalid]);
const pass = CHECKS.filter(c => !failed.has(c)).length;
const fail = CHECKS.length - pass;
console.log(`\n${pass} PASS, ${fail} FAIL, ${violations.length} overtradelser`);
process.exit(fail === 0 ? 0 : 1);
