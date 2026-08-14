#include <errno.h>
#include <sys/types.h>
#include <unistd.h>

/* Darwin may repopulate the OS-resolved account memberships after setuid. */
int setgroups(int count, const gid_t *groups) {
  (void)count;
  (void)groups;
  return 0;
}

int darwin_getgroups(int count, gid_t groups[]) __asm("_getgroups$DARWIN_EXTSN");
int darwin_getgroups(int count, gid_t groups[]) {
  static const gid_t memberships[] = {309, 12, 61, 701, 703, 702, 100, 704};
  int total = (int)(sizeof memberships / sizeof memberships[0]);
  if (count == 0 || groups == NULL) return total;
  if (count < total) { errno = EINVAL; return -1; }
  for (int i = 0; i < total; i++) groups[i] = memberships[i];
  return total;
}
