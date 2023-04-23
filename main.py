import os
import random
import re
from datetime import datetime, timedelta
from threading import Thread
from time import sleep

import cv2
import win32api
import win32con
import win32gui

import keyboard_detector
import process_ocr
from admin_privileges import running_as_admin
from device_validation import DeviceValidation
from thread_safe_queue import ThreadSafeQueue
from window_capture import WindowCapture

os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
NINE = 0x39
ALT = 0xA4
X = 0x58
MIDDLE_BUTTON = 0x04

window_name = "Knight OnLine Client"
wincapture = WindowCapture(window_name)

prev_coordination = None
gm_protection = False
ocr_error_counter = 0


class CharacterEnum:
    MAGE_GOD = 1
    BP = 2
    WARRIOR = 3
    ASSASSIN = 4
    MAGE_SOFT = 5


def press(code):
    win32api.keybd_event(code, win32api.MapVirtualKey(code, 0), 0, 0)
    sleep(random.uniform(0.03, 0.10))
    win32api.keybd_event(code, win32api.MapVirtualKey(code, 0), win32con.KEYEVENTF_KEYUP, 0)


def click(evt='left'):
    event_up = win32con.MOUSEEVENTF_LEFTUP if evt == 'left' else win32con.MOUSEEVENTF_RIGHTUP
    event_down = win32con.MOUSEEVENTF_LEFTDOWN if evt == 'left' else win32con.MOUSEEVENTF_RIGHTDOWN

    win32api.mouse_event(event_down, 0, 0)
    sleep(random.uniform(0.1, 0.2))
    win32api.mouse_event(event_up, 0, 0)


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
        sleep(random.uniform(0.2, 0.3))


def ts_use(ts_for_mage=False):
    sleep(0.5)
    press(ZERO)
    sleep(random.uniform(0.9, 1))

    if ts_for_mage:
        # Death Knight.
        scroll(-4)
        press(TAB)
        scroll(-1)
    else:
        press(TAB)
        sleep(0.5)
        # Bulture.
        scroll(-1)
        sleep(0.5)

    press(ENTER)
    sleep(0.5)
    press(0x1B)
    sleep(0.5)
    press(0x1B)


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


ts_interval = random.uniform(3600, 3602)
next_ts_use = datetime.now()
next_skill_use = datetime.now()
next_skill_use_timedelta = random.uniform(0.1, 0.2)
mana_interval = random.uniform(54, 56)
next_mana_use_for_mage = datetime.now() + timedelta(seconds=mana_interval)


def read_screen(text_reader_thread):
    queue_cleared = False

    while True:
        if not keyboard_monitor.get_combination_active():
            screenshot = wincapture.get_screenshot()[0:90, 0:200]

            # Scale the image by a factor of 1.5
            scaled_img = cv2.resize(screenshot, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)

            text_reader_thread.put(scaled_img)

            sleep(5)
        else:
            if not queue_cleared:
                text_reader_thread.clear()
                queue_cleared = True


def ocr_info_bar(text_reader_thread):
    global prev_coordination, ocr_error_counter

    while True:
        if not keyboard_monitor.get_combination_active():
            screenshot = text_reader_thread.get()

            if screenshot is None:
                sleep(1)
                continue

            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            results = process_ocr.process(gray, debug=False)
            # hp = results[1]
            # mp = results[2]

            try:
                coordination_format = re.compile(".*,")
                coordination_probabilities = list(filter(coordination_format.match, results))

                pattern = r'([a-zA-Z]+)(\s+)(\d+)(,\d+)'
                result = re.sub(pattern, r'\1\2\3\4', coordination_probabilities[0])
                result = result.split()

                coordination = result[1] if len(result) > 1 else result[0]
                print('Coordination check - ', coordination, ' - at {:%H:%M:%S}'.format(datetime.now()))

                if prev_coordination is not None and coordination != prev_coordination:
                    keyboard_monitor.set_combination_active(True)
                    press(X)
                    print('...GM detected and program paused at {:%H:%M:%S}...'.format(datetime.now()))

                prev_coordination = coordination
            except Exception as e:
                print('Error occurred while parsing coordinates. Re-reading...', e)
                print('Rotating camera angle.')
                press(MIDDLE_BUTTON)
                ocr_error_counter += 1
                # ocr_info_bar(text_reader_thread)

                if ocr_error_counter > 4:
                    print('Big problem...')
                    break

            sleep(5)

            # key = cv2.waitKey(1) & 0xFF

            # if key == ord("q"):
            #     break


