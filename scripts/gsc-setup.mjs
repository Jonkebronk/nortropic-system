// scripts/gsc-setup.mjs — GSC META-verifiering (datafundament förslag 09)
//
// Ändrar GSC-verifieringen från manuell prosa (gsc-launch-steps.md) till en
// körning: META-taggen är en fil i ett repo du äger, till skillnad från DNS TXT
// som kräver kundens registrar (Oderland). Anropas fristående via CLI eller ur
// nortropic-cutover-workflowet (nod 10, förslag 10), fas 3.
//
// VAKTARNA FÖRST. TESTKLIENT, .vercel.app och den kanoniska kontrollen körs
// före varje skarp handling och kräver VARKEN googleapis ELLER en nyckel.
// Därför är googleapis en LAT dynamisk import (inte top-level som i utkastet i
// datafundament-addendum §6.3): en saknad GOOGLE_APPLICATION_CREDENTIALS kan
// aldrig hinna kasta ett auth-fel före TESTKLIENT-vakten, och scripts/ slipper
// ett package.json i whitelisten. Vaktarna blir körbara och bevisbara utan
// credentials — det som kodinspektion inte kan ge.
//
// Setup en gång: se datafundament-addendum §6.1 (Google Cloud-projekt, service-
// konto, `npm i googleapis`, GOOGLE_APPLICATION_CREDENTIALS/GSC_HUMAN_OWNER/
// GSC_CLIENT_OWNER). En nyckel räcker för alla kunddomäner för alltid.

import { promises as fs } from 'node:fs';
import { pathToFileURL } from 'node:url';

const SCOPES = [
  'https://www.googleapis.com/auth/siteverification',
  'https://www.googleapis.com/auth/webmasters',
];

// Förväntad "inte redo än"-orsak: sajten/taggen/sitemap är inte live. ENDAST
// dessa får --skip-if-not-ready svälja. TESTKLIENT, .vercel.app, kanonisk drift
// och auth-fel är riktiga fel och ska fela hårt även i deploy-kontext.
class NotReadyError extends Error {}

// Kanonisk variant — måste matcha sajtens redirect.
// www och apex är SKILDA properties vid URL-prefix.
const siteUrlFor = (domain) => `https://${domain}/`;

// Lat: googleapis + auth byggs först NÄR ett API-anrop ska göras — efter vaktarna.
async function gscClients() {
  const { google } = await import('googleapis');
  const auth = new google.auth.GoogleAuth({
    keyFile: process.env.GOOGLE_APPLICATION_CREDENTIALS,
    scopes: SCOPES,
  });
  return {
    verification: google.siteVerification({ version: 'v1', auth }),
    searchconsole: google.searchconsole({ version: 'v1', auth }),
  };
}

/**
 * Läser klientrepots business.ts (src/content/ i faktiska byggen, content/ i
 * äldre kontraktprosa), bekräftar att det ÄR domänens repo, och plockar
 * testklient-flaggan. Skrivs en token i FEL repo hamnar en kunds
 * verifieringstoken i en annans sajt — och verifieringen misslyckas sedan tyst
 * för båda. Kastar hellre än skriver blint.
 */
export async function readClientRepo(clientRepoPath, domain) {
  const candidates = [
    `${clientRepoPath}/src/content/business.ts`,
    `${clientRepoPath}/content/business.ts`,
  ];
  let text, businessFile;
  for (const c of candidates) {
    try { text = await fs.readFile(c, 'utf8'); businessFile = c; break; } catch { /* prova nästa */ }
  }
  if (!text) {
    throw new Error(`Hittar ingen business.ts under ${clientRepoPath} (src/content/ eller content/) — fel repo, eller inget Nortropic-bygge. Skriver ingenting.`);
  }

  const dm = text.match(/domain:\s*["']([^"']+)["']/);
  if (!dm) {
    throw new Error(`${businessFile} saknar ett domain-fält — kan inte bekräfta att detta är ${domain}:s repo. Skriver ingenting.`);
  }
  const norm = (d) => d.replace(/^www\./, '').toLowerCase();   // www/apex = samma repo, olika GSC-property
  if (norm(dm[1]) !== norm(domain)) {
    throw new Error(`Fel repo: business.ts har domain "${dm[1]}" men du verifierar ${domain}. En kunds token i en annans sajt misslyckas tyst för båda. Skriver ingenting.`);
  }

  const testklient = /testklient:\s*true/.test(text);
  const contentDir = businessFile.replace(/business\.ts$/, '');  // verification.ts läggs bredvid business.ts
  return { contentDir, testklient };
}

// ---------- STEG 1: token ----------

