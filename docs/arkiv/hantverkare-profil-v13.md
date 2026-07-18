# Branschprofil: hantverkare (VVS/rör, el, städ, bygg/snickeri, låssmed, målare...)

Referensimplementationen — den kalibrering som var hårdkodad i systemet t.o.m. v12.1, extraherad vid v13. Plannern (steg 5e) återanvänder och anpassar denna mot varje kunds research; profilen är ett UTGÅNGSLÄGE, briefens §7 är kontraktet. Levande fil: 5e uppdaterar den efter godkända briefs. Fryst snapshot vid v13: `docs/arkiv/hantverkare-profil-v13.md` i systemrepot.

## §7.1 Arketyp & primärhandling
- **Arketyp:** akut/planerat hemarbete hos en stressad husägare som jämför tre flikar i mobilen.
- **Primärhandling:** `offert` + samtal som par — akutbranscher (VVS-jour, låssmed) lutar mot `ring nu`; planerat arbete (bygg, målning) mot `offert`.
- **Gate 1-test (klartext):** "tel-länkar öppnar uppringaren på 375px; offertformulär → mejl LEVERERAT till LEAD_TO_EMAIL (Resend-status, aldrig ett 200); felväg utan Resend-nyckel visar telefonnumret; phone_click/quote_submit avfyras; telefon på 404/error."
- CTA-par: "Ring [nummer]" + "Få kostnadsfri offert". Sticky nummer, flytande ringknapp ≥56px.

## §7.2 Röstregister
- **Adjektiv:** pålitlig, konkret, lugn, rak, jordnära.
- **Registret ("trusted local tradesperson"):** korta meningar; siffror, orter och restider i stället för adjektiv; skriven för en stressad husägare som bestämmer sig på 30 sekunder.
- **Exempelmeningar (mönster):** "Stopp i avloppet i Täby? Vi är där inom 2 timmar." · "Fast pris efter kostnadsfri besiktning."
- **Legitimt bransch-vernacular:** jour, inställelsetid, fast pris, ROT-avdrag, besiktning, behörighet/auktoriserad (endast med kvitto), "vi lämnar rent efter oss".

### Ton per undergren (fd copy-blocklist "Tone calibration by trade" + content-designers rad)
- **VVS/rör**: urgent-capable, reassuring. Emergencies are the entry point; planned work is the upsell. (urgent-reassuring)
- **El**: safety + behörighet first (auktoriserad elinstallatör, Elsäkerhetsverket) — trust beats speed. (safety/behörighet-first)
- **Städ**: reliability + recurring relationship. RUT-avdrag prominent, "samma team varje gång". (reliability + RUT)
- **Bygg/hantverk**: portfolio + process. Before/after, referensjobb med ort, tydlig offertprocess. (process + referens)

## §7.3 Bransch-antislop (adderas till bas-blocklistan)
- "Inga jobb är för små eller för stora"
- "Vi tar hand om hela kedjan"
- "Från idé till färdigt resultat"
- "Gratis offert utan förpliktelser" (som fluff — pristransparens ska vara konkret)
- "Med många års erfarenhet i branschen" (utan årtal = tomt)
- "Vi sätter kunden först"
- Ogrundade "auktoriserad/certifierad" utan register-/certifikatkvitto

## §7.4 Kvittolista & attribution
- **Kvitton:** F-skatt (obligatoriskt kvitto i footer — invariant), org.nr, certifikat/behörigheter (t.ex. Säker Vatten, Elsäkerhetsverkets register — alltid med källa), försäkring/ansvarsförsäkring, garantier, riktiga omdömen med namn + ort, referensjobb med ort, before/after-foton av riktiga jobb.
- **Bransch-obligatoriska copyelement (fd copy-blocklist Required):** ROT/RUT-avdrag där tillämpligt, helst med kundens faktiska pris efter avdrag; restidslöfte above fold ENDAST om genuint sant; "Jour dygnet runt" ENDAST om numret faktiskt är bemannat.
- **Attributionsregler:** behörighet redovisas med register/utfärdare; garanti med villkor; betyg med källa och antal; aldrig årtal/eftablering utan research-belägg.

## §7.5 Schema-typ
`LocalBusiness`-subtyp per undergren: `Plumber`, `Electrician`, `HousePainter`, `HVACBusiness`, `MovingCompany`, `HomeAndConstructionBusiness` (snickare — Carpenter finns inte i schema.org)...

## §7.6 SEO-läge
`lokal` — full "[tjänst] i [stad]"-ortsjakt; ortssidor endast för orter där firman faktiskt jobbar (5 riktiga slår 25 spunna).

## §7.7 Juridikflaggor
Inga — bas-juridiken räcker (Integritetspolicy, cookie-läge, Företagsuppgifter, claims-verifierbarhet).

## §7.8 Motion-nivå
Sätts per kund i §5; hantverkar-default `subtil`.
