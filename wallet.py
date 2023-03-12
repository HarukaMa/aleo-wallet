import os
import pathlib
import sys

import appdirs

is_windows = os.name == "nt"

if is_windows:
    import win32file
else:
    import fcntl

from wallet import main

if __name__ == '__main__':
    # noinspection PyTypeChecker

    data_path = appdirs.user_data_dir("WalletDev", False)
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    lockfile = data_path + "/wallet.lock"
    pathlib.Path(lockfile).touch()
    if is_windows:
        try:
            lock = win32file.CreateFile(lockfile, win32file.GENERIC_READ, 0, None, win32file.OPEN_EXISTING, 0, None)
        except:
            sys.exit(255)
        sys.exit(main())
    else:
        with open(lockfile, "r") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except:
                sys.exit(255)
            sys.exit(main())