def run_combo_ts(bot_type):
    while True:
        if not keyboard_monitor.get_combination_active():
            global next_ts_use, next_skill_use, next_skill_use_timedelta, next_mana_use_for_mage

            if datetime.now() >= next_ts_use:
                ts_for_mage = bot_type == CharacterEnum.MAGE_GOD or bot_type == CharacterEnum.MAGE_SOFT
                ts_use(ts_for_mage)

                next_ts_use = datetime.now() + timedelta(seconds=ts_interval)

                print('Next TS use: {:%H:%M:%S}'.format(next_ts_use))
            else:
                if datetime.now() >= next_skill_use:
                    if bot_type == CharacterEnum.MAGE_GOD or bot_type == CharacterEnum.MAGE_SOFT:
                        if bot_type == CharacterEnum.MAGE_GOD:
                            press(Z)

                        mage_soft_combo()

                        if datetime.now() >= next_mana_use_for_mage:
                            press(NINE)

                            next_mana_use_for_mage = datetime.now() + timedelta(seconds=mana_interval)
                    elif bot_type == CharacterEnum.BP:
                        next_skill_use_timedelta = random.uniform(1, 1.2)
                        bp_soft_combo()
                    elif bot_type == CharacterEnum.WARRIOR:
                        warrior_combo()
                    elif bot_type == CharacterEnum.ASSASSIN:
                        assassin_combo()

                    next_skill_use = datetime.now() + timedelta(seconds=next_skill_use_timedelta)


def start():
    text_reader_thread = ThreadSafeQueue()

    Thread(target=read_screen, args=(text_reader_thread,)).start()

    if gm_protection:
        Thread(target=ocr_info_bar, args=(text_reader_thread,)).start()

    Thread(target=run_combo_ts, args=(bot_type,)).start()


if __name__ == '__main__':
    if device_registration.is_device_legal():
        gm_protection_answer = input('Enable GM protection? y or n: ').lower()

        if gm_protection_answer == 'y':
            gm_protection = True

        print("What type do you want to run with TS?")
        print("{} = Mage (God Mode)".format(CharacterEnum.MAGE_GOD))
        print("{} = BP".format(CharacterEnum.BP))
        print("{} = Warrior".format(CharacterEnum.WARRIOR))
        print("{} = Assassin".format(CharacterEnum.ASSASSIN))
        print("{} = Mage (Soft Mode)".format(CharacterEnum.MAGE_SOFT))

        bot_type = int(input('Your answer: '))

        if 1 <= bot_type <= 5:
            win32api.keybd_event(ALT, win32api.MapVirtualKey(ALT, 0), 0, 0)

            try:
                hwnd_main = win32gui.FindWindow(None, window_name)
                hwnd_child = win32gui.GetWindow(hwnd_main, win32con.GW_CHILD)
                win32gui.SetForegroundWindow(hwnd_child)
            finally:
                win32api.keybd_event(ALT, win32api.MapVirtualKey(ALT, 0), win32con.KEYEVENTF_KEYUP, 0)

                Thread(target=start).start()

# pyinstaller --onefile C:\Users\undefined\PycharmProjects\knightonline\main.py --paths C:\Users\undefined\AppData\Local\Programs\Python\Python39-32\Lib\site-packages --key myKey -n TZA
