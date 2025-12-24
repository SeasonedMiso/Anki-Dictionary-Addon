# -*- coding: utf-8 -*-
# Thanks to Damien Elmes, this plugin is loosely based on his original Plugin and borrows slightly from his project
# Also thanks to the creators of the Japanese Pronunciation/Pitch Accent, Japanese Pitch Accent Notes, and pitch accent note button  which I also borrowed marginally from
#

import sys
from pathlib import Path

# Add libs/ directory to Python path for third-party dependencies
addon_dir = Path(__file__).parent
libs_dir = addon_dir / "libs"
if str(libs_dir) not in sys.path:
    sys.path.insert(0, str(libs_dir))

from . import main
from .src.legacy.utils import ffmpegInstaller, miUpdater, miflix, checkForThirtyTwo