export async function getMetaToken(domain, { testklient = false } = {}) {
  if (testklient) throw new Error('TESTKLIENT — GSC-uppsättning körs inte skarpt');

  if (domain.endsWith('.vercel.app')) {
    throw new Error(`${domain} är en Vercel-subdomän — koppla kundens riktiga domän först`);
  }

  const { verification } = await gscClients();
  const { data } = await verification.webResource.getToken({
    requestBody: {
      site: { type: 'SITE', identifier: siteUrlFor(domain) },
      verificationMethod: 'META',
    },
  });

  // data.token är hela taggen:
  // <meta name="google-site-verification" content="..." />
  return data.token;
}

/** Skriver token till klientrepots verification.ts (bredvid business.ts). */
export async function writeMetaToken(token, contentDir) {
  const file = `${contentDir}verification.ts`;
  const content = data => `// Genererad av gsc-setup.mjs — ta ALDRIG bort.
// Försvinner taggen tappas GSC-verifieringen och datan slutar komma in, tyst.
export const googleSiteVerification = ${JSON.stringify(data)};
`;
  const match = token.match(/content=["']([^"']+)["']/);
  if (!match) throw new Error(`Kunde inte tolka token: ${token}`);
  await fs.writeFile(file, content(match[1]), 'utf8');
  console.log(`Skrev ${file}`);
  console.log('Rendera i layout: <meta name="google-site-verification" content={googleSiteVerification} />');
  return match[1];
}

// ---------- STEG 2: verifiera ----------

// Exporterad (utkastet hade den privat) så den kanoniska kontrollen går att
// köra fristående UTAN någon GSC-skrivning — det är exakt test C:s yta.
// Kastar vanlig Error för kanonisk drift (hårt fel — fel variant/delade
// properties, inte ett tidsproblem).
//
// TVÅ RIKTNINGAR (C-fyndet): `landed.hostname !== domain` fångar bara "redirect
// BORT". Den är false BÅDE när allt är rätt OCH när inget är konfigurerat (båda
// varianterna svarar 200 utan redirect) — två tillstånd som ser identiska ut.
// Därför kontrolleras även den MOTSATTA varianten: den ska 301:a till den
// kanoniska. Svarar båda 200 är det ett fynd, inte ett grönt.
export async function assertCanonical(domain) {
  // 1. Den angivna domänen får inte redirecta BORT från sig själv.
  const res = await fetch(siteUrlFor(domain), { redirect: 'follow' });
  if (!res.ok) throw new NotReadyError(`https://${domain} svarar ${res.status}`);
  const landed = new URL(res.url);
  if (landed.hostname !== domain) {
    throw new Error(
      `${domain} redirectar till ${landed.hostname}. ` +
      `Verifiera den kanoniska varianten i stället — www och apex är skilda properties.`
    );
  }

  // 2. Den MOTSATTA varianten (www↔apex) måste 301:a HIT. Följ den och se var
  //    den landar — undici kan inte inspektera en redirect:'manual'-respons
  //    (opaque, status 0), så vi läser slutdestinationen i stället.
  const other = domain.startsWith('www.') ? domain.slice(4) : `www.${domain}`;
  let otherRes;
  try {
    otherRes = await fetch(siteUrlFor(other), { redirect: 'follow' });
  } catch {
    return res;   // motsatta varianten svarar inte alls → ingen konkurrerande host, OK
  }
  const otherLanded = new URL(otherRes.url);
  if (otherLanded.hostname === domain) return res;             // bra: other 301:ar till kanonisk
  if (otherLanded.hostname === other) {
    if (otherRes.ok) {                                          // other serverar sig själv, 2xx
      throw new Error(
        `Både ${domain} och ${other} svarar ${otherRes.status} utan att ${other} 301:ar till ${domain} — ` +
        `delade GSC-properties + dubblettinnehåll indexerat på två värdar. Sätt upp 301:en före verifiering.`
      );
    }
    return res;                                                // other 4xx/5xx på sig själv → ingen konkurrent, OK
  }
  // other landar någon HELT annanstans → fel kanonisk riktning
  throw new Error(`${other} landar på ${otherLanded.hostname}, inte ${domain} — fel kanonisk riktning.`);
}

// Kastar NotReadyError för "inte redo än"-orsaker (soft-skip-bara).
export async function assertTagIsLive(domain, expected) {
  const res = await assertCanonical(domain);   // full kanonisk kontroll + återanvänder svaret (ingen dubbelfetch)
  const html = await res.text();
  if (!html.includes(expected)) {
    throw new NotReadyError('META-taggen syns inte i produktions-HTML — deploya först');
  }

  const sm = await fetch(`https://${domain}/sitemap.xml`, { redirect: 'follow' });
  if (!sm.ok) throw new NotReadyError(`sitemap.xml svarar ${sm.status}`);
}

