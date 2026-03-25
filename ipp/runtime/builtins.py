import math
import random
import json


def ipp_print(*args):
    output = []
    for arg in args:
        if arg is None:
            output.append("nil")
        elif isinstance(arg, bool):
            output.append("true" if arg else "false")
        elif isinstance(arg, float):
            if arg.is_integer():
                output.append(str(int(arg)))
            else:
                output.append(str(arg))
        elif isinstance(arg, Vector2):
            output.append(f"vec2({arg.x}, {arg.y})")
        elif isinstance(arg, Vector3):
            output.append(f"vec3({arg.x}, {arg.y}, {arg.z})")
        elif isinstance(arg, Color):
            output.append(f"color({arg.r}, {arg.g}, {arg.b}, {arg.a})")
        elif isinstance(arg, Rect):
            output.append(f"rect({arg.x}, {arg.y}, {arg.width}, {arg.height})")
        elif hasattr(arg, 'elements'):
            output.append(str(arg.elements))
        elif hasattr(arg, 'data'):
            output.append(str(arg))
        elif isinstance(arg, (list, tuple)):
            output.append(str(arg))
        elif hasattr(arg, '__dict__'):
            output.append(str(arg))
        else:
            output.append(str(arg))
    print(" ".join(output))
    return None


def ipp_len(obj):
    if isinstance(obj, (list, tuple, str)):
        return len(obj)
    if hasattr(obj, 'elements'):
        return len(obj.elements)
    if hasattr(obj, 'data'):
        return len(obj.data)
    if hasattr(obj, '__len__'):
        return len(obj)
    raise RuntimeError(f"Cannot get length of {type(obj)}")


def ipp_type(obj):
    if obj is None:
        return "nil"
    if isinstance(obj, bool):
        return "bool"
    if isinstance(obj, int):
        return "number"
    if isinstance(obj, float):
        return "number"
    if isinstance(obj, str):
        return "string"
    if isinstance(obj, (list, tuple)):
        return "list"
    if hasattr(obj, 'elements'):
        return "list"
    if isinstance(obj, dict):
        return "dict"
    if hasattr(obj, 'data'):
        return "dict"
    if isinstance(obj, Vector2):
        return "vec2"
    if isinstance(obj, Vector3):
        return "vec3"
    if isinstance(obj, Color):
        return "color"
    if isinstance(obj, Rect):
        return "rect"
    if callable(obj):
        return "function"
    return "unknown"


def ipp_to_number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def ipp_to_string(value):
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def ipp_to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def ipp_to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def ipp_to_bool(value):
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return len(value) > 0
    if isinstance(value, (list, dict, tuple)):
        return len(value) > 0
    return True


def ipp_abs(n):
    return abs(n)


def ipp_min(*args):
    if not args:
        raise RuntimeError("min requires at least one argument")
    return min(args)


def ipp_max(*args):
    if not args:
        raise RuntimeError("max requires at least one argument")
    return max(args)


def ipp_sum(*args):
    if not args:
        return 0
    total = 0
    for arg in args:
        if hasattr(arg, 'elements'):
            arg = arg.elements
        if isinstance(arg, (list, tuple)):
            total += sum(arg)
        else:
            total += arg
    return total


def ipp_range(start, end=None, step=1):
    if end is None:
        return list(range(start))
    return list(range(start, end, step))


def ipp_random():
    return random.random()


def ipp_randint(min_val, max_val):
    return random.randint(int(min_val), int(max_val))


def ipp_randfloat(min_val, max_val):
    return random.uniform(float(min_val), float(max_val))


def ipp_choice(seq):
    if not seq:
        raise RuntimeError("choice requires non-empty sequence")
    return random.choice(seq)


def ipp_shuffle(seq):
    result = list(seq)
    random.shuffle(result)
    return result


def ipp_round(n):
    return round(n)


def ipp_floor(n):
    return math.floor(n)


def ipp_ceil(n):
    return math.ceil(n)


def ipp_sqrt(n):
    return math.sqrt(n)


def ipp_pow(base, exp):
    return base ** exp


def ipp_sin(n):
    return math.sin(n)


def ipp_cos(n):
    return math.cos(n)


def ipp_tan(n):
    return math.tan(n)


def ipp_log(n, base=math.e):
    if base == math.e:
        return math.log(n)
    return math.log(n, base)


def ipp_log10(n):
    return math.log10(n)


