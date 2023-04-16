import ctypes
import os
from time import sleep

from colorful_text import text


def running_as_admin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if not is_admin:
        text('You must run this software as administrator.')

        sleep(10)

        raise SystemExit(0)
