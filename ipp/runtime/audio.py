"""
ipp/runtime/audio.py
v2.0.24 — Proper Audio Backend

Provides:
  sound_load(path)       - load a sound file, returns Sound object
  Sound.play(loops, volume, pan) - play the sound
  Sound.stop()           - stop this sound
  Sound.set_volume(lev)  - set this sound's volume
  stop_all_sounds()      - stop all playing sounds
  set_volume(level)      - set global master volume (0.0-1.0)

Cross-platform:
  pygame.mixer (if available, WAV/OGG/MP3)
  Windows winsound fallback (.wav only)
"""

import sys
import os

_HAS_PYGAME = False
try:
    import pygame
    pygame.mixer.init(frequency=22050, size=-16, channels=8, buffer=512)
    _HAS_PYGAME = True
except Exception:
    pass

_master_volume = 0.5
_all_sounds = []


class Sound:
    """Represents a loaded sound that can be played, stopped, and adjusted."""

    __slots__ = ('_path', '_buffer', '_channels', '_volume')

    def __init__(self, path):
        self._path = str(path)
        self._buffer = None
        self._channels = []
        self._volume = 1.0
        if _HAS_PYGAME:
            try:
                self._buffer = pygame.mixer.Sound(self._path)
            except Exception:
                pass
        _all_sounds.append(self)

    def play(self, loops=0, volume=None, pan=0.0):
        """Play the sound.
        loops=0: play once.
        volume=None: use this sound's current volume.
        pan: -1.0 (full left) to 1.0 (full right), 0.0 = center.
        Returns True if playback started, False otherwise.
        """
        if _HAS_PYGAME and self._buffer is not None:
            try:
                vol = (volume if volume is not None else self._volume) * _master_volume
                channel = self._buffer.play(loops=int(loops))
                if channel:
                    if vol != 1.0:
                        channel.set_volume(vol)
                    pan = max(-1.0, min(1.0, float(pan)))
                    if abs(pan) > 0.01:
                        left = vol * min(1.0, 1.0 - pan)
                        right = vol * min(1.0, 1.0 + pan)
                        channel.set_volume(left, right)
                    self._channels.append(channel)
                return True
            except Exception:
                return False
        elif sys.platform == 'win32':
            import winsound
            try:
                flags = winsound.SND_FILENAME | winsound.SND_ASYNC
                winsound.PlaySound(self._path, flags)
                return True
            except Exception:
                return False
        return False

    def stop(self):
        """Stop this sound."""
        if _HAS_PYGAME:
            for ch in self._channels:
                try:
                    ch.stop()
                except Exception:
                    pass
            self._channels = []
        elif sys.platform == 'win32':
            import winsound
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass

    def set_volume(self, level):
        """Set volume for this sound (0.0-1.0)."""
        self._volume = max(0.0, min(1.0, float(level)))
        if _HAS_PYGAME and self._buffer is not None:
            try:
                self._buffer.set_volume(self._volume * _master_volume)
            except Exception:
                pass

    def __del__(self):
        try:
            _all_sounds.remove(self)
        except ValueError:
            pass


def ipp_sound_load(path):
    """Load a sound file and return a Sound object."""
    if not os.path.isfile(str(path)):
        return None
    try:
        return Sound(path)
    except Exception:
        return None


def ipp_stop_all_sounds():
    """Stop all currently playing sounds."""
    for snd in list(_all_sounds):
        try:
            snd.stop()
        except Exception:
            pass


def ipp_set_volume(level):
    """Set global master volume (0.0 = silent, 1.0 = max)."""
    global _master_volume
    _master_volume = max(0.0, min(1.0, float(level)))
    if _HAS_PYGAME:
        try:
            pygame.mixer.music.set_volume(_master_volume)
        except Exception:
            pass
    return _master_volume
