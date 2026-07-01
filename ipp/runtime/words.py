"""
ipp/runtime/words.py — Shared keyword & builtin name sets.
Single source of truth for highlighting, completion, and REPL.
"""

KEYWORDS = frozenset({
    'var', 'let', 'const', 'func', 'class', 'if', 'elif', 'else',
    'for', 'while', 'do', 'until', 'repeat', 'return', 'break', 'continue',
    'import', 'from', 'as', 'in', 'try', 'catch', 'throw', 'finally',
    'match', 'case', 'default', 'async', 'await', 'yield',
    'extends', 'super', 'self', 'this', 'new', 'not', 'and', 'or', 'is',
    'enum', 'interface', 'implements', 'static',
    'pub', 'priv', 'mut', 'ref', 'defer', 'with', 'pass', 'del',
    'nil', 'true', 'false', 'with', 'export',
})

ATOMS = frozenset({'nil', 'true', 'false'})

BUILTIN_NAMES = frozenset({
    'print', 'len', 'type', 'range', 'abs', 'min', 'max', 'sum', 'round',
    'floor', 'ceil', 'sqrt', 'pow', 'sin', 'cos', 'tan', 'log', 'input',
    'str', 'int', 'float', 'bool', 'randint', 'random', 'keys', 'values',
    'items', 'contains', 'split', 'join', 'upper', 'lower', 'strip',
    'replace', 'find', 'starts_with', 'ends_with', 'assert', 'exit',
    'list', 'dict', 'set', 'tuple', 'sorted', 'reversed', 'enumerate',
    'zip', 'map', 'filter', 'chr', 'ord', 'hex', 'bin', 'oct', 'repr',
    'hash', 'id', 'dir', 'vars', 'callable', 'hasattr', 'getattr',
    'setattr', 'isinstance', 'issubclass', 'iter', 'next', 'open',
    'divmod', 'all', 'any', 'slice', 'eval',
    'ipp_type', 'ipp_version', 'strip_ansi', 'json_parse',
    'json_stringify', 'base64_encode', 'base64_decode',
    'key_pressed', 'get_key', 'get_key_async', 'on_keydown',
    'on_keyup', 'advance_frame', 'simulate_key_press',
    'simulate_key_release', 'KEY',
    'vec2', 'vec3', 'vec4', 'mat4', 'quat', 'complex', 'Color',
    'Rect', 'Vector2', 'Vector3', 'Signal', 'deque', 'datetime',
    'atan2', 'exp', 'pi', 'tau', 'inf', 'choice', 'shuffle', 'seed',
    'async_run', 'format', 'sprintf',
    'canvas', 'scene', 'node', 'camera', 'mesh', 'light',
    'http_get', 'http_post', 'logger',
    'key_down', 'key_up', 'key_name',
    'file_read', 'file_write', 'file_append', 'file_delete', 'file_exists',
    'gpu_init', 'gpu_close', 'gpu_is_open', 'gpu_size',
    'audio_load', 'audio_play', 'audio_stop', 'audio_volume',
    'isclose', 'trunc', 'lerp', 'clamp', 'map_range',
})

TYPENAMES = frozenset({
    'Number', 'String', 'Bool', 'List', 'Dict', 'Set', 'Func',
    'Class', 'Object', 'Vector2', 'Vector3', 'Vector4', 'Matrix4',
    'Quaternion', 'Color', 'Rect', 'Complex', 'Signal',
    'Error', 'TypeError', 'ValueError', 'IndexError', 'KeyError',
    'RuntimeError', 'ZeroDivisionError',
})