export async function verifyAndRegister(domain, expectedToken, { testklient = false } = {}) {
  if (testklient) throw new Error('TESTKLIENT — GSC-uppsättning körs inte skarpt');

  await assertTagIsLive(domain, expectedToken);
  console.log('Taggen är live, sitemap svarar');

  const { verification, searchconsole } = await gscClients();
  const site = { type: 'SITE', identifier: siteUrlFor(domain) };

  const { data: resource } = await verification.webResource.insert({
    verificationMethod: 'META',
    requestBody: { site },
  });
  console.log(`Verifierad: ${resource.id}`);

  // Ägarskap: kunden äger sin tillgång (gsc-launch-steps.md), du får åtkomst,
  // service-kontot behåller API-åtkomst tills offboarding.
  const owners = new Set(resource.owners || []);
  const toAdd = [process.env.GSC_HUMAN_OWNER, process.env.GSC_CLIENT_OWNER]
    .filter(Boolean)
    .filter((o) => !owners.has(o));

  if (!process.env.GSC_CLIENT_OWNER) {
    console.warn('⚠️  GSC_CLIENT_OWNER inte satt — kunden äger inte sin property än. Lägg till så snart adressen är känd.');
  }

  if (toAdd.length) {
    await verification.webResource.update({
      id: resource.id,
      requestBody: { site: resource.site, owners: [...owners, ...toAdd] },
    });
    console.log(`Ägare tillagda: ${toAdd.join(', ')}`);
  }

  const siteUrl = siteUrlFor(domain);
  await searchconsole.sites.add({ siteUrl });
  await searchconsole.sitemaps.submit({
    siteUrl,
    feedpath: `https://${domain}/sitemap.xml`,
  });

  console.log(`\nKLART: ${siteUrl} — data börjar samlas inom några dagar.\n`);
  return { siteUrl };
}

// ---------- CLI ----------
// pathToFileURL i stället för `file://${process.argv[1]}`: den senare matchar
// aldrig import.meta.url på Windows (drivbokstav + omvända snedstreck), så CLI-
// blocket skulle tyst aldrig köra. pathToFileURL normaliserar båda plattformarna.
if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [cmd, domain, repoPath] = process.argv.slice(2);
  const soft = process.argv.includes('--skip-if-not-ready');

  const run = async () => {
    if (cmd === 'token') {
      if (!domain || !repoPath) throw new Error('Användning: gsc-setup.mjs token domän.se ./klientrepo');
      // Bekräfta rätt repo + läs testklient FÖRE getMetaToken, så TESTKLIENT-
      // vakten avbryter token/filskrivningen (addendum §5.4: alla fyra) före API.
      const { contentDir, testklient } = await readClientRepo(repoPath, domain);
      const token = await getMetaToken(domain, { testklient });
      await writeMetaToken(token, contentDir);
      console.log('\nDeploya, kör sedan: gsc-setup.mjs verify ' + domain);
    } else if (cmd === 'verify') {
      if (!domain) throw new Error('Användning: gsc-setup.mjs verify domän.se');
      // MEDVETET VAL: verify hämtar tokenet igen via API (getToken är idempotent
      // för samma sajt+konto, addendum §6.10) i stället för att läsa det ur
      // verification.ts. verify KRÄVER ändå auth för insert/sites.add/submit, så
      // återhämtningen adderar inget nytt auth-krav; och Google blir källan till
      // sanning för "vilken tag ska ligga live". Alternativet (läs ur filen) är
      // robustare mot stale API men kräver repopath och litar på en deploy-artefakt.
      const token = await getMetaToken(domain);
      const match = token.match(/content=["']([^"']+)["']/);
      await verifyAndRegister(domain, match[1]);
    } else {
      throw new Error('Användning: gsc-setup.mjs [token|verify] domän.se [repopath]');
    }
  };

  // --skip-if-not-ready sväljer ENDAST förväntade "inte redo än"-orsaker.
  // TESTKLIENT, .vercel.app, kanonisk drift och auth-fel felar hårt (exit 1)
  // så ett saknat credentials aldrig loggas som "hoppar över" och exit 0.
  try {
    await run();
  } catch (e) {
    if (soft && e instanceof NotReadyError) {
      console.log(`Hoppar över (inte redo): ${e.message}`);
      process.exit(0);
    }
    console.error(`\nFEL: ${e.message}\n`);
    process.exit(1);
  }
}
