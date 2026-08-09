# Delad hjälpkod för exit-testerna. Källas av varje h-00N-exit.
# Odömbart räknas ALDRIG som grönt. exit 0 = PASS, 1 = FAIL, 2 = ODÖMBART.
set -u
pass=0; fail=0
ok() { echo "PASS  $1"; pass=$((pass+1)); }
no() { echo "FAIL  $1 — $2"; fail=$((fail+1)); }
krav_komponent() {
  if [ ! -x "$1" ]; then
    echo "FAIL  K0 komponent — $1 saknas eller är inte körbar"
    echo; echo "0 PASS, 1 FAIL"
    exit 1
  fi
  ok "K0 komponent finns och är körbar"
}
summera() {
  echo; echo "$pass PASS, $fail FAIL"
  [ "$fail" -eq 0 ] || exit 1
}

# Mekanismkontroll. Ett test som förväntar sig ett STOPP måste först belägga
# att stoppmekanismen är aktiv — annars är "nekade" och "fanns inte" samma
# utfall. Odömbart är varken PASS eller FAIL: exit 2.
#   $1 = mekanismens namn
#   $2 = kommando som lyckas (exit 0) om och endast om mekanismen är aktiv
krav_mekanism() {
  if ! eval "$2" >/dev/null 2>&1; then
    echo "SKIP  K1 mekanism — $1 ej aktiv, testet är odömbart"
    echo; echo "$pass PASS, $fail FAIL, ODÖMBART"
    exit 2
  fi
  ok "K1 mekanism aktiv: $1"
}

# Temp-katalog. verify/ ligger i denyWrite — ett test som skriver bredvid sig
# själv fallerar på skrivförbud och rapporterar rött av fel skäl.
# TMPDIR kan bära ett AVSLUTANDE SNEDSTRECK — macOS ger /var/folders/.../T/ —
# och utan strykningen blir sökvägen ".../T//nortropic-exit.XXXXXX". Dubbelslashen
# är laglig men inte kanonisk: Python normaliserar bort den när en komponent
# skriver ut sin sökväg, bash gör det inte när ett prov bygger sin jämförelse.
# Ett prov som jämför en egenbyggd absolut sökväg mot en komponents utdata föll
# därför i ägarterminalen och passerade i sandboxen — samma commit, olika TMPDIR
# (mätt 2026-08-09, h-016:s K19). Strykningen sker HÄR så klassen aldrig uppstår.
temp_kat() {
  local bas="${TMPDIR:-/tmp}"
  mktemp -d "${bas%/}/nortropic-exit.XXXXXX"
}
