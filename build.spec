import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# ── Data & binaries ───────────────────────────────────────────────────────────
datas = []
datas += collect_data_files('faster_whisper')
datas += collect_data_files('ctranslate2')
datas += collect_data_files('sounddevice')
datas += collect_data_files('tokenizers')
datas += collect_data_files('huggingface_hub')

binaries = []
binaries += collect_dynamic_libs('ctranslate2')
binaries += collect_dynamic_libs('sounddevice')

# ── Platform-specific hidden imports ─────────────────────────────────────────
if sys.platform == 'win32':
    _platform_imports = [
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
        'pynput._util.win32',
        'pynput._util.win32_vk',
        'pystray._win32',
        'pyperclip.backends.windows',
    ]
elif sys.platform == 'darwin':
    _platform_imports = [
        'pynput.keyboard._darwin',
        'pynput.mouse._darwin',
        'pynput._util.darwin',
        'pystray._darwin',
        'pyperclip.backends.pbcopy',
    ]
else:
    _platform_imports = [
        'pynput.keyboard._xorg',
        'pynput.mouse._xorg',
        'pystray._gtk3',
        'pyperclip.backends.xclip',
    ]

hidden_imports = _platform_imports + [
    'sounddevice',
    'soundfile',
    'cffi',
    '_cffi_backend',
    'ctranslate2',
    'faster_whisper',
    'tokenizers',
    'huggingface_hub',
    'huggingface_hub.utils',
    'numpy',
    'numpy.core._methods',
    'numpy.lib.format',
    'pyperclip',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL._imaging',
]

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=['runtime_hooks/ct2_hook.py'],
    excludes=['tkinter', 'matplotlib', 'scipy', 'pandas', 'IPython', 'jupyter'],
    noarchive=False,
)

pyz = PYZ(a.pure)

# ── Windows → single Voicy.exe ────────────────────────────────────────────────
if sys.platform == 'win32':
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        name='Voicy',
        debug=False,
        strip=False,
        upx=False,
        console=False,
        icon=None,
    )

# ── macOS → Voicy.app bundle ──────────────────────────────────────────────────
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='Voicy',
        debug=False,
        strip=False,
        upx=False,
        console=False,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        name='Voicy',
    )
    app = BUNDLE(
        coll,
        name='Voicy.app',
        bundle_identifier='com.voicy.app',
        info_plist={
            'NSMicrophoneUsageDescription': 'Voicy needs microphone access to record speech.',
            'NSPrincipalClass': 'NSApplication',
            'LSUIElement': True,        # hide from Dock (tray-only app)
        },
    )
