from datetime import datetime

from pynput import keyboard

from colorful_text import text


class KeyboardDetector:
    # The key combination to check
    _COMBINATION = {keyboard.Key.ctrl_r, keyboard.Key.alt_gr}

    # The currently active modifiers.
    _current = set()
    _combination_active = False

    pause_event = None

    def __init__(self, pause_event):
        self.pause_event = pause_event

        with keyboard.Listener(on_press=self._on_press, on_release=self._on_release) as listener:
            listener.join()

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
                    self.pause_event.set()  # Pauses the thread.
                else:
                    text('...PROGRAM RESUMED...')
                    self.pause_event.clear()  # Resumes the thread.

    def _on_release(self, key):
        try:
            self._current.remove(key)
        except KeyError:
            pass

    def pause_bot(self):
        self._combination_active = True

    def get_combination_active(self):
        return self._combination_active
