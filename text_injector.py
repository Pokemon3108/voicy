import platform
import time
import pyperclip
from pynput.keyboard import Key, Controller


class TextInjector:
    def __init__(self):
        self._keyboard = Controller()
        self._is_mac = platform.system() == 'Darwin'

    def inject(self, text: str) -> None:
        try:
            old = pyperclip.paste()
        except Exception:
            old = ''

        try:
            pyperclip.copy(text)
            time.sleep(0.05)

            if self._is_mac:
                with self._keyboard.pressed(Key.cmd):
                    self._keyboard.tap('v')
            else:
                with self._keyboard.pressed(Key.ctrl):
                    self._keyboard.tap('v')

            time.sleep(0.15)
        finally:
            try:
                pyperclip.copy(old)
            except Exception:
                pass
