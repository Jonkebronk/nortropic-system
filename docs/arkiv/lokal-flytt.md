# Lokal flytt — engångschecklista för operatörens maskin

Senast verifierad mot systemet: 2026-07-18 · b68252e

> Körs EN gång på operatörens lokala maskin, efter att v9 mergats. Filerna nedan finns bara där — inte i repot och inte i fjärrmiljöer. I drift är repo-roten `~/.claude`, så dokumentationen nås som `~/.claude/docs/`. När checklistan är genomförd är den historik (filen ligger i `arkiv/` och uppdateras inte).

## 1. Ersätt guiden med en pekfil

Ersätt HELA innehållet i `~/Workflow/NORTROPIC-GUIDE.md` med exakt detta:

```markdown
# Flyttad

Flyttad — se docs/00-guide.md i nortropic-system (`~/.claude/docs/00-guide.md`).
Denna pekfil uppdateras inte.
```

Originalinnehållet behöver inte sparas separat: guiden är omskriven ur systemfilerna som `docs/00-guide.md`, uppdaterad mot v8-verkligheten i samma svep.

## 2. Ersätt systemplanen med en pekfil

Ersätt HELA innehållet i `~/Workflow/NORTROPIC-SYSTEM-PLAN.md` med exakt detta:

```markdown
# Flyttad

Flyttad — se docs/arkiv/systemplan.md i nortropic-system (`~/.claude/docs/arkiv/systemplan.md`, fryst designhistorik).
Levande beslut förs i `~/.claude/docs/05-beslutslogg.md`.
Denna pekfil uppdateras inte.
```

## 3. Uppdatera minnet `nortropic_system.md`

I minnesfilen `nortropic_system.md` (under `~/.claude`-minnesstrukturen på den lokala maskinen): ersätt varje omnämnande av att dokumentationen bor i `~/Workflow` med följande stycke:

```markdown
Dokumentationen bor i systemrepots docs/: README.md i ~/.claude-roten är ingången,
~/.claude/docs/00-guide.md är operatörsguiden, docs/05-beslutslogg.md är beslutsloggen
som får en rad vid VARJE applicerat steward-förslag, och doctor-kontroll #12 vaktar
docs-drift. Pekfilerna i ~/Workflow (NORTROPIC-GUIDE.md, NORTROPIC-SYSTEM-PLAN.md)
uppdateras inte.
```

## 4. Städgrep — inga brutna referenser

Kör:

```bash
grep -rn "NORTROPIC-GUIDE\|SYSTEM-PLAN" ~/.claude ~/Workflow --include='*.md'
```

Förväntat resultat: träffar ENDAST i de två pekfilerna från steg 1–2 och i denna fil. Varje annan träff är en referens som ska uppdateras till den nya sökvägen (`~/.claude/docs/…`). I själva systemrepot finns inga sådana referenser — det är verifierat vid v9-leveransen.

## 5. Kvitto i beslutsloggen

Lägg en rad i `~/.claude/docs/05-beslutslogg.md`:

```
| <dagens datum> | v9 lokal flytt | Pekfiler på plats i ~/Workflow, minnet uppdaterat, städgrep ren | <commit> |
```

Committa raden. Därmed är hela v9-flytten klar och spårbar.
