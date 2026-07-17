# Nortropic Design Checklist — Full Reference

Judge everything mobile-first (375px), then 768/1280. The visitor is outdoors, in sunlight, one-handed, stressed.

## 1. Header (sticky, every page)
- [ ] Logo left, compact — max 40px tall on mobile
- [ ] **Phone number visible as text** (not icon-only) on ≥768px; on mobile a ring-icon button with `tel:` link, right-aligned in thumb zone
- [ ] Primary CTA button ("Få offert") beside phone on desktop
- [ ] Nav: max 7 items, no dropdowns deeper than 1 level, "Kontakt" always last
- [ ] Header height ≤64px mobile; never covers content on scroll-up reveal

## 2. Hero
- [ ] Headline = the visitor's problem or the outcome, with geografi: "Elektriker i Uppsala — jour dygnet runt"
- [ ] Sub-line: what you do + where + how fast
- [ ] One primary CTA (call) + one secondary (quote form anchor) — never three buttons
- [ ] Trust row within the fold: Google-betyg (real number), år i branschen, certifikat-badges
- [ ] Background: real photo (team/job/van) with legible overlay, or clean solid/soft tone. NEVER: gradient mesh, blobs, dot grids, particle effects, 3D illustrations
- [ ] LCP element is this hero image/text — must render < 2.5s

## 3. Mobile call ergonomics
- [ ] Floating call button: bottom-right, ≥56×56px, `tel:` link, visible on every page after 300px scroll
- [ ] Every phone number in body text is a `tel:` link
- [ ] Tap targets ≥44px, spaced ≥8px

## 4. Quote form
- [ ] Max 5 fields: Namn, Telefon, (E-post), Tjänst (select), Meddelande
- [ ] Telefon field first-class — many visitors prefer callback over writing
- [ ] Inline on Kontakt page AND as section on Hem — never modal-only
- [ ] Submit button says what happens: "Skicka — vi ringer inom 30 min" (only if true)
- [ ] Success state confirms next step + shows phone number as fallback
- [ ] Labels above fields, visible (no placeholder-only labels), autocomplete attributes set

## 5. Trust architecture
- [ ] Omdömen with **full name + ort** ("Anna L., Sollentuna") — anonymous 5-star walls read as fake
- [ ] Google reviews: real rating number + count, linked to the profile
- [ ] Badges that mean something in Sverige: F-skattsedel, ID06 (bygg), Säker Vatten (VVS), Elsäkerhetsverket-registrering (el), försäkringsbolag, branschorganisationer
- [ ] Garanti stated concretely ("5 års garanti på ROT-arbeten"), not "nöjd-kund-garanti" fluff
- [ ] Om oss: real faces, real names, real history. No stock-suits.

## 6. Photography
- [ ] Real > perfect: team at work, vans with logo, completed jobs, before/after pairs
- [ ] No US stock (headsets, glass offices, handshakes), no AI-generated humans
- [ ] Every image has descriptive Swedish alt text; WebP/AVIF; explicit width/height (no CLS)

## 7. Color & type
- [ ] Palette anchored by trade + trust: VVS/rör → blues; el/energi → amber/warm; städ → greens/fresh; bygg → earthy/robust. One accent for CTAs only, used nowhere else
- [ ] CTA color contrast ≥4.5:1, and the CTA is the ONLY element in that color
- [ ] Max 2 typefaces; body ≥16px mobile; line length 45–75 chars; headlines sentence case (Swedish convention — never Title Case Every Word)
- [ ] No thin gray text on white (min contrast 4.5:1 for body)

## 8. Layout & motion
- [ ] Sections alternate rhythm (text/image, full-bleed, cards) — not five identical centered blocks
- [ ] Left-aligned body text; centering reserved for short heroes/CTA banners
- [ ] Motion: subtle reveals ≤300ms max, respects `prefers-reduced-motion`. No counters, typewriters, parallax, scroll-hijack
- [ ] Cards: consistent but not uniform — vary emphasis by importance, not by template

## 9. Page-bottom pattern (every page)
- [ ] Closing CTA banner: phone + quote button + service area reminder
- [ ] Footer: NAP exactly matching Google Företagsprofil (namn, adress, telefon), org.nr, öppettider, service areas as links, Integritetspolicy link
- [ ] Footer is small — a 6-page site needs no mega-footer

## Severity guide
**Instant fail** = breaks lead generation (phone/CTA missing, form broken/bloated, slop hero).
**Signal** = erodes trust or distinctiveness (stock/AI photos, template patterns, motion junk).
Fix all instant fails before design review; batch signals into one polish pass with `impeccable`.
