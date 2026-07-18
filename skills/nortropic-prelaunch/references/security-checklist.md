# Gate 7 — Säkerhet: kontroller & kanoniska fixar

Statisk Next.js-sajt utan databas: attackytan är liten men verklig — beroenden, headers, formulär-endpointen (den ENDA servern) och läckta hemligheter. Alla fixar nedan respekterar static-first: **ingen Redis/Upstash/DB får introduceras för rate limiting.**

## 1. Beroenden

```bash
npm audit --omit=dev        # (pnpm: pnpm audit --prod)
```
- **FAIL**: någon high/critical i produktionsberoenden.
- **Fix**: uppgradera paketet; går inte det, byt paket. `npm audit fix` är OK **endast** om lockfile-diffen granskas innan commit (auto-fix kan bumpa majors).
- Dev-beroenden (eslint, prettier m.fl.) rapporteras som NOTE, inte FAIL — de når aldrig produktion.

## 2. Säkerhetsheaders

**Verifiera vad som FAKTISKT servas** — inte vad configen säger:
```bash
curl -sI https://<preview-url>/ | grep -iE 'content-security|strict-transport|x-content-type|referrer-policy|x-frame|frame-ancestors'
```
Saknas preview-URL (lokal granskning): bedöm mot `headers()` i `next.config.ts` istället, markera header-fynden "UNVERIFIED — verifiera med curl vid första preview-deploy". HSTS kan aldrig bedömas från config (Vercel kan serva den ändå) — alltid UNVERIFIED tills curl körts.

Krav:
| Header | Värde |
|---|---|
| `Content-Security-Policy` | baslinjen nedan (self + ev. bildhost) |
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains` — **Vercel servar ofta denna redan**: kolla curl-utdata FÖRST, lägg bara till om den saknas (undvik dubbla headers) |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `frame-ancestors 'none'` i CSP | (eller `X-Frame-Options: DENY` som fallback för äldre klienter — båda är OK) |

**Kanonisk fix — `headers()` i `next.config.ts`** (inte `vercel.json` när next.config redan äger konfigurationen). Copy-paste-facit:

```ts
const securityHeaders = [
  {
    key: "Content-Security-Policy",
    value: [
      "default-src 'self'",
      // 'unsafe-inline' krävs av Nexts inline-bootstrap på statiska sidor
      // (nonces kräver dynamisk rendering — bryter static-first).
      "script-src 'self' 'unsafe-inline'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data:",            // + klientens bildhost om extern
      "font-src 'self'",                  // next/font är self-hosted
      "connect-src 'self'",               // Vercel Analytics postar same-origin (/_vercel/insights)
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      // Kontakt-sidans kart-embed? Lägg till: "frame-src https://www.google.com"
    ].join("; "),
  },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "X-Frame-Options", value: "DENY" },
  // Strict-Transport-Security: lägg till ENDAST om curl visar att Vercel inte redan servar den:
  // { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains" },
];

const nextConfig: NextConfig = {
  async headers() {
    return [{ source: "/(.*)", headers: securityHeaders }];
  },
};
```

Efter fixen: kör `curl -sI` igen mot en ny preview-deploy och verifiera att varje header servas. En CSP som blockerar Analytics eller kartan syns direkt i konsolen — testa Hem + Kontakt i webbläsaren efter deploy.

**Analytics-loadern får inte CSP-blockeras (bekräftad regress — rorjour Gate 1).** Stacken kör Vercel Analytics som standard. `connect-src 'self'` täcker BARA beacon-POSTen till `/_vercel/insights/event` — INTE själva loader-scriptet. Om loadern hämtas cross-origin (t.ex. `https://va.vercel-scripts.com/...`) blockeras den av `script-src 'self'`: `track()` köar `phone_click`/`quote_submit` i `window.vaq` men INGEN beacon skickas (konsolen: "Failed to load script") → konverteringsspårningen är tyst död, fast alla headers ser rena ut i curl. **Verifiera efter deploy:** öppna konsolen på en skarp preview, klicka en `tel:`-länk eller skicka formuläret, och bekräfta en POST till `/_vercel/insights/event` (inte bara att `window.vaq` växer). Blockeras loadern → lägg dess exakta host i `script-src` och verifiera om. Detta är samma gate-krock som kart-embedden (Gate 6 juridik ⟷ Gate 7 CSP): en säkerhets-CSP får aldrig tyst slå ut en konverterings- eller leadfunktion — härda OCH verifiera att default-analytics fortfarande skickar.

