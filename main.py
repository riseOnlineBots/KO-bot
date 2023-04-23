import os
import random
import re
import threading
import warnings
from datetime import datetime, timedelta
from threading import Thread
from time import sleep

import win32api
import win32con
import win32gui
from cv2 import cv2
from pynput.keyboard import Key, Controller
from pynput.mouse import Button

import keyboard_detector
import process_ocr
from admin_privileges import running_as_admin
from device_validation import DeviceValidation
from window_capture import WindowCapture

# Disables UserWarning logs that are coming from torchvision.
warnings.filterwarnings("ignore", category=UserWarning)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

registered_devices = ['D8-BB-C1-17-F1-9E', '50-2B-73-CC-02-29', 'B4-2E-99-F3-C3-E7', '30-9C-23-E0-93-1B',
                      '1C-BF-CE-78-C9-EA', '30-9C-23-00-7B-A8', '00-E0-4C-C0-AF-D7', '98-8D-46-DE-EF-09',
                      'B4-2E-99-F3-C6-2E', '2C-F0-5D-6E-A8-BF', '00-E0-4C-B4-07-CF']
device_registration = DeviceValidation(registered_devices)
running_as_admin()

# http://kbdedit.com/manual/low_level_vk_list.html
ENTER = Key.enter
TAB = Key.tab
R = 'r'
Z = 'z'
ZERO = '0'
TWO = '2'
THREE = '3'
FOUR = '4'
FIVE = '5'
SIX = '6'
SEVEN = '7'
EIGHT = '8'
NINE = '9'
ALT = Key.alt_l
X = 'x'
S = 's'
MIDDLE_BUTTON = Button.middle

window_name = "Knight OnLine Client"
wincapture = WindowCapture(window_name)

prev_coordination = None
gm_protection = False

keyboard = Controller()


class CharacterEnum:
    MAGE_GOD = 1
    BP = 2
    WARRIOR = 3
    ASSASSIN = 4
    MAGE_SOFT = 5


def press(code):
    keyboard.press(code)
    sleep(random.uniform(0.03, 0.10))
    keyboard.release(code)


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
        sleep(random.uniform(0.2, 0.4))


def ts_use(ts_for_mage=False):
    sleep(0.5)
    press(ZERO)
    sleep(random.uniform(0.7, 1))

    if ts_for_mage:
        # Death Knight.
        scroll(-4)
        press(TAB)
        scroll(-1)
    else:
        press(TAB)
        sleep(random.uniform(0.3, 0.6))
        # Bulture.
        scroll(-1)
        sleep(random.uniform(0.4, 0.6))

    press(ENTER)
    sleep(random.uniform(0.3, 0.5))
    press(Key.esc)

    sleep(random.uniform(0.3, 0.5))
    press(Key.esc)


def warrior_combo():
    press(TWO)
    press(THREE)

    sleep(random.uniform(0.55, 0.69))
    press(R)
    sleep(random.uniform(0.10, 0.15))
    press(R)


def assassin_combo():
    press(THREE)
    press(FOUR)
    press(FIVE)
    press(SIX)
    press(SEVEN)
    press(EIGHT)

    sleep(random.uniform(0.55, 0.69))
    press(R)
    sleep(random.uniform(0.10, 0.15))
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


def ocr_info_bar(pause_event):
    global prev_coordination

    while True:
        if pause_event.is_set():
            continue

        # 1360, 768.
        screenshot = wincapture.get_screenshot()[70:91, 15:230]

        if screenshot is None:
            sleep(0.5)
            continue

        scaled_img = cv2.resize(screenshot, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
        gray = cv2.cvtColor(scaled_img, cv2.COLOR_BGR2GRAY)
        results = process_ocr.process(gray, debug=False)

        try:
            coordination_format = re.compile(".*,")
            coordination_probabilities = list(filter(coordination_format.match, results))

            pattern = r'([a-zA-Z]+)(\s+)(\d+)(,\d+)'
            result = re.sub(pattern, r'\1\2\3\4', coordination_probabilities[0])
            result_list = result.split()
            coordination = [item for item in result_list if re.search(',', item)]
            coordination = coordination[-1] if coordination else None
            print('Coordination check - ', coordination, ' - at {:%H:%M:%S}'.format(datetime.now()))

            if prev_coordination is not None and coordination != prev_coordination:
                press(S)
                press(X)
                print('...GM detected and program paused at {:%H:%M:%S}...'.format(datetime.now()))

                keyboard.press(Key.alt_gr)
                keyboard.press(Key.ctrl_r)
                keyboard.release(Key.alt_gr)
                keyboard.release(Key.ctrl_r)

                prev_coordination = None
                press(X)
                continue

            prev_coordination = coordination
        except Exception as e:
            print('Error occurred while parsing coordinates. Re-reading...', e)


ts_interval = random.uniform(3600, 3602)
next_ts_use = datetime.now()
next_skill_use = datetime.now()
next_skill_use_timedelta = random.uniform(0.1, 0.2)
mana_interval = random.uniform(54, 56)
next_mana_use_for_mage = datetime.now() + timedelta(seconds=mana_interval)


def run_combo_ts(bot_type, pause_event):
    while True:
        if pause_event.is_set():
            continue

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
    pause_event = threading.Event()

    if gm_protection:
        ocr_thread = Thread(target=ocr_info_bar, args=(pause_event,))
        ocr_thread.start()

    ts_combo_thread = Thread(target=run_combo_ts, args=(bot_type, pause_event))
    ts_combo_thread.start()

    keyboard_detector.KeyboardDetector(pause_event)


# ocr - 1.6.2
# torch 1.10.2
# torchvision 0.11.3

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
            keyboard.press(ALT)

            try:
                hwnd_main = win32gui.FindWindow(None, window_name)
                hwnd_child = win32gui.GetWindow(hwnd_main, win32con.GW_CHILD)
                win32gui.SetForegroundWindow(hwnd_child)
            finally:
                keyboard.release(ALT)

            start()

# pyinstaller --onefile .\main.py --paths C:\Users\undefined\AppData\Local\Programs\Python\Python39\Lib\site-packages --key myKey -n wq
