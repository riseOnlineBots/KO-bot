from datetime import datetime, timedelta
from threading import Thread, Event as ThreadEvent
from time import sleep

import win32api
import win32con
import win32gui

import keyboard_detector
from admin_privileges import running_as_admin
from device_validation import DeviceValidation

registered_devices = ['D8-BB-C1-17-F1-9E', '50-2B-73-CC-02-29', 'B4-2E-99-F3-C3-E7', '30-9C-23-E0-93-1B',
                      '1C-BF-CE-78-C9-EA', '30-9C-23-00-7B-A8', '00-E0-4C-C0-AF-D7', '98-8D-46-DE-EF-09',
                      'B4-2E-99-F3-C6-2E', '2C-F0-5D-6E-A8-BF', '00-E0-4C-B4-07-CF']
device_registration = DeviceValidation(registered_devices)
running_as_admin()

keyboard_monitor = keyboard_detector.KeyboardDetector()
keyboard_monitor.start()

# http://kbdedit.com/manual/low_level_vk_list.html
ENTER = 0x0D
TAB = 0x09
R = 0x52
Z = 0x5A
ZERO = 0x30
TWO = 0x32
THREE = 0x33
FOUR = 0x34
FIVE = 0x35
SIX = 0x36
SEVEN = 0x37
EIGHT = 0x38

window_name = "Knight OnLine Client"
hwndMain = win32gui.FindWindow(None, window_name)
hwndChild = win32gui.GetWindow(hwndMain, win32con.GW_CHILD)


def press(code):
    win32api.keybd_event(code, win32api.MapVirtualKey(code, 0), 0, 0)
    sleep(.05)
    win32api.keybd_event(code, win32api.MapVirtualKey(code, 0), win32con.KEYEVENTF_KEYUP, 0)


def click(evt='left'):
    event_up = win32con.MOUSEEVENTF_LEFTUP if evt == 'left' else win32con.MOUSEEVENTF_RIGHTUP
    event_down = win32con.MOUSEEVENTF_LEFTDOWN if evt == 'left' else win32con.MOUSEEVENTF_RIGHTDOWN

    win32api.mouse_event(event_down, 0, 0)
    sleep(0.1)
    win32api.mouse_event(event_up, 0, 0)


def keep_mouse_in_window():
    (x, y, w, h) = win32gui.GetWindowRect(hwndChild)
    center_x = x
    center_y = y
    win32api.SetCursorPos((center_x, center_y))
    click('right')


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
        sleep(0.3)


def ts_use(ts_for_mage=False):
    sleep(0.5)
    press(ZERO)
    sleep(1)

    if ts_for_mage:
        # Death Knight.
        scroll(-3)
    else:
        press(TAB)
        sleep(0.5)
        # Bulture.
        scroll(-1)
        sleep(0.5)

    press(ENTER)
    sleep(0.5)
    press(ENTER)


def warrior_combo():
    press(TWO)
    press(THREE)

    sleep(0.68)
    press(R)
    sleep(0.15)
    press(R)


def assassin_combo():
    press(THREE)
    press(FOUR)
    press(FIVE)
    press(SIX)
    press(SEVEN)
    press(EIGHT)

    sleep(0.68)
    press(R)
    sleep(0.15)
    press(R)


def mage_soft_combo():
    press(THREE)
    press(FOUR)
    press(FIVE)
    press(SIX)
    press(SEVEN)
    press(EIGHT)


def bp_soft_combo():
    press(TWO)


next_ts_use = datetime.now()
next_skill_use = datetime.now()


def ts_with_combo_run():
    global next_ts_use, next_skill_use

    if datetime.now() >= next_ts_use:
        ts_for_mage = False
        ts_use(ts_for_mage)

        next_ts_use = datetime.now() + timedelta(seconds=3600)
        print('Next TS use: {:%H:%M:%S}'.format(next_ts_use))
    else:
        if datetime.now() >= next_skill_use:
            # press(Z)
            # mage_soft_combo()
            # bp_soft_combo()
            # warrior_combo()
            assassin_combo()
            next_skill_use = datetime.now() + timedelta(seconds=0.1)  # seconds=1 for bp, 0.1 for others.


def run_thread(pause_event):
    while True:
        if keyboard_monitor.get_combination_active():
            pause_event.set()  # Pauses the thread.
        else:
            if pause_event.is_set():
                pause_event.clear()

            ts_with_combo_run()


if device_registration.is_device_legal():
    win32gui.SetForegroundWindow(hwndChild)

    pause_event = ThreadEvent()
    thread = Thread(target=run_thread, args=(pause_event,))
    thread.start()

# pyinstaller --onefile C:\Users\undefined\PycharmProjects\knightonline\main.py --paths C:\Users\undefined\AppData\Local\Programs\Python\Python39-32\Lib\site-packages --key myKey -n TZA
