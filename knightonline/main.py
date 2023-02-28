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
    sleep(1)

    global purpose

    if purpose == PURPOSE.TEST:
        mouse.scroll(0, -1)
    elif purpose == PURPOSE.WARRIOR:
        # Presses 2.
        press(0x32)
        # Presses 3.
        press(0x33)
    elif purpose == PURPOSE.TS:
        # Presses ESC.
        press(0x1B)
        # TS slot (0).
        press(0x30)
        sleep(1)
        # Presses TAB.
        press(0x09)
        sleep(0.5)
        # Scrolls down.
        mouse.scroll(0, -1)
        sleep(0.5)
        # Presses enter.
        press(0x0D)
        sleep(1)
        press(0x0D)

        # # Loops to "Above 60 lvl".
        # for i in range(5):
        #     # Presses arrow down.
        #     press(0x28)
        #
        # # Presses TAB.
        # press(0x09)
        #
        # # Presses Arrow down.
        # press(0x28)

        # Sleeps for 1 hour and 5 seconds.
        sleep(3605)
    elif purpose == PURPOSE.ASSASSIN:
        press(0x33)
        press(0x34)
        press(0x35)
        press(0x36)
        press(0x37)
        press(0x38)


win32gui.SetForegroundWindow(hwndChild)

while True:
    # http://kbdedit.com/manual/low_level_vk_list.html

    thread = Thread(target=run())

# pyinstaller --onefile C:\Users\undefined\PycharmProjects\gogan\main.py --paths C:\Users\undefined\AppData\Local\Programs\Python\Python39-32\Lib\site-packages
