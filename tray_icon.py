from __future__ import annotations
import sys
from pathlib import Path
from typing import Callable

from PIL import Image
import pystray


def _resource_path(relative: str) -> Path:
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent
    return base / relative


def _load_icon() -> Image.Image:
    path = _resource_path('icons/microphone.ico')
    with Image.open(path) as img:
        return img.convert('RGBA')


class TrayIcon:
    def __init__(self, on_quit: Callable[[], None]):
        self._on_quit = on_quit
        self._state = 'idle'
        self._tray_image = _load_icon()
        self._icon = pystray.Icon(
            'voicy',
            self._tray_image,
            'Voicy — Idle',
            menu=self._build_menu(),
        )

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem(lambda _: f'Status: {self._state.capitalize()}', None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Quit', self._quit),
        )

    def _quit(self, icon: pystray.Icon, item) -> None:
        icon.stop()
        self._on_quit()

    def set_state(self, state: str) -> None:
        self._state = state
        labels = {'idle': 'Idle', 'recording': 'Recording...', 'processing': 'Processing...'}
        self._icon.title = f'Voicy — {labels.get(state, state)}'

    def notify(self, message: str) -> None:
        try:
            self._icon.notify(message, 'Voicy')
        except Exception:
            pass

    def run(self) -> None:
        self._icon.run()
