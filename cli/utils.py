"""CLI utilities for NetLab."""

import platform
import sys


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system().lower() == "windows"


def safe_emoji(emoji: str, fallback: str) -> str:
    """Return emoji or fallback text for Windows compatibility."""
    if is_windows():
        return fallback
    return emoji


def setup_console_encoding() -> None:
    """Set up console encoding for Unicode support on Windows."""
    if is_windows():
        # Try to enable UTF-8 mode on Windows
        try:
            # This helps with Unicode support in Windows console
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except (AttributeError, OSError):
            # Fallback for older Python versions or restricted environments
            pass