## 3. Formulärmissbruk (offert-endpointen — sajtens enda server)

| Kontroll | Krav | Kanonisk fix |
|---|---|---|
| (a) Honeypot | Bottar som fyller i fältet får **tyst 200 utan mejl** — boten lär sig inget | Dolt fält (t.ex. `foretag`); ifyllt → `return { ok: true }` utan Resend-anrop |
| (b) Tidsfälla | En orimligt snabb submit efter sidladdning avvisas tyst. **Förfluten tid MÄTS PÅ EN ENDA KLOCKA** (klientens: mount → submit) och skickas som en varaktighet i ms — ALDRIG en rå `startedAt`-tidsstämpel som servern jämför mot sin egen `Date.now()`. Klockskillnad klient/server tappar då riktiga leads tyst (= H1). Saknat/0-värde (direkt-POST förbi formuläret) är INTE ett fynd — fältet är ett bot-filter, inte autentisering, och ska fail-open. | Klienten sätter `mountTime = Date.now()` vid mount och submittar `Date.now() - mountTime` som `elapsedMs`. Servern: `if (elapsedMs > 0 && elapsedMs < 1500) return { ok: true }` (tyst). Tröskeln hålls låg (1,5 s) så att webbläsar-/keychain-autofyll hos en återkommande besökare inte felklassas. **Jämför aldrig en klientstämpel mot serverns `Date.now()`.** |
| (c) Validering | ALLA fält valideras server-side: längdtak, e-postformat, enum för tjänst | Zod-schema i server action — max-längder på varje strängfält (namn ≤100, meddelande ≤3000), `z.email()`, `z.enum(tjänster)` |
| (d) Fast mottagare | Mottagaradressen hårdkodas från env (`LEAD_TO_EMAIL`), fallback `business.email` — **läses ALDRIG ur request body** | `const to = process.env.LEAD_TO_EMAIL ?? business.email` — annars är endpointen ett öppet spam-relay. CRITICAL om brutet |
| (e) Generiska fel | Klienten får bara generiska felkoder (`"validering"`/`"sandning"`) — inga env-namn, stackar eller Resend-svar | Diagnostik till `console.error` (serverlogg); klient-state bär aldrig råa fel |

**Rate limiting**: plattformsnivå (Vercel WAF / bot challenge) noteras som **tillval** i rapporten — aldrig en egen DB-baserad limiter (bryter static-first, ingen databas).

Referensimplementation: `rorjour-stockholm/src/app/actions/lead.ts` uppfyller (a)–(e).

## 4. Hemligheter

```bash
grep -r "re_" .next/static/          # Resend-nyckelprefix i klientbundeln = CRITICAL
grep -rE "RESEND_API_KEY|LEAD_TO_EMAIL" src/ | grep -v "use server"   # env-namn utanför serverkod?
git log --all --diff-filter=A --name-only -- ".env*"   # .env-filer i historiken?
```
- `.env*` ska stå i `.gitignore` OCH aldrig ha committats (kolla historiken, inte bara nuläget — en nyckel i historiken är läckt även om filen tagits bort).
- Alla API-nycklar endast i server-kod (`"use server"`-filer / route handlers). Ett env-varnamn i en klientkomponent är en varning; ett nyckel-VÄRDE var som helst i repo/bundle är CRITICAL → rotera nyckeln omedelbart.

## Severity-mappning
- **CRITICAL**: mottagare ur request body · nyckelvärde i bundle/repo/historik · high/critical prod-CVE med känd exploit · CSP saknas helt på en skarp klient
- **HIGH**: enskild säkerhetsheader saknas · honeypot/tidsfälla saknas · fältvalidering utan längdtak
- **MEDIUM**: HSTS-duplikat · dev-beroende-CVE:er · WAF-tillvalet inte aktiverat
