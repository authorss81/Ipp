"""
ipp/runtime/audio.py
v2.3.0 — Audio Playback Support

Provides:
  play_sound(path)       - play a sound file
  stop_sound()           - stop currently playing sound
  set_volume(level)      - set volume 0.0-1.0

Cross-platform:
  Windows → winsound (built-in, .wav only)
  Optional → pygame.mixer (if available, broader format support)
"""

import sys
import os

# Try optional audio backends
_HAS_PYGAME = False
try:
    import pygame
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    _HAS_PYGAME = True
except Exception:
    pass

# State
_current_sound = None
_volume = 0.5
_pygame_channel = None


def _play_winsound(path):
    import winsound
    flags = winsound.SND_FILENAME | winsound.SND_ASYNC
    winsound.PlaySound(str(path), flags)


def _play_pygame(path):
    global _current_sound, _pygame_channel
    _stop_pygame()
    try:
        snd = pygame.mixer.Sound(str(path))
        snd.set_volume(_volume)
        _pygame_channel = snd.play()
        _current_sound = snd
    except Exception:
        pass


def _stop_winsound():
    import winsound
    winsound.PlaySound(None, winsound.SND_PURGE)


def _stop_pygame():
    global _current_sound, _pygame_channel
    if _pygame_channel is not None:
        try:
            _pygame_channel.stop()
        except Exception:
            pass
        _pygame_channel = None
    _current_sound = None


def ipp_play_sound(path: str) -> str:
    """Play a sound file. Supports .wav (built-in), more formats with pygame."""
    if not os.path.isfile(str(path)):
        return f"[sound error: file not found: {path}]"
    try:
        if _HAS_PYGAME:
            _play_pygame(path)
        elif sys.platform == 'win32':
            _play_winsound(path)
        else:
            return "[sound error: no audio backend available]"
        return "[sound playing]"
    except Exception as e:
        return f"[sound error: {e}]"


def ipp_stop_sound() -> str:
    """Stop the currently playing sound."""
    try:
        if _HAS_PYGAME:
            _stop_pygame()
        elif sys.platform == 'win32':
            _stop_winsound()
        return "[sound stopped]"
    except Exception as e:
        return f"[sound error: {e}]"


def ipp_set_volume(level: float) -> str:
    """Set volume level (0.0 = silent, 1.0 = max)."""
    global _volume
    _volume = max(0.0, min(1.0, float(level)))
    if _HAS_PYGAME and _current_sound is not None:
        try:
            _current_sound.set_volume(_volume)
        except Exception:
            pass
    return f"[volume set to {_volume}]"
