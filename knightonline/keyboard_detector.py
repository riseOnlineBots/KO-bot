from datetime import datetime

from pynput import keyboard

from colorful_text import text


class KeyboardDetector:
    # The key combination to check
    _COMBINATION = {keyboard.Key.ctrl_r, keyboard.Key.alt_gr}

    # The currently active modifiers.
    _current = set()
    _combination_active = False

    def _on_press(self, key):
        if key in self._COMBINATION:
            if key not in self._current:
                self._current.add(key)

            if self._current == self._COMBINATION:
                if self._combination_active:
                    self._current.clear()

                self._combination_active = not self._combination_active

                if self._combination_active:
                    text('...PROGRAM PAUSED at {:%H:%M:%S}...'.format(datetime.now()))
                else:
                    text('...PROGRAM RESUMED...')

    def _on_release(self, key):
        try:
            self._current.remove(key)
        except KeyError:
            pass

    def start(self):
        # Collect events until released
        listener = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release)
        listener.start()

    def get_combination_active(self):
        return self._combination_active
