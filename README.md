# Voicy — Speech-to-Text Hotkey

A lightweight background app that turns speech into typed text anywhere on your desktop.  
Press **Alt+V** to start recording, press again to stop — the transcribed text is pasted directly into whatever field is focused.

---

## How It Works

```
Alt+V pressed          Alt+V pressed again
     │                       │
     ▼                       ▼
 [RECORDING]  ──────▶  [PROCESSING]  ──────▶  [IDLE]
 Mic captures              Whisper                Text
 audio frames           transcribes            pasted
```

1. **Hotkey listener** (`hotkey_listener.py`) runs in a background thread via `pynput` and watches for `Alt+V` globally — regardless of which app is focused.
2. **Recorder** (`recorder.py`) opens a `sounddevice` input stream and accumulates audio frames into a NumPy buffer at 16 kHz mono (Whisper's native format).
3. On second `Alt+V`, the buffer is handed to the **Transcriber** (`transcriber.py`), which runs `faster-whisper` locally — no internet required. Language is auto-detected (Russian and English work out of the box).
4. The **Text Injector** (`text_injector.py`) saves your current clipboard, copies the transcribed text, simulates `Ctrl+V` (or `Cmd+V` on macOS) to paste it, then restores your original clipboard.
5. The **system tray icon** (`tray_icon.py`) shows the current state and lets you quit cleanly.

All heavy work (transcription + injection) runs in a daemon thread so the UI never freezes.

---

## Requirements

- Python 3.10+
- Windows 10/11 (also works on macOS and Linux with minor caveats — see [Platform Notes](#platform-notes))
- A working microphone

---

## Setup

```bash
# 1. Clone / copy the project folder
cd voicy

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python main.py
```

On **first launch** the Whisper `tiny` model (~75 MB) is downloaded automatically and cached by `faster-whisper`.  
A tray notification confirms the app is ready.

---

## Usage

| Action | What happens |
|--------|-------------|
| **Alt+V** (first press) | Recording starts — short high-pitched beep |
| **Alt+V** (second press) | Recording stops — short low-pitched beep, transcription begins |
| While transcribing | Hotkey is ignored; tray icon turns yellow |
| Transcription succeeds | Text pasted at cursor; tray returns to gray |
| Nothing was said | Double error beep, nothing pasted |

---

## Configuration

Edit `config.py` to change defaults:

```python
HOTKEY      = '<alt>+v'   # Global hotkey combination
MODEL_SIZE  = 'small'      # Whisper model size (see table below)
SAMPLE_RATE = 16000       # Hz — keep at 16000 for Whisper
CHANNELS    = 1           # Mono
LANGUAGE    = None        # None = auto-detect; or e.g. 'ru', 'en'
COMPUTE_TYPE = 'int8'     # Quantisation: 'int8' (fast) or 'float16' (accurate)
DEVICE      = 'cpu'       # Where Whisper runs: 'cpu', 'cuda', or 'auto'
```

`DEVICE` is the Whisper inference device, not the microphone. Use `'cpu'` unless you have an NVIDIA GPU with CUDA set up for CTranslate2; `'cuda'` runs the model on that GPU; `'auto'` picks CUDA when available, otherwise CPU. On CPU keep `COMPUTE_TYPE = 'int8'`.

### Model Size vs. Accuracy

| Model | RAM | Speed | Accuracy |
|-------|-----|-------|----------|
| `tiny` | ~75 MB | fastest | good for short phrases |
| `base` | ~145 MB | fast | better punctuation |
| `small` | ~465 MB | medium | recommended for longer dictation |
| `medium` | ~1.5 GB | slow | near-human accuracy |

---

## Releasing a New Version

Merge changes to `master`. Release Please opens or updates a release PR.
After merging that PR, CI creates the version tag, builds both platforms, and publishes
a GitHub Release automatically.

GitHub Actions builds Windows and macOS binaries in parallel, then attaches
`voicy-<version>.exe` and `voicy-<version>.dmg` to that GitHub Release. Users
download from the **Releases** page — no Python required.

---

## Project Structure

```
voicy/
├── main.py                         Entry point — App class, state machine
├── config.py                       Constants: hotkey, model, sample rate
├── recorder.py                     Mic capture via sounddevice (callback-based)
├── transcriber.py                  faster-whisper model loader + transcribe()
├── text_injector.py                Clipboard save → paste → restore
├── hotkey_listener.py              pynput GlobalHotKeys in daemon thread
├── audio_feedback.py               Sine-wave beeps (winsound on Windows, sounddevice elsewhere)
├── tray_icon.py                    pystray icon with 3 states + quit menu
├── build.spec                      PyInstaller build spec (Win + macOS)
├── runtime_hooks/
│   └── ct2_hook.py                 Fixes ctranslate2 DLL paths in packaged build
├── .github/
│   └── workflows/
│       └── release.yml             CI: builds .exe + .dmg, publishes GitHub Release
└── requirements.txt
```

---

## Platform Notes

### Windows
- Run as **Administrator** if the hotkey doesn't fire in elevated windows (Task Manager, UAC dialogs).

### macOS
- Grant **Accessibility** permission (System Settings → Privacy → Accessibility) for `pynput` to register global hotkeys.
- Grant **Microphone** permission on first run.
- Paste uses `Cmd+V` automatically.

### Linux
- Requires `python3-xlib` or `python3-dev`: `sudo apt install python3-xlib`
- Wayland is **not supported** by `pynput` — use X11 session.
- May need `sudo apt install portaudio19-dev` for `sounddevice`.

---

## Troubleshooting

**Hotkey does nothing**  
→ Check the app is running (tray icon visible). On Windows, try running as admin.

**`No input devices found` error on startup**  
→ Plug in a microphone. Check Windows Sound settings → Recording tab.

**Transcription is empty / error beep**  
→ Spoke too quietly or too briefly. Try speaking closer to the mic, or switch to `base` model in `config.py`.

**Text pasted in wrong place**  
→ Click the target field, then press Alt+V. The injector pastes into whatever window had focus when the hotkey was released the second time.
