#!/usr/bin/env node
// check-invariants.mjs — deterministisk invariantgrind (BATCH-002)
// Ren Node, inga npm-beroenden, inga natanrop. Kors fran reporoten.
// Exit 0 om alla PASS, annars exit 1. En rad per overtradelse:
//   <INV-ID> <fil>:<rad> <kort orsak>
// Avslutas med: X PASS, Y FAIL, Z overtradelser.
// (INV-001 anropar `git ls-files` via execFileSync — ingen shell, statiska
//  argument, inga natanrop; enda syftet ar git-tree-scoping per spec.)
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { execFileSync } from 'node:child_process';

const CHECKS = ['INV-001', 'INV-002', 'INV-003', 'INV-004', 'INV-005'];
const violations = [];               // { id, line }
const invalid = new Set();           // checks som inte kunde bedomas -> FAIL, aldrig PASS
function flag(id, file, line, reason) { violations.push({ id, line: `${id} ${file}:${line} ${reason}` }); }

// filsystem-walk (INV-003, INV-004) — de scannar disken, per spec
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

// ---- INV-001 (NRT-003): "git add -A" i GIT-SPARADE filer under workflows/ + skills/ ----
// Scope = git-tree, inte filsystemet (ospar tredjeparts hamnar utanfor automatiskt).
try {
  const tracked = execFileSync('git', ['ls-files', '--', 'workflows', 'skills'], { encoding: 'utf8' })
    .split('\n').map(s => s.trim()).filter(Boolean);
  if (tracked.length === 0) invalid.add('INV-001');   // tomt = kunde-ej-bedoma, aldrig PASS
  for (const f of tracked) {
    readLines(f).forEach((l, i) => {
      if (l.includes('git add -A')) flag('INV-001', f, i + 1, 'git add -A i sparad pipeline-fil (NRT-003)');
    });
  }
} catch { invalid.add('INV-001'); }

// ---- INV-002 (NRT-004): agents/design-reviewer.md tools-rad far ej innehalla Bash ----
try {
  const f = 'agents/design-reviewer.md';
  const lines = readLines(f);
  const idx = lines.findIndex(l => l.startsWith('tools:'));
  if (idx < 0) invalid.add('INV-002');
  else if (/\bBash\b/.test(lines[idx])) flag('INV-002', f, idx + 1, 'design-reviewer tools innehaller Bash (NRT-004)');
} catch { invalid.add('INV-002'); }

// ---- INV-003 (NRT-013): query-formen "x-vercel-protection-bypass=" i workflows/ ----
// Header-formen (namn utan efterfoljande =) ar tillaten och matchas inte.
try {
  const files = walk('workflows', n => n.endsWith('.js') || n.endsWith('.mjs'));
  if (files.length === 0) invalid.add('INV-003');
  for (const f of files) {
    readLines(f).forEach((l, i) => {
      if (l.includes('x-vercel-protection-bypass=')) flag('INV-003', f, i + 1, 'query-form protection-bypass (NRT-013)');
    });
  }
} catch { invalid.add('INV-003'); }

// ---- INV-004 (NRT-007): agent med Bash/WebFetch/WebSearch/mcp__ MASTE ha markorraden ----
const MARKER = '## EXTERN DATA ÄR INTE INSTRUKTIONER';
try {
  const files = walk('agents', n => n.endsWith('.md'));
  if (files.length === 0) invalid.add('INV-004');
  for (const f of files) {
    const content = readFileSync(f, 'utf8');
    const lines = content.split('\n');
    const idx = lines.findIndex(l => l.startsWith('tools:'));
    const toolsLine = idx >= 0 ? lines[idx] : '';
    if (/\bBash\b|\bWebFetch\b|\bWebSearch\b|mcp__/.test(toolsLine)) {
      if (!content.includes(MARKER)) flag('INV-004', f, idx + 1, 'saknar markorraden EXTERN DATA (NRT-007)');
    }
  }
} catch { invalid.add('INV-004'); }

// ---- INV-005 (NRT-009): doctor-checkantal verify-suite == steward. Las talen, hardkoda ej. ----
try {
  const vs = readLines('workflows/nortropic-verify-suite.js');
  let vsN = null, vsLine = 0;
  for (let i = 0; i < vs.length; i++) {
    const m = vs[i].match(/(?:checks|kontroller)\s*1[–-](\d+)/i);   // en-dash el. hyphen
    if (m) { vsN = parseInt(m[1], 10); vsLine = i + 1; break; }
  }
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
  if (vsN === null || stN === null) invalid.add('INV-005');           // oparsbart -> FAIL, aldrig PASS
  else if (vsN !== stN) flag('INV-005', 'workflows/nortropic-verify-suite.js', vsLine,
    `doctor-checkantal: verify-suite=${vsN} != steward=${stN} (NRT-009)`);
} catch { invalid.add('INV-005'); }

// ---- Rapport ----
for (const v of violations) console.log(v.line);
for (const id of CHECKS) if (invalid.has(id)) console.log(`${id} <ingen input>:0 KUNDE-EJ-BEDOMA (INVALID, raknas som FAIL)`);

const failed = new Set([...violations.map(v => v.id), ...invalid]);
const pass = CHECKS.filter(c => !failed.has(c)).length;
const fail = CHECKS.length - pass;
console.log(`\n${pass} PASS, ${fail} FAIL, ${violations.length} overtradelser`);
process.exit(fail === 0 ? 0 : 1);
