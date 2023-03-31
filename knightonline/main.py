from datetime import datetime, timedelta
from threading import Thread
from time import sleep

import win32api
import win32con
import win32gui


class PURPOSE:
    TEST = 0,
    WARRIOR = 1,
    TS = 2,
    ASSASSIN = 3


purpose = PURPOSE.ASSASSIN
ts_for_mage = True

window_name = "Knight OnLine Client"
hwndMain = win32gui.FindWindow(None, window_name)
hwndChild = win32gui.GetWindow(hwndMain, win32con.GW_CHILD)


def press(code):
    win32api.keybd_event(code, win32api.MapVirtualKey(code, 0), 0, 0)
    sleep(.05)
    win32api.keybd_event(code, win32api.MapVirtualKey(code, 0), win32con.KEYEVENTF_KEYUP, 0)


def press_left():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def press_right():
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
    sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)


def scroll_down():
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -1, 0)


def keep_mouse_in_window():
    (x, y, w, h) = win32gui.GetWindowRect(hwndChild)
    center_x = x + 15
    center_y = y - 130
    win32api.SetCursorPos((center_x, center_y))
    press_right()


def scroll(clicks=0):
    """
    :param clicks: + values = scroll up. - values = scroll down
    """
    if clicks > 0:
        increment = win32con.WHEEL_DELTA
    else:
        increment = win32con.WHEEL_DELTA * -1

    for _ in range(abs(clicks)):
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, increment, 0)
        sleep(0.5)


def run():
    global purpose, ts_for_mage

    if purpose == PURPOSE.TEST:
        scroll_down()
    elif purpose == PURPOSE.WARRIOR:
        # Presses 2.
        press(0x32)

        # Presses 3.
        press(0x33)
        sleep(0.68)
        # R
        press(0x52)
        sleep(0.15)
        press(0x52)

    elif purpose == PURPOSE.TS:
        win32gui.SetForegroundWindow(hwndChild)
        sleep(1)
        # Presses ESC.
        press(0x1B)
        # TS slot (0).
        press(0x30)
        sleep(1)

        if ts_for_mage:
            # Death Knight.
            for i in range(3):
                # Scrolls down.
                scroll_down()
                sleep(0.5)
        else:
            # Presses TAB.
            press(0x09)
            sleep(0.5)
            # Scrolls down (Bulture).
            scroll_down()
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
        # press(0x5A)  # Z
        press(0x33)  # 3
        press(0x34)  # 4
        press(0x35)  # 5
        press(0x36)  # 6
        press(0x37)  # 7
        press(0x38)  # 8
        sleep(0.68)

        press(0x52)
        sleep(0.15)
        press(0x52)


ts_duration_in_seconds = 3600
next_ts_use = datetime.now()
next_skill_use = datetime.now()


def ts_z_attack():
    global next_ts_use, next_skill_use, ts_for_mage

    if datetime.now() >= next_ts_use:
        sleep(0.5)
        keep_mouse_in_window()
        sleep(0.5)
        # TS slot (0).
        press(0x30)
        sleep(1)

        if ts_for_mage:
            # Death Knight.
            scroll(-3)
        else:
            # Presses TAB.
            press(0x09)
            sleep(0.5)
            # Scrolls down (Bulture).
            scroll_down()
            sleep(0.5)

        # Presses enter.
        press(0x0D)
        sleep(0.5)
        press(0x0D)

        next_ts_use = datetime.now() + timedelta(seconds=ts_duration_in_seconds)
        print('Next TS use: {:%H:%M:%S}'.format(next_ts_use))
    else:
        if datetime.now() >= next_skill_use:
            if ts_for_mage:
                press(0x5A)  # Z
                press(0x33)  # 3
                press(0x34)  # 4
                press(0x35)  # 5
                press(0x36)  # 6
                press(0x37)  # 7
                press(0x38)  # 8
            else:
                # No Z here.
                press(0x32)  # 2
            next_skill_use = datetime.now() + timedelta(seconds=1)


win32gui.SetForegroundWindow(hwndChild)

while True:
    # http://kbdedit.com/manual/low_level_vk_list.html

    # thread = Thread(target=run())
    thread = Thread(target=ts_z_attack())

# pyinstaller --onefile C:\Users\undefined\PycharmProjects\knightonline\main.py --paths C:\Users\undefined\AppData\Local\Programs\Python\Python39-32\Lib\site-packages -n TZA
