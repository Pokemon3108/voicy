import numpy as np
from faster_whisper import WhisperModel
from config import MODEL_SIZE, LANGUAGE, COMPUTE_TYPE, DEVICE


class Transcriber:
    def __init__(self):
        print(f"Loading Whisper model '{MODEL_SIZE}' ...")
        self._model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
        print("Whisper model loaded.")

    def transcribe(self, audio: np.ndarray) -> str | None:
        if audio is None or len(audio) == 0:
            return None

        try:
            segments, _info = self._model.transcribe(
                audio,
                language=LANGUAGE,
                beam_size=5,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 300},
            )
            text = " ".join(seg.text.strip() for seg in segments).strip()
            return text if text else None
        except Exception as exc:
            print(f"Transcription error: {exc}")
            return None
