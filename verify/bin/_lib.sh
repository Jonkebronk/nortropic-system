# Delad hjälpkod för exit-testerna. Källas av varje h-00N-exit.
# Odömbart räknas ALLTID som FAIL — aldrig tyst grönt.
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
