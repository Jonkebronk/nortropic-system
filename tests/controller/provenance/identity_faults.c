#include <errno.h>
#include <grp.h>
#include <sys/types.h>
#include <unistd.h>

#ifdef FAIL_SETGROUPS
int setgroups(int count, const gid_t *groups) {
  (void)count;
  (void)groups;
  errno = EPERM;
  return -1;
}
#endif

#ifdef WRONG_EUID
static int identity_dropped;

int setuid(uid_t uid) {
  if (uid != getuid()) {
    errno = EPERM;
    return -1;
  }
  identity_dropped = 1;
  return 0;
}

uid_t geteuid(void) {
  return identity_dropped ? getuid() + 1 : getuid();
}
#endif
