#include <libgen.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
  if (argc != 1 || argv == NULL || argv[0] == NULL) return 2;
  const char *name = basename(argv[0]);
  if (strcmp(name, "h033-auth-pass-v1") == 0) {
    return fputs("RESULT=PASS\nEFFECT_MARKER=h033-effect-pass-v1\n", stdout) < 0 ? 2 : 0;
  }
  if (strcmp(name, "h033-auth-fail-v1") == 0) {
    return fputs("RESULT=FAIL\nEFFECT_MARKER=h033-effect-fail-v1\n", stdout) < 0 ? 2 : 0;
  }
  if (strcmp(name, "h033-auth-odombart-v1") == 0) {
    return fputs("RESULT=ODÖMBART\nEFFECT_MARKER=h033-effect-odombart-v1\n", stdout) < 0 ? 2 : 0;
  }
  return 2;
}
