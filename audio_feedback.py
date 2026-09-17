import io
import sys
import threading
import wave

import numpy as np

if sys.platform == 'win32':
    import winsound
else:
    import sounddevice as sd


def _generate_tone(frequency: float, duration: float, sample_rate: int = 44100) -> np.ndarray:
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = np.sin(2 * np.pi * frequency * t)
    # Fade in/out to avoid clicks
    fade_samples = min(int(sample_rate * 0.01), len(tone) // 4)
    fade = np.linspace(0, 1, fade_samples)
    tone[:fade_samples] *= fade
    tone[-fade_samples:] *= fade[::-1]
    return (tone * 32767).astype(np.int16)


def _play_tone(tone: np.ndarray, sample_rate: int = 44100) -> None:
    if sys.platform == 'win32':
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(tone.tobytes())
        winsound.PlaySound(buf.getvalue(), winsound.SND_MEMORY)
        return

    sd.play(tone.astype(np.float32) / 32768.0, samplerate=sample_rate, blocking=True)


def _play_async(frequency: float, duration: float) -> None:
    try:
        _play_tone(_generate_tone(frequency, duration))
    except Exception:
        pass


def play_start():
    threading.Thread(target=_play_async, args=(880.0, 0.15), daemon=True).start()


def play_stop():
    threading.Thread(target=_play_async, args=(440.0, 0.15), daemon=True).start()


def play_error():
    # Two low beeps — distinct from start/stop
    def _error():
        _play_async(220.0, 0.12)
        import time; time.sleep(0.05)
        _play_async(220.0, 0.12)
    threading.Thread(target=_error, daemon=True).start()
