from datetime import datetime, timedelta
from threading import Thread
from time import sleep

import win32api
import win32con
import win32gui
# pynput has .keyboard as well.
from pynput.mouse import Controller as MouseController

mouse = MouseController()


class PURPOSE:
    TEST = 0,
    WARRIOR = 1,
    TS = 2,
    ASSASSIN = 3


window_name = "Knight OnLine Client"
hwndMain = win32gui.FindWindow(None, window_name)
hwndChild = win32gui.GetWindow(hwndMain, win32con.GW_CHILD)

purpose = PURPOSE.TS


def press(code):
    win32api.keybd_event(code, win32api.MapVirtualKey(code, 0), 0, 0)
    sleep(.05)
    win32api.keybd_event(code, win32api.MapVirtualKey(code, 0), win32con.KEYEVENTF_KEYUP, 0)


def run():
    global purpose

    if purpose == PURPOSE.TEST:
        mouse.scroll(0, -1)
    elif purpose == PURPOSE.WARRIOR:
        # Presses 2.
        press(0x32)
        # Presses 3.
        press(0x33)
    elif purpose == PURPOSE.TS:
        sleep(1)
        mage = True
        # Presses ESC.
        press(0x1B)
        # TS slot (0).
        press(0x30)
        sleep(1)

        if mage:
            # Death Knight.
            for i in range(3):
                # Scrolls down.
                mouse.scroll(0, -1)
                sleep(0.5)
        else:
            # Presses TAB.
            press(0x09)
            sleep(0.5)
            # Scrolls down (Bulture).
            mouse.scroll(0, -1)
            sleep(0.5)

        # Presses enter.
        press(0x0D)
        sleep(1)
        press(0x0D)

        duration_in_seconds = 3600
        next_use = datetime.now() + timedelta(seconds=duration_in_seconds)
        print('Next TS use: {:%H:%M:%S}'.format(next_use))

        # Sleeps for 1 hour.
        sleep(duration_in_seconds)
    elif purpose == PURPOSE.ASSASSIN:
        press(0x5A)  # Z
        press(0x33)  # 3
        press(0x34)  # 4
        press(0x35)  # 5
        press(0x36)  # 6
        press(0x37)  # 7
        press(0x38)  # 8


ts_in_action = False
ts_duration_in_seconds = 3600
next_ts_use = datetime.now()


def ts_z_attack():
    global ts_in_action, next_ts_use

    if datetime.now() >= next_ts_use:
        sleep(1)
        # Presses ESC.
        press(0x1B)
        # TS slot (0).
        press(0x30)
        sleep(1)
        # Death Knight.
        for i in range(3):
            # Scrolls down.
            mouse.scroll(0, -1)
            sleep(0.5)

        # Presses enter.
        press(0x0D)
        sleep(1)
        press(0x0D)

        next_ts_use = datetime.now() + timedelta(seconds=ts_duration_in_seconds)
        print('Next TS use: {:%H:%M:%S}'.format(next_ts_use))
    else:
        press(0x5A)  # Z
        press(0x33)  # 3
        press(0x34)  # 4
        press(0x35)  # 5
        press(0x36)  # 6
        press(0x37)  # 7
        press(0x38)  # 8


win32gui.SetForegroundWindow(hwndChild)

while True:
    # http://kbdedit.com/manual/low_level_vk_list.html

    # thread = Thread(target=run())
    thread = Thread(target=ts_z_attack())

# pyinstaller --onefile C:\Users\undefined\PycharmProjects\knightonline\main.py --paths C:\Users\undefined\AppData\Local\Programs\Python\Python39-32\Lib\site-packages -n TZA
