from __future__ import annotations
import threading
from enum import Enum

import sounddevice as sd

import audio_feedback
from recorder import Recorder
from transcriber import Transcriber
from text_injector import TextInjector
from hotkey_listener import HotkeyListener
from tray_icon import TrayIcon


class State(Enum):
    IDLE = 'idle'
    RECORDING = 'recording'
    PROCESSING = 'processing'


class App:
    def __init__(self):
        self._state = State.IDLE
        self._lock = threading.Lock()

        self._check_microphone()

        self._recorder = Recorder()
        self._transcriber = Transcriber()
        self._injector = TextInjector()
        self._tray = TrayIcon(on_quit=self._quit)
        self._hotkey = HotkeyListener(callback=self._on_hotkey)

    def _check_microphone(self) -> None:
        try:
            devices = sd.query_devices()
            inputs = [d for d in devices if d['max_input_channels'] > 0]
            if not inputs:
                raise RuntimeError("No input devices found.")
        except Exception as exc:
            print(f"Microphone error: {exc}")
            # Tray not ready yet; print is best we can do at init time.
            raise

    def _on_hotkey(self) -> None:
        with self._lock:
            if self._state == State.IDLE:
                self._start_recording()
            elif self._state == State.RECORDING:
                self._stop_recording()
            # PROCESSING: ignore

    def _start_recording(self) -> None:
        self._state = State.RECORDING
        self._tray.set_state('recording')
        audio_feedback.play_start()
        self._recorder.start()

    def _stop_recording(self) -> None:
        self._state = State.PROCESSING
        self._tray.set_state('processing')
        self._recorder.stop()
        audio_feedback.play_stop()
        threading.Thread(target=self._process, daemon=True, name='process').start()

    def _process(self) -> None:
        audio = self._recorder.get_audio()
        text = self._transcriber.transcribe(audio)

        if text:
            self._injector.inject(text)
        else:
            audio_feedback.play_error()
            self._tray.notify("Nothing transcribed.")

        with self._lock:
            self._state = State.IDLE
        self._tray.set_state('idle')

    def _quit(self) -> None:
        self._hotkey.stop()

    def run(self) -> None:
        self._hotkey.start_in_thread()
        self._tray.notify("Speech-to-Text ready. Press Alt+V to record.")
        self._tray.run()  # blocks main thread (pystray requirement)


if __name__ == '__main__':
    App().run()
