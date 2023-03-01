import sys

major, minor, micro, releaselevel, serial = sys.version_info

if major != 3:
    sys.exit(1) # for consistent exit codes
else:
    print(minor) # outputs to stdout
    sys.exit(0)