def ipp_degrees(n):
    return math.degrees(n)


def ipp_radians(n):
    return math.radians(n)


def ipp_asin(n):
    return math.asin(n)


def ipp_acos(n):
    return math.acos(n)


def ipp_atan(n):
    return math.atan(n)


def ipp_atan2(y, x):
    return math.atan2(y, x)


def ipp_pi():
    return math.pi


def ipp_e():
    return math.e


def ipp_input(prompt=""):
    return input(prompt)


def ipp_exit(code=0):
    exit(code)


def ipp_assert(condition, message="Assertion failed"):
    if not condition:
        raise RuntimeError(f"Assertion failed: {message}")


def ipp_keys(d):
    if not isinstance(d, dict):
        raise RuntimeError("keys requires a dict")
    return list(d.keys())


def ipp_values(d):
    if not isinstance(d, dict):
        raise RuntimeError("values requires a dict")
    return list(d.values())


def ipp_items(d):
    if not isinstance(d, dict):
        raise RuntimeError("items requires a dict")
    return list(d.items())


def ipp_has_key(d, key):
    return key in d


def ipp_str(s):
    if s is None:
        return "nil"
    if isinstance(s, bool):
        return "true" if s else "false"
    return str(s)


def ipp_int(s, base=10):
    try:
        return int(s, base)
    except (ValueError, TypeError):
        return None


def ipp_float(s):
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def ipp_bool(s):
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    if isinstance(s, (int, float)):
        return s != 0
    if isinstance(s, str):
        return s.lower() in ('true', '1', 'yes', 'on')
    return True


def ipp_split(s, delimiter=" "):
    if not isinstance(s, str):
        raise RuntimeError("split requires a string")
    return s.split(delimiter)


def ipp_join(items, separator=""):
    if hasattr(items, 'elements'):
        items = items.elements
    elif not isinstance(items, (list, tuple)):
        raise RuntimeError("join requires a list")
    return separator.join(str(x) for x in items)


def ipp_upper(s):
    if not isinstance(s, str):
        raise RuntimeError("upper requires a string")
    return s.upper()


def ipp_lower(s):
    if not isinstance(s, str):
        raise RuntimeError("lower requires a string")
    return s.lower()


def ipp_strip(s):
    if not isinstance(s, str):
        raise RuntimeError("strip requires a string")
    return s.strip()


def ipp_replace(s, old, new):
    if not isinstance(s, str):
        raise RuntimeError("replace requires a string")
    return s.replace(old, new)


def ipp_starts_with(s, prefix):
    if not isinstance(s, str):
        raise RuntimeError("starts_with requires a string")
    return s.startswith(prefix)


def ipp_ends_with(s, suffix):
    if not isinstance(s, str):
        raise RuntimeError("ends_with requires a string")
    return s.endswith(suffix)


def ipp_find(s, sub, start=0):
    if not isinstance(s, str):
        raise RuntimeError("find requires a string")
    idx = s.find(sub, start)
    return idx if idx >= 0 else -1


def ipp_split_lines(s):
    if not isinstance(s, str):
        raise RuntimeError("split_lines requires a string")
    return s.splitlines()


def ipp_count(s, sub):
    if not isinstance(s, str):
        raise RuntimeError("count requires a string")
    return s.count(sub)


def ipp_contains(s, sub):
    if not isinstance(s, str):
        raise RuntimeError("contains requires a string")
    return sub in s


def ipp_startswith(s, prefix):
    return ipp_starts_with(s, prefix)


def ipp_endswith(s, suffix):
    return ipp_ends_with(s, suffix)


def ipp_replace_all(s, old, new):
    if not isinstance(s, str):
        raise RuntimeError("replace_all requires a string")
    return s.replace(old, new)


def ipp_substring(s, start, end=None):
    if not isinstance(s, str):
        raise RuntimeError("substring requires a string")
    start = int(start)
    if end is not None:
        end = int(end)
    if end is None:
        return s[start:]
    return s[start:end]


def ipp_index_of(s, sub, start=0):
    return ipp_find(s, sub, start)


def ipp_char_at(s, index):
    if not isinstance(s, str):
        raise RuntimeError("char_at requires a string")
    index = int(index)
    if index < 0 or index >= len(s):
        return ""
    return s[index]


def ipp_ascii(s):
    if not isinstance(s, str) or len(s) == 0:
        return 0
    return ord(s[0])


def ipp_from_ascii(code):
    return chr(int(code))


def ipp_json_parse(json_str):
    import json
    try:
        from ipp.interpreter.interpreter import IppList, IppDict
        data = json.loads(json_str)
        if isinstance(data, dict):
            return IppDict(data)
        elif isinstance(data, list):
            return IppList(data)
        return data
    except Exception as e:
        raise RuntimeError(f"JSON parse error: {e}")


def ipp_json_stringify(obj, indent=None):
    import json
    from ipp.interpreter.interpreter import IppList, IppDict
    def convert(v):
        if isinstance(v, IppDict):
            return {k: convert(v.data[k]) for k in v.data}
        if isinstance(v, IppList):
            return [convert(e) for e in v.elements]
        return v
    try:
        return json.dumps(convert(obj), indent=indent)
    except Exception as e:
        raise RuntimeError(f"JSON stringify error: {e}")


def ipp_regex_match(pattern, text):
    import re
    return bool(re.match(pattern, text))


def ipp_regex_search(pattern, text):
    import re
    match = re.search(pattern, text)
    if match:
        return match.group()
    return ""


def ipp_regex_replace(pattern, text, replacement):
    import re
    return re.sub(pattern, replacement, text)


class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def length_squared(self):
        return self.x * self.x + self.y * self.y
    
    def normalize(self):
        l = self.length()
        if l == 0:
            return Vector2(0, 0)
        return Vector2(self.x / l, self.y / l)
    
    def distance(self, other):
        return (self - other).length()
    
    def distance_squared(self, other):
        return (self - other).length_squared()
    
    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"
    
    def __str__(self):
        return f"Vector2({self.x}, {self.y})"


class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __rmul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __truediv__(self, scalar):
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def length_squared(self):
        return self.x * self.x + self.y * self.y + self.z * self.z
    
    def normalize(self):
        l = self.length()
        if l == 0:
            return Vector3(0, 0, 0)
        return Vector3(self.x / l, self.y / l, self.z / l)
    
    def distance(self, other):
        return (self - other).length()
    
    def distance_squared(self, other):
        return (self - other).length_squared()
    
    def __repr__(self):
        return f"Vector3({self.x}, {self.y}, {self.z})"
    
    def __str__(self):
        return f"Vector3({self.x}, {self.y}, {self.z})"


def ipp_vec2(x=0, y=0):
    return Vector2(x, y)


def ipp_vec3(x=0, y=0, z=0):
    return Vector3(x, y, z)


def ipp_color(r=0, g=0, b=0, a=255):
    return Color(r, g, b, a)


def ipp_rect(x=0, y=0, width=0, height=0):
    return Rect(x, y, width, height)


class Color:
    def __init__(self, r=0, g=0, b=0, a=255):
        self.r = max(0, min(255, int(r)))
        self.g = max(0, min(255, int(g)))
        self.b = max(0, min(255, int(b)))
        self.a = max(0, min(255, int(a)))
    
    def __add__(self, other):
        return Color(self.r + other.r, self.g + other.g, self.b + other.b, self.a + other.a)
    
    def __sub__(self, other):
        return Color(self.r - other.r, self.g - other.g, self.b - other.b, self.a - other.a)
    
    def __mul__(self, scalar):
        return Color(self.r * scalar, self.g * scalar, self.b * scalar, self.a * scalar)
    
    def __rmul__(self, scalar):
        return Color(self.r * scalar, self.g * scalar, self.b * scalar, self.a * scalar)
    
    def lerp(self, other, t):
        return Color(
            self.r + (other.r - self.r) * t,
            self.g + (other.g - self.g) * t,
            self.b + (other.b - self.b) * t,
            self.a + (other.a - self.a) * t
        )
    
    def to_hex(self):
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}{self.a:02x}"
    
    def to_rgb(self):
        return (self.r, self.g, self.b)
    
    def to_rgba(self):
        return (self.r, self.g, self.b, self.a)
    
    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"
    
    def __str__(self):
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"


class Rect:
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    @property
    def left(self):
        return self.x
    
    @property
    def right(self):
        return self.x + self.width
    
    @property
    def top(self):
        return self.y
    
    @property
    def bottom(self):
        return self.y + self.height
    
    @property
    def position(self):
        return Vector2(self.x, self.y)
    
    @property
    def size(self):
        return Vector2(self.width, self.height)
    
    @property
    def center(self):
        return Vector2(self.x + self.width / 2, self.y + self.height / 2)
    
    def contains(self, point):
        return (self.x <= point.x < self.x + self.width and 
                self.y <= point.y < self.y + self.height)
    
    def intersects(self, other):
        return not (self.right < other.left or 
                    self.left > other.right or 
                    self.bottom < other.top or 
                    self.top > other.bottom)
    
    def inflate(self, dx, dy):
        return Rect(self.x - dx, self.y - dy, self.width + 2*dx, self.height + 2*dy)
    
    def __repr__(self):
        return f"Rect({self.x}, {self.y}, {self.width}, {self.height})"
    
    def __str__(self):
        return f"Rect({self.x}, {self.y}, {self.width}, {self.height})"


def ipp_read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Cannot read file: {e}")


def ipp_write_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        raise RuntimeError(f"Cannot write file: {e}")


def ipp_append_file(path, content):
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        raise RuntimeError(f"Cannot append to file: {e}")


def ipp_file_exists(path):
    import os
    return os.path.exists(path)


def ipp_delete_file(path):
    import os
    try:
        os.remove(path)
        return True
    except Exception as e:
        raise RuntimeError(f"Cannot delete file: {e}")


def ipp_list_dir(path="."):
    import os
    try:
        return os.listdir(path)
    except Exception as e:
        raise RuntimeError(f"Cannot list directory: {e}")


def ipp_mkdir(path):
    import os
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        raise RuntimeError(f"Cannot create directory: {e}")


def ipp_time():
    import time
    return time.time()


def ipp_sleep(seconds):
    import time
    time.sleep(seconds)


def ipp_clock():
    import time
    return time.perf_counter()


# Game Dev Math Functions

def ipp_lerp(a, b, t):
    """Linear interpolation between a and b"""
    return a + (b - a) * t


def ipp_clamp(value, min_val, max_val):
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))


