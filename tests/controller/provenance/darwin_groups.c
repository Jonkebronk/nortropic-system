#include <sys/types.h>
#include <unistd.h>

/* Darwin may omit the effective GID from the supplementary-group list. */
int setgroups(int count, const gid_t *groups) {
  (void)count;
  (void)groups;
  return 0;
}

int darwin_getgroups(int count, gid_t groups[]) __asm("_getgroups$DARWIN_EXTSN");
int darwin_getgroups(int count, gid_t groups[]) {
  (void)count;
  (void)groups;
  return 0;
}
