__author__ = "Chad J. Schroeder"
__copyright__ = "Copyright (C) 2005 Chad J. Schroeder"
__revision__ = "$Id$"
__version__ = "0.2"

import os               # Miscellaneous OS interfaces.
import sys              # System-specific parameters and functions.
import resource

# File mode creation mask of the daemon.
UMASK = 0

WORKDIR = "/"

# Default maximum for the number of available file descriptors.
MAXFD = 1024

# The standard I/O file descriptors are redirected to /dev/null by default.
if (hasattr(os, "devnull")):
    REDIRECT_TO = os.devnull
else:
    REDIRECT_TO = "/dev/null"

def createDaemon():
    """Detach a process from the controlling terminal and run it in the
    background as a daemon.
    """

    try:
        pid = os.fork()
    except OSError, e:
        raise Exception, "%s [%d]" % (e.strerror, e.errno)

    if (pid == 0):       # The first child.
        os.setsid()

        try:
            pid = os.fork()        # Fork a second child.
        except OSError, e:
            raise Exception, "%s [%d]" % (e.strerror, e.errno)

        if (pid == 0):    # The second child.
            os.chdir(WORKDIR)
            os.umask(UMASK)
        else:
            os._exit(0)    # Exit parent (the first child) of the second child.
    else:
        os._exit(0)       # Exit parent of the first child.

    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = MAXFD

    # Iterate through and close all file descriptors.
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:   # ERROR, fd wasn't open to begin with (ignored)
            pass

    os.open(REDIRECT_TO, os.O_RDWR)      # standard input (0)

    # Duplicate standard input to standard output and standard error.
    os.dup2(0, 1)                        # standard output (1)
    os.dup2(0, 2)                        # standard error (2)

    return(0)

if __name__ == "__main__":

    retCode = createDaemon()

    procParams = """
   return code = %s
   process ID = %s
   parent process ID = %s
   process group ID = %s
   session ID = %s
   user ID = %s
   effective user ID = %s
   real group ID = %s
   effective group ID = %s
   """ % (retCode, os.getpid(), os.getppid(), os.getpgrp(), os.getsid(0),
          os.getuid(), os.geteuid(), os.getgid(), os.getegid())

    open("createDaemon.log", "w").write(procParams + "\n")

    sys.exit(retCode)