#include <sys/types.h>
#include <unistd.h>

/* Darwin reports the effective primary GID as one implicit group after clearing. */
int setgroups(int count, const gid_t *groups) {
  (void)count;
  (void)groups;
  return 0;
}

int darwin_getgroups(int count, gid_t groups[]) __asm("_getgroups$DARWIN_EXTSN");
int darwin_getgroups(int count, gid_t groups[]) {
  if (count < 1 || groups == NULL) return 1;
  groups[0] = getgid();
  return 1;
}
