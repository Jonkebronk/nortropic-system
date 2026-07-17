# Swedish/EU Legal Requirements — Full Reference

**PROCESS RULE: legal findings are reported, never auto-fixed.** The pipeline stops and a human (the Nortropic owner, if needed with the client's lawyer) decides. Nothing below is legal advice — it is the checklist of what to verify.

## 1. Integritetspolicy (GDPR — required on every site)
The quote form collects personal data (namn, telefon, e-post) → the site MUST have a Swedish privacy policy page (`/integritetspolicy`) covering:
- **Personuppgiftsansvarig**: company name, org.nr, address, e-post
- **What is collected**: form fields, and any analytics identifiers
- **Purpose + legal basis**: answering quote requests (avtal/berättigat intresse); analytics (samtycke if cookie-based, berättigat intresse if cookieless — state which)
- **Recipients/processors**: Resend (e-post), Vercel (hosting/analytics), Google (Maps/GA4 if used) — name them
- **Retention**: how long lead emails are kept (client decides; write the actual practice)
- **Rights**: tillgång, rättelse, radering, invändning, dataportabilitet; right to complain to **IMY** (Integritetsskyddsmyndigheten, imy.se)
- Third-country transfers if any US processors — mention SCC/DPF status

## 2. Cookies & consent (ePrivacy / LEK)
- **Nortropic default (Vercel Analytics only)**: cookieless — **no consent banner needed**. Policy still describes analytics. This is a selling point; don't add a banner "just in case", it costs conversions.
- **If GA4/Meta pixel/YouTube embeds**: opt-in consent BEFORE any non-necessary cookie is set (PTS/IMY practice). GA4 requires **Consent Mode v2** with default denied. Banner: neka = lika lätt som acceptera, no pre-ticked boxes, no cookie walls.
- Google Maps iframe can set cookies → either consent-gate the embed (facade: static image until click) or verify current embed behavior and cover it in the policy.

## 3. Företagsuppgifter (e-handelslagen / marknadsföringslagen)
Footer (or easily reachable page) must show: **company name, org.nr, geographic address, contact (phone/e-post)**. F-skatt statement customary for trades. If VAT-relevant to consumers: prices **inkl. moms**.

## 4. Marketing claims (marknadsföringslagen)
- "Auktoriserad" / "certifierad" → must be backed by real registration (el: Elsäkerhetsverkets register; VVS: Säker Vatten; etc.). Verify or remove.
- Displayed betyg/omdömen must be real and current; review selection must not mislead (Omnibus direktivet: state whether reviews are verified)
- "Jour dygnet runt" → phone actually staffed 24/7, or reword ("Jour kvällar & helger")
- ROT/RUT price examples must be correct for the service type (ROT 30%, RUT 50%, current caps) and labeled "efter avdrag"

## 5. Ångerrätt / Allmänna villkor (distansavtalslagen) — only when applicable
A quote-request site sells nothing online → **no ångerrätt machinery needed**. BUT if the site takes bookings with payment, or binding orders: 14-day ångerrätt information, villkor page, and konsumentverkets ångerblankett link become required. Flag to human if the brief includes any online booking/payment.

## 6. Tillgänglighet
Private-sector small business sites are generally outside DOS-lagen (public sector) scope, and the European Accessibility Act (2025) targets e-commerce/consumer services — a pure lead-gen trades site is typically out of scope, but Nortropic ships WCAG 2.1 AA anyway (Gate 4). Flag to human if the client is public-sector-adjacent or adds e-commerce.

## 7. Fonts, embeds, US processors (Schrems II practice)
- **Google Fonts via CDN: never** (German rulings set the practice; self-host via `next/font`)
- Prefer EU-served/cookieless third parties; every third-party request on the site must be explainable in the policy

## Launch sign-off block (human fills)
```
[ ] Integritetspolicy reviewed against actual data flows        — sign: ____
[ ] Cookie situation verified (cookieless confirmed / consent working) — sign: ____
[ ] Företagsuppgifter + F-skatt + org.nr correct               — sign: ____
[ ] All claims verified (certifikat, betyg, jour, ROT/RUT)     — sign: ____
```
