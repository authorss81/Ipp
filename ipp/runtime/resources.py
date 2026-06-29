import os
import json

_resources = {}

def load_texture(path, key):
    try:
        from ipp.runtime.canvas import ipp_canvas_load_image
        val = ipp_canvas_load_image(path, key)
        _resources[key] = {'type': 'texture', 'path': path, 'value': val,
                            'mtime': os.path.getmtime(path) if os.path.exists(path) else 0}
        return val
    except Exception:
        _resources[key] = {'type': 'texture', 'path': path, 'value': None, 'mtime': 0}
        return None

class _IppSound:
    def __init__(self, sound):
        self._sound = sound
    def play(self):
        if self._sound:
            try:
                self._sound.play()
            except:
                pass
    def stop(self):
        if self._sound:
            try:
                self._sound.stop()
            except:
                pass

def load_sound(path, key):
    try:
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        sound = pygame.mixer.Sound(path)
        val = _IppSound(sound)
    except ImportError:
        val = _IppSound(None)
    except Exception:
        val = _IppSound(None)
    _resources[key] = {'type': 'sound', 'path': path, 'value': val,
                        'mtime': os.path.getmtime(path) if os.path.exists(path) else 0}
    return val

def _parse_tiled_json(data):
    tile_w = data.get('tilewidth', 32)
    tile_h = data.get('tileheight', 32)
    layers = []
    for layer_data in data.get('layers', []):
        if layer_data.get('type') == 'tilelayer':
            h = layer_data['height']
            w = layer_data['width']
            tiles = layer_data['data']
            grid = []
            for row in range(h):
                grid.append(tiles[row * w:(row + 1) * w])
            layers.append({'type': 'tilelayer', 'grid': grid,
                           'width': w, 'height': h})
    return {'tilewidth': tile_w, 'tileheight': tile_h, 'layers': layers}

def load_tilemap(path, key):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        val = _parse_tiled_json(data)
        _resources[key] = {'type': 'tilemap', 'path': path, 'value': val,
                            'mtime': os.path.getmtime(path)}
        return val
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        _resources[key] = {'type': 'tilemap', 'path': path, 'value': None,
                            'mtime': 0}
        return None

def reload_changed():
    for key, res in _resources.items():
        try:
            new_mtime = os.path.getmtime(res['path'])
            if new_mtime != res['mtime']:
                if res['type'] == 'texture':
                    load_texture(res['path'], key)
                elif res['type'] == 'sound':
                    load_sound(res['path'], key)
                elif res['type'] == 'tilemap':
                    load_tilemap(res['path'], key)
        except:
            pass
