import io
import sys
import threading
import wave

import numpy as np

if sys.platform == 'win32':
    import winsound
else:
    import sounddevice as sd

# Peak volume as a fraction of full scale (1.0 was a sharp, loud beep).
_AMPLITUDE = 0.16


def _generate_tone(frequency: float, duration: float, sample_rate: int = 44100) -> np.ndarray:
    n = int(sample_rate * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    tone = np.sin(2 * np.pi * frequency * t)

    fade_in = min(int(sample_rate * 0.03), n // 3)
    fade_out = min(int(sample_rate * 0.08), n // 2)
    envelope = np.ones(n)
    envelope[:fade_in] = np.linspace(0, 1, fade_in)
    envelope[-fade_out:] = np.linspace(1, 0, fade_out)
    # Decay so the tone eases off instead of sitting at full volume.
    envelope *= np.exp(-3.5 * t / duration)

    peak = float(np.max(np.abs(tone * envelope))) or 1.0
    tone = tone * envelope / peak * _AMPLITUDE
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
    threading.Thread(target=_play_async, args=(660.0, 0.12), daemon=True).start()


def play_stop():
    threading.Thread(target=_play_async, args=(392.0, 0.14), daemon=True).start()


def play_error():
    # Two low beeps — distinct from start/stop
    def _error():
        _play_async(196.0, 0.14)
        import time; time.sleep(0.08)
        _play_async(196.0, 0.14)
    threading.Thread(target=_error, daemon=True).start()
