import threading
import numpy as np
import sounddevice as sd
from config import SAMPLE_RATE, CHANNELS


class Recorder:
    def __init__(self):
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()

    def start(self) -> None:
        with self._lock:
            self._frames = []
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype='float32',
                callback=self._callback,
            )
            self._stream.start()

    def stop(self) -> None:
        with self._lock:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None

    def get_audio(self) -> np.ndarray:
        with self._lock:
            if not self._frames:
                return np.zeros(SAMPLE_RATE, dtype='float32')
            return np.concatenate(self._frames, axis=0).flatten()

    def _callback(self, indata: np.ndarray, frames: int, time, status) -> None:
        with self._lock:
            self._frames.append(indata.copy())
