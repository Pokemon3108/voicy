import os
import sys

if hasattr(sys, '_MEIPASS'):
    # Add extraction dir to PATH so ctranslate2 DLLs are found
    meipass = sys._MEIPASS
    os.environ['PATH'] = meipass + os.pathsep + os.environ.get('PATH', '')
    # ctranslate2 looks for its own directory via this env var
    os.environ.setdefault('CT2_LIBRARY_DIR', meipass)
