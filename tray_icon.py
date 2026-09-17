from __future__ import annotations
from typing import Callable
from PIL import Image, ImageDraw
import pystray


_ICON_SIZE = 64
_COLORS = {
    'idle':       (120, 120, 120, 255),
    'recording':  (210,  40,  40, 255),
    'processing': (220, 170,   0, 255),
}


def _make_icon(state: str) -> Image.Image:
    img = Image.new('RGBA', (_ICON_SIZE, _ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    m = 6
    draw.ellipse([m, m, _ICON_SIZE - m, _ICON_SIZE - m], fill=_COLORS[state])
    # Mic body
    cx, cy = _ICON_SIZE // 2, _ICON_SIZE // 2
    mw, mh = 10, 16
    draw.rounded_rectangle(
        [cx - mw, cy - mh, cx + mw, cy + mh // 2],
        radius=mw,
        fill=(255, 255, 255, 220),
    )
    # Mic stand
    draw.arc([cx - mw - 4, cy - 4, cx + mw + 4, cy + mh], start=0, end=180, fill=(255, 255, 255, 220), width=3)
    draw.line([cx, cy + mh, cx, cy + mh + 6], fill=(255, 255, 255, 220), width=3)
    draw.line([cx - 6, cy + mh + 6, cx + 6, cy + mh + 6], fill=(255, 255, 255, 220), width=3)
    return img


class TrayIcon:
    def __init__(self, on_quit: Callable[[], None]):
        self._on_quit = on_quit
        self._state = 'idle'
        self._icons = {s: _make_icon(s) for s in _COLORS}
        self._icon = pystray.Icon(
            'voicy',
            self._icons['idle'],
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
        self._icon.icon = self._icons[state]
        self._icon.title = f'Voicy — {labels.get(state, state)}'

    def notify(self, message: str) -> None:
        try:
            self._icon.notify(message, 'Voicy')
        except Exception:
            pass

    def run(self) -> None:
        self._icon.run()
