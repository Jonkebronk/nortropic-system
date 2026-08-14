#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#ifndef FAULT_MARKER
#error FAULT_MARKER is required
#endif

pid_t fork(void) {
  errno = EAGAIN;
  return -1;
}

pid_t waitpid(pid_t pid, int *status, int options) {
  (void)status;
  (void)options;
  if (pid == -1) return 0;
  errno = ECHILD;
  return -1;
}

int kill(pid_t pid, int signal_number) {
  int fd = open(FAULT_MARKER, O_WRONLY | O_CREAT | O_APPEND, 0600);
  if (fd >= 0) {
    dprintf(fd, "pid=%d signal=%d\n", pid, signal_number);
    close(fd);
  }
  errno = EINVAL;
  return -1;
}
