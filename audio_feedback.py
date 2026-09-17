import threading
import numpy as np

try:
    import simpleaudio as sa
    _SA_AVAILABLE = True
except Exception:
    _SA_AVAILABLE = False


def _generate_tone(frequency: float, duration: float, sample_rate: int = 44100) -> np.ndarray:
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = np.sin(2 * np.pi * frequency * t)
    # Fade in/out to avoid clicks
    fade_samples = min(int(sample_rate * 0.01), len(tone) // 4)
    fade = np.linspace(0, 1, fade_samples)
    tone[:fade_samples] *= fade
    tone[-fade_samples:] *= fade[::-1]
    return (tone * 32767).astype(np.int16)


def _play_async(frequency: float, duration: float) -> None:
    if not _SA_AVAILABLE:
        return
    try:
        tone = _generate_tone(frequency, duration)
        play_obj = sa.play_buffer(tone, 1, 2, 44100)
        play_obj.wait_done()
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
