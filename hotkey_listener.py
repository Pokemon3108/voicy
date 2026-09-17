import threading
from typing import Callable
from pynput import keyboard
from config import HOTKEY


class HotkeyListener:
    def __init__(self, callback: Callable[[], None]):
        self._callback = callback
        self._hotkeys: keyboard.GlobalHotKeys | None = None

    def start_in_thread(self) -> None:
        thread = threading.Thread(target=self._run, daemon=True, name='hotkey-listener')
        thread.start()

    def _run(self) -> None:
        self._hotkeys = keyboard.GlobalHotKeys({HOTKEY: self._callback})
        self._hotkeys.start()
        self._hotkeys.join()

    def stop(self) -> None:
        if self._hotkeys is not None:
            self._hotkeys.stop()