def ipp_map_range(value, in_min, in_max, out_min, out_max):
    """Map value from one range to another"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def ipp_distance(x1, y1, x2, y2):
    """Distance between two points"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def ipp_distance_3d(x1, y1, z1, x2, y2, z2):
    """Distance between two 3D points"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def ipp_normalize(x, y):
    """Normalize 2D vector"""
    mag = math.sqrt(x * x + y * y)
    if mag == 0:
        return (0, 0)
    return (x / mag, y / mag)


def ipp_normalize_3d(x, y, z):
    """Normalize 3D vector"""
    mag = math.sqrt(x * x + y * y + z * z)
    if mag == 0:
        return (0, 0, 0)
    return (x / mag, y / mag, z / mag)


def ipp_dot(x1, y1, x2, y2):
    """Dot product of 2D vectors"""
    return x1 * x2 + y1 * y2


def ipp_dot_3d(x1, y1, z1, x2, y2, z2):
    """Dot product of 3D vectors"""
    return x1 * x2 + y1 * y2 + z1 * z2


def ipp_cross(x1, y1, x2, y2):
    """Cross product of 2D vectors (returns z component)"""
    return x1 * y2 - y1 * x2


def ipp_sign(value):
    """Returns -1, 0, or 1 based on sign"""
    if value < 0:
        return -1
    elif value > 0:
        return 1
    return 0


def ipp_smoothstep(edge0, edge1, x):
    """Smoothstep interpolation"""
    t = ipp_clamp((x - edge0) / (edge1 - edge0), 0, 1)
    return t * t * (3 - 2 * t)


def ipp_move_towards(current, target, max_delta):
    """Move current towards target by max_delta"""
    diff = target - current
    if abs(diff) <= max_delta:
        return target
    return current + math.sign(diff) * max_delta


def ipp_angle(x1, y1, x2, y2):
    """Angle between two points in radians"""
    return math.atan2(y2 - y1, x2 - x1)


def ipp_rotate_x(x, y, angle):
    """Rotate point around origin by angle (radians)"""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return x * cos_a - y * sin_a, x * sin_a + y * cos_a


def ipp_deg_to_rad(degrees):
    """Convert degrees to radians"""
    return degrees * math.pi / 180


def ipp_rad_to_deg(radians):
    """Convert radians to degrees"""
    return radians * 180 / math.pi


def ipp_fac(n):
    """Factorial"""
    return math.factorial(n)


def ipp_gcd(a, b):
    """Greatest common divisor"""
    return math.gcd(int(a), int(b))


def ipp_lcm(a, b):
    """Least common multiple"""
    return abs(int(a) * int(b)) // ipp_gcd(a, b)


def ipp_hypot(x, y):
    """Hypotenuse"""
    return math.hypot(x, y)


def ipp_floor_div(a, b):
    """Floor division"""
    return int(a) // int(b)



BUILTINS = {
    "print": ipp_print,
    "len": ipp_len,
    "type": ipp_type,
    "to_number": ipp_to_number,
    "to_string": ipp_to_string,
    "to_int": ipp_to_int,
    "to_float": ipp_to_float,
    "to_bool": ipp_to_bool,
    "str": ipp_str,
    "int": ipp_int,
    "float": ipp_float,
    "bool": ipp_bool,
    "abs": ipp_abs,
    "min": ipp_min,
    "max": ipp_max,
    "sum": ipp_sum,
    "range": ipp_range,
    "random": ipp_random,
    "randint": ipp_randint,
    "randfloat": ipp_randfloat,
    "choice": ipp_choice,
    "shuffle": ipp_shuffle,
    "round": ipp_round,
    "floor": ipp_floor,
    "ceil": ipp_ceil,
    "sqrt": ipp_sqrt,
    "pow": ipp_pow,
    "sin": ipp_sin,
    "cos": ipp_cos,
    "tan": ipp_tan,
    "log": ipp_log,
    "log10": ipp_log10,
    "degrees": ipp_degrees,
    "radians": ipp_radians,
    "asin": ipp_asin,
    "acos": ipp_acos,
    "atan": ipp_atan,
    "atan2": ipp_atan2,
    "pi": ipp_pi,
    "e": ipp_e,
    "input": ipp_input,
    "exit": ipp_exit,
    "assert": ipp_assert,
    "keys": ipp_keys,
    "values": ipp_values,
    "items": ipp_items,
    "has_key": ipp_has_key,
    "read_file": ipp_read_file,
    "write_file": ipp_write_file,
    "append_file": ipp_append_file,
    "file_exists": ipp_file_exists,
    "delete_file": ipp_delete_file,
    "list_dir": ipp_list_dir,
    "mkdir": ipp_mkdir,
    "time": ipp_time,
    "sleep": ipp_sleep,
    "clock": ipp_clock,
    "split": ipp_split,
    "join": ipp_join,
    "upper": ipp_upper,
    "lower": ipp_lower,
    "strip": ipp_strip,
    "replace": ipp_replace,
    "starts_with": ipp_starts_with,
    "ends_with": ipp_ends_with,
    "find": ipp_find,
    "split_lines": ipp_split_lines,
    "count": ipp_count,
    "contains": ipp_contains,
    "startswith": ipp_startswith,
    "endswith": ipp_endswith,
    "replace_all": ipp_replace_all,
    "substring": ipp_substring,
    "index_of": ipp_index_of,
    "char_at": ipp_char_at,
    "ascii": ipp_ascii,
    "from_ascii": ipp_from_ascii,
    "json_parse": ipp_json_parse,
    "json_stringify": ipp_json_stringify,
    "regex_match": ipp_regex_match,
    "regex_search": ipp_regex_search,
    "regex_replace": ipp_regex_replace,
    "vec2": ipp_vec2,
    "vec3": ipp_vec3,
    "color": ipp_color,
    "rect": ipp_rect,
    
    # Game Dev Math
    "lerp": ipp_lerp,
    "clamp": ipp_clamp,
    "map_range": ipp_map_range,
    "distance": ipp_distance,
    "distance_3d": ipp_distance_3d,
    "normalize": ipp_normalize,
    "normalize_3d": ipp_normalize_3d,
    "dot": ipp_dot,
    "dot_3d": ipp_dot_3d,
    "cross": ipp_cross,
    "sign": ipp_sign,
    "smoothstep": ipp_smoothstep,
    "move_towards": ipp_move_towards,
    "angle": ipp_angle,
    "rotate": ipp_rotate_x,
    "deg_to_rad": ipp_deg_to_rad,
    "rad_to_deg": ipp_rad_to_deg,
    "factorial": ipp_fac,
    "gcd": ipp_gcd,
    "lcm": ipp_lcm,
    "hypot": ipp_hypot,
    "floor_div": ipp_floor_div,
}