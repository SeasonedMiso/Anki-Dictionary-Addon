# -*- coding: utf-8 -*-
"""
Platform detection utilities.
"""

import sys
import platform as _platform


def is_mac() -> bool:
    """Check if running on macOS."""
    return sys.platform == "darwin"


def is_win() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def is_lin() -> bool:
    """Check if running on Linux."""
    return sys.platform.startswith("linux")


def get_platform_name() -> str:
    """Get the platform name."""
    return _platform.system()


def get_platform_version() -> str:
    """Get the platform version."""
    return _platform.release()
