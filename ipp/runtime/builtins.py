import math
import random
import json
from ipp.runtime.canvas import (
    ipp_canvas_open, ipp_canvas_rect, ipp_canvas_circle,
    ipp_canvas_line, ipp_canvas_text, ipp_canvas_clear, ipp_canvas_show
)


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
        elif hasattr(arg, 'ipp_class') or hasattr(arg, 'cls'):
            # FIX BUG-N6: call __str__ on user-defined class instances
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
        return "int"
    if isinstance(obj, float):
        return "float"
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
    if hasattr(obj, '_items'):
        return "set"
    if isinstance(obj, Vector2):
        return "vec2"
    if isinstance(obj, Vector3):
        return "vec3"
    if isinstance(obj, Color):
        return "color"
    if isinstance(obj, Rect):
        return "rect"
    if hasattr(obj, 'ipp_class'):
        return "instance"
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
    if hasattr(d, 'data'):
        return list(d.data.keys())
    if isinstance(d, dict):
        return list(d.keys())
    raise RuntimeError("keys requires a dict")


def ipp_values(d):
    if hasattr(d, 'data'):
        return list(d.data.values())
    if isinstance(d, dict):
        return list(d.values())
    raise RuntimeError("values requires a dict")


def ipp_items(d):
    # FIX: Handle IppDict objects
    if hasattr(d, 'items') and callable(d.items):
        return d.items()
    if hasattr(d, 'data'):
        return list(d.data.items())
    if isinstance(d, dict):
        return list(d.items())
    raise RuntimeError("items requires a dict")


def ipp_has_key(d, key):
    # FIX: Handle IppDict objects
    if hasattr(d, 'has'):
        return d.has(key)
    if hasattr(d, 'data'):
        return key in d.data
    return key in d


def ipp_str(s):
    if s is None:
        return "nil"
    if isinstance(s, bool):
        return "true" if s else "false"
    # FIX BUG-N6: str() triggers IppInstance.__str__ which calls user-defined __str__
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


def ipp_regex_match(text, pattern):
    import re
    return bool(re.match(pattern, text))


def ipp_regex_search(text, pattern):
    import re
    match = re.search(pattern, text)
    if match:
        return match.group()
    return ""


def ipp_regex_replace(text, pattern, replacement):
    import re
    return re.sub(pattern, replacement, text)


def ipp_next(generator):
    """Get next value from a generator"""
    from ipp.interpreter.interpreter import IppGenerator
    if isinstance(generator, IppGenerator):
        try:
            return next(generator)
        except StopIteration:
            return None
    elif hasattr(generator, '__next__'):
        try:
            return generator.__next__()
        except StopIteration:
            return None
    else:
        raise RuntimeError(f"Cannot call next() on {type(generator).__name__}")


def ipp_is_generator(obj):
    """Check if an object is a generator"""
    from ipp.interpreter.interpreter import IppGenerator
    return isinstance(obj, IppGenerator)


# Async/Await
def ipp_async_run(coro):
    """Run an async coroutine"""
    from ipp.interpreter.interpreter import IppCoroutine, IppEventLoop, _ipp_get_interpreter
    if isinstance(coro, IppCoroutine):
        interp = _ipp_get_interpreter()
        saved_return = interp.return_value
        loop = IppEventLoop(interp)
        result = loop.run_until_complete(coro)
        # Restore return_value so main execution continues
        interp.return_value = saved_return
        return result
    raise RuntimeError("async_run() expects a coroutine")

def ipp_create_task(coro):
    """Create a task from coroutine"""
    from ipp.interpreter.interpreter import IppCoroutine, IppEventLoop, _ipp_get_interpreter
    if isinstance(coro, IppCoroutine):
        interp = _ipp_get_interpreter()
        saved_return = interp.return_value
        loop = IppEventLoop(interp)
        loop.create_task(coro)
        result = loop.run_until_complete(coro)
        interp.return_value = saved_return
        return result
    raise RuntimeError("create_task() expects a coroutine")

def ipp_is_coroutine(obj):
    """Check if object is a coroutine"""
    from ipp.interpreter.interpreter import IppCoroutine
    return isinstance(obj, IppCoroutine)


# v1.5.0 - Additional Builtins

# Random
def ipp_seed(n):
    import random
    random.seed(int(n))
    return True

def ipp_normal(mu=0.0, sigma=1.0):
    import random
    return random.gauss(float(mu), float(sigma))

# Time
def ipp_now():
    import datetime
    return datetime.datetime.now().isoformat()

def ipp_delta():
    import time
    if not hasattr(ipp_delta, '_last'):
        ipp_delta._last = time.perf_counter()
    now = time.perf_counter()
    delta = now - ipp_delta._last
    ipp_delta._last = now
    return delta

def ipp_format_duration(seconds):
    seconds = float(seconds)
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}m {s}s"
    else:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h}h {m}m {s}s"

# Color
def ipp_from_hex(hex_str):
    hex_str = str(hex_str).lstrip('#')
    if len(hex_str) == 6:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return {"r": r, "g": g, "b": b, "a": 255}
    elif len(hex_str) == 8:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        a = int(hex_str[6:8], 16)
        return {"r": r, "g": g, "b": b, "a": a}
    raise RuntimeError(f"Invalid hex color: {hex_str}")

def ipp_to_hex(r, g, b, a=255):
    r, g, b, a = int(r), int(g), int(b), int(a)
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"

def ipp_blend(c1, c2, t):
    t = float(t)
    if isinstance(c1, dict) and isinstance(c2, dict):
        return {
            "r": int(c1.get("r", 0) * (1-t) + c2.get("r", 0) * t),
            "g": int(c1.get("g", 0) * (1-t) + c2.get("g", 0) * t),
            "b": int(c1.get("b", 0) * (1-t) + c2.get("b", 0) * t),
            "a": int(c1.get("a", 255) * (1-t) + c2.get("a", 255) * t),
        }
    raise RuntimeError("blend() expects color dicts")

def ipp_hsl(h, s, l):
    h, s, l = float(h), float(s), float(l)
    h = h % 360
    s = min(1.0, max(0.0, s))
    l = min(1.0, max(0.0, l))
    c = (1 - abs(2*l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c/2
    if h < 60: r, g, b = c, x, 0
    elif h < 120: r, g, b = x, c, 0
    elif h < 180: r, g, b = 0, c, x
    elif h < 240: r, g, b = 0, x, c
    elif h < 300: r, g, b = x, 0, c
    else: r, g, b = c, 0, x
    return {"r": int((r+m)*255), "g": int((g+m)*255), "b": int((b+m)*255), "a": 255}

# Easing
def ipp_ease_in(t):
    t = float(t)
    return t * t * (3 - 2 * t)

def ipp_ease_out(t):
    t = float(t)
    return t * t * (3 - 2 * t)

def ipp_bounce(t):
    t = float(t)
    if t < 4/11: return (121*t*t)/16
    elif t < 8/11: return (363/40.0*t*t) - (99/10.0*t) + 17/5.0
    elif t < 9/10: return (4356/361.0*t*t) - (35442/1805.0*t) + 16061/1805.0
    else: return (54/5.0*t*t) - (513/25.0*t) + 268/25.0

def ipp_spring(t, damping=0.5):
    import math
    t = float(t)
    return 1 - math.exp(-damping * t) * math.cos(t * 10)

# String
def ipp_read_lines(path):
    with open(str(path), 'r', encoding='utf-8') as f:
        return f.readlines()

def ipp_words(text):
    return str(text).split()

def ipp_truncate(text, max_len=50, suffix="..."):
    text = str(text)
    max_len = int(max_len)
    suffix = str(suffix)
    if len(text) <= max_len:
        return text
    return text[:max_len - len(suffix)] + suffix

def ipp_pad_left(text, width, char=" "):
    return str(text).rjust(int(width), str(char))

def ipp_pad_right(text, width, char=" "):
    return str(text).ljust(int(width), str(char))

# List
def ipp_reverse(lst):
    if hasattr(lst, 'elements'):
        lst.elements.reverse()
        return lst
    if isinstance(lst, list):
        lst.reverse()
        return lst
    raise RuntimeError("reverse() expects a list")

def ipp_binary_search(lst, target):
    items = lst.elements if hasattr(lst, 'elements') else lst
    left, right = 0, len(items) - 1
    while left <= right:
        mid = (left + right) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def ipp_group_by(lst, key_fn_name):
    items = lst.elements if hasattr(lst, 'elements') else lst
    result = {}
    for item in items:
        key = str(item)
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result

def ipp_zip_with(lst1, lst2):
    l1 = lst1.elements if hasattr(lst1, 'elements') else lst1
    l2 = lst2.elements if hasattr(lst2, 'elements') else lst2
    return [[a, b] for a, b in zip(l1, l2)]

# Regex
def ipp_find_all(text, pattern):
    import re
    return re.findall(str(pattern), str(text))

def ipp_sub(text, pattern, replacement):
    import re
    return re.sub(str(pattern), str(replacement), str(text))

def ipp_escape(text):
    import re
    return re.escape(str(text))

# Path
def ipp_glob(pattern):
    import glob
    return glob.glob(str(pattern))

# Grid
def ipp_pathfind(grid, start, end):
    """A* pathfinding on a 2D grid (list of lists)"""
    if hasattr(grid, 'elements'):
        grid = grid.elements
    start, end = tuple(start), tuple(end)
    rows, cols = len(grid), len(grid[0])
    open_set = [start]
    came_from = {}
    g_score = {start: 0}
    f_score = {start: abs(start[0]-end[0]) + abs(start[1]-end[1])}
    
    import heapq
    while open_set:
        current = heapq.heappop([(f_score.get(n, float('inf')), n) for n in open_set])[1]
        open_set.remove(current)
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = current[0]+dr, current[1]+dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 1:
                neighbor = (nr, nc)
                tentative = g_score[current] + 1
                if tentative < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    f_score[neighbor] = tentative + abs(nr-end[0]) + abs(nc-end[1])
                    if neighbor not in open_set:
                        open_set.append(neighbor)
    return []

def ipp_neighbors(grid, row, col):
    if hasattr(grid, 'elements'):
        grid = grid.elements
    rows, cols = len(grid), len(grid[0])
    result = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = row+dr, col+dc
        if 0 <= nr < rows and 0 <= nc < cols:
            result.append((nr, nc))
    return result

def ipp_flood_fill(grid, row, col, target=None):
    if hasattr(grid, 'elements'):
        grid = grid.elements
    rows, cols = len(grid), len(grid[0])
    if target is None:
        target = grid[row][col]
    visited = set()
    stack = [(row, col)]
    while stack:
        r, c = stack.pop()
        if (r, c) in visited:
            continue
        if 0 <= r < rows and 0 <= c < cols and grid[r][c] == target:
            visited.add((r, c))
            stack.extend([(r-1,c),(r+1,c),(r,c-1),(r,c+1)])
    return list(visited)

# Debug
def ipp_assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(f"assert_eq failed: {a!r} != {b!r}" + (f" - {msg}" if msg else ""))

def ipp_inspect(obj):
    if hasattr(obj, '__dict__'):
        return {k: str(v) for k, v in obj.__dict__.items()}
    if hasattr(obj, 'data'):
        return obj.data
    if hasattr(obj, 'elements'):
        return obj.elements
    return str(obj)


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


def ipp_set(items=None):
    from ipp.interpreter.interpreter import IppSet, IppList
    if items is None:
        return IppSet()
    if isinstance(items, IppList):
        return IppSet(items.elements)
    if isinstance(items, list):
        return IppSet(items)
    return IppSet([items])


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
    sign = -1 if diff < 0 else (1 if diff > 0 else 0)
    return current + sign * max_delta


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


# v0.11.0 Standard Library Features

import datetime
import os
import base64 as b64
import hashlib
import csv
import io


class DateTime:
    """DateTime class for date/time operations"""
    def __init__(self, year, month, day, hour=0, minute=0, second=0, microsecond=0):
        self._dt = datetime.datetime(year, month, day, hour, minute, second, microsecond)
    
    def now():
        """Create DateTime with current time"""
        now = datetime.datetime.now()
        return DateTime(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond)
    
    def year(self):
        return self._dt.year
    
    def month(self):
        return self._dt.month
    
    def day(self):
        return self._dt.day
    
    def hour(self):
        return self._dt.hour
    
    def minute(self):
        return self._dt.minute
    
    def second(self):
        return self._dt.second
    
    def weekday(self):
        return self._dt.weekday()
    
    def format(self, fmt):
        """Format datetime using strftime format"""
        return self._dt.strftime(fmt)
    
    def timestamp(self):
        """Return Unix timestamp"""
        return self._dt.timestamp()
    
    def add_days(self, days):
        """Add days to datetime"""
        new_dt = self._dt + datetime.timedelta(days=days)
        return DateTime(new_dt.year, new_dt.month, new_dt.day, new_dt.hour, new_dt.minute, new_dt.second, new_dt.microsecond)
    
    def add_hours(self, hours):
        """Add hours to datetime"""
        new_dt = self._dt + datetime.timedelta(hours=hours)
        return DateTime(new_dt.year, new_dt.month, new_dt.day, new_dt.hour, new_dt.minute, new_dt.second, new_dt.microsecond)
    
    def __str__(self):
        return self._dt.isoformat()
    
    def __repr__(self):
        return f"DateTime({self._dt.year}, {self._dt.month}, {self._dt.day}, {self._dt.hour}, {self._dt.minute}, {self._dt.second})"


def ipp_datetime_now():
    """Create DateTime with current time"""
    return DateTime.now()


def ipp_datetime_create(year, month, day, hour=0, minute=0, second=0):
    """Create DateTime from components"""
    return DateTime(year, month, day, hour, minute, second)


# Path utilities
class Path:
    """Path class for path manipulation"""
    def __init__(self, path):
        self._path = path
    
    def dirname(self):
        """Return directory name"""
        import os
        return os.path.dirname(self._path)
    
    def basename(self):
        """Return base name (filename)"""
        import os
        return os.path.basename(self._path)
    
    def join(self, *parts):
        """Join path parts"""
        import os
        return os.path.join(self._path, *parts)
    
    def exists(self):
        """Check if path exists"""
        import os
        return os.path.exists(self._path)
    
    def is_file(self):
        """Check if path is a file"""
        import os
        return os.path.isfile(self._path)
    
    def is_dir(self):
        """Check if path is a directory"""
        import os
        return os.path.isdir(self._path)
    
    def ext(self):
        """Return file extension"""
        import os
        return os.path.splitext(self._path)[1]
    
    def stem(self):
        """Return filename without extension"""
        import os
        return os.path.splitext(os.path.basename(self._path))[0]
    
    def absolute(self):
        """Return absolute path"""
        import os
        return os.path.abspath(self._path)
    
    def __str__(self):
        return self._path


def ipp_path(path):
    """Create Path object"""
    return Path(path)


def ipp_path_dirname(path):
    """Get directory name of path"""
    import os
    return os.path.dirname(path)


def ipp_path_basename(path):
    """Get base name of path"""
    import os
    return os.path.basename(path)


def ipp_path_join(*parts):
    """Join path parts"""
    import os
    return os.path.join(*parts)


def ipp_path_exists(path):
    """Check if path exists"""
    import os
    return os.path.exists(path)


# Hash functions
def ipp_md5(data):
    """Compute MD5 hash"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.md5(data).hexdigest()


def ipp_sha256(data):
    """Compute SHA256 hash"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def ipp_sha1(data):
    """Compute SHA1 hash"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha1(data).hexdigest()


def ipp_sha512(data):
    """Compute SHA512 hash"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha512(data).hexdigest()


def ipp_hash(data):
    """Compute generic hash"""
    if isinstance(data, str):
        return hash(data)
    if isinstance(data, (int, float)):
        return hash(data)
    return hash(str(data))


# Base64 encoding/decoding
def ipp_base64_encode(data):
    """Encode string to Base64"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return b64.b64encode(data).decode('utf-8')


def ipp_base64_decode(data):
    """Decode Base64 string"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return b64.b64decode(data).decode('utf-8')


def ipp_base64_encode_bytes(data):
    """Encode bytes to Base64"""
    return b64.b64encode(data).decode('utf-8')


def ipp_base64_decode_bytes(data):
    """Decode Base64 to bytes"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return b64.b64decode(data)


# CSV parsing
def ipp_csv_parse(csv_string, delimiter=","):
    """Parse CSV string to list of lists"""
    from ipp.interpreter.interpreter import IppList
    reader = csv.reader(io.StringIO(csv_string), delimiter=delimiter)
    return IppList([IppList(row) for row in reader])


def ipp_csv_parse_dict(csv_string, delimiter=","):
    """Parse CSV string to list of dicts (using first row as headers)"""
    from ipp.interpreter.interpreter import IppList, IppDict
    reader = csv.DictReader(io.StringIO(csv_string), delimiter=delimiter)
    return IppList([IppDict(dict(row)) for row in reader])


def ipp_csv_to_string(data, delimiter=",", headers=None):
    """Convert list of lists/dicts to CSV string"""
    output = io.StringIO()
    if headers:
        writer = csv.DictWriter(output, fieldnames=headers, delimiter=delimiter)
        writer.writeheader()
        for row in data:
            if hasattr(row, 'data'):
                writer.writerow(row.data)
            else:
                writer.writerow(row)
    else:
        writer = csv.writer(output, delimiter=delimiter)
        for row in data:
            if hasattr(row, 'elements'):
                writer.writerow(row.elements)
            else:
                writer.writerow(row)
    return output.getvalue()


# OS utilities
def ipp_os_platform():
    """Get OS platform"""
    return os.name


def ipp_os_getenv(key, default=None):
    """Get environment variable"""
    return os.environ.get(key, default)


def ipp_os_setenv(key, value):
    """Set environment variable"""
    os.environ[key] = value
    return True


def ipp_os_listenv():
    """List all environment variables"""
    from ipp.interpreter.interpreter import IppDict
    return IppDict(dict(os.environ))


def ipp_os_cwd():
    """Get current working directory"""
    return os.getcwd()


def ipp_os_chdir(path):
    """Change working directory"""
    os.chdir(path)
    return True


# Complex numbers
class Complex:
    """Complex number class"""
    def __init__(self, real=0, imag=0):
        self.real = real
        self.imag = imag
    
    def __add__(self, other):
        if isinstance(other, Complex):
            return Complex(self.real + other.real, self.imag + other.imag)
        return Complex(self.real + other, self.imag)
    
    def __sub__(self, other):
        if isinstance(other, Complex):
            return Complex(self.real - other.real, self.imag - other.imag)
        return Complex(self.real - other, self.imag)
    
    def __mul__(self, other):
        if isinstance(other, Complex):
            return Complex(
                self.real * other.real - self.imag * other.imag,
                self.real * other.imag + self.imag * other.real
            )
        return Complex(self.real * other, self.imag * other)
    
    def __truediv__(self, other):
        if isinstance(other, Complex):
            denom = other.real ** 2 + other.imag ** 2
            return Complex(
                (self.real * other.real + self.imag * other.imag) / denom,
                (self.imag * other.real - self.real * other.imag) / denom
            )
        return Complex(self.real / other, self.imag / other)
    
    def __neg__(self):
        return Complex(-self.real, -self.imag)
    
    def __abs__(self):
        return math.sqrt(self.real ** 2 + self.imag ** 2)
    
    def conjugate(self):
        return Complex(self.real, -self.imag)
    
    def abs(self):
        return abs(self)
    
    def __str__(self):
        if self.imag >= 0:
            return f"{self.real}+{self.imag}i"
        return f"{self.real}{self.imag}i"
    
    def __repr__(self):
        return f"Complex({self.real}, {self.imag})"


def ipp_complex(real=0, imag=0):
    """Create Complex number"""
    return Complex(real, imag)


# XML parsing/generation
import xml.etree.ElementTree as ET


def ipp_xml_parse(xml_string):
    """Parse XML string to dict-like structure"""
    from ipp.interpreter.interpreter import IppDict, IppList
    try:
        root = ET.fromstring(xml_string)
        return IppDict(_xml_element_to_dict(root))
    except Exception as e:
        raise RuntimeError(f"XML parse error: {e}")


def _xml_element_to_dict(element):
    """Convert XML element to dict"""
    result = {}
    if element.attrib:
        result["@attributes"] = dict(element.attrib)
    if element.text and element.text.strip():
        if len(element) == 0:
            return element.text
        result["#text"] = element.text
    for child in element:
        child_data = _xml_element_to_dict(child)
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(child_data)
        else:
            result[child.tag] = child_data
    return result


def ipp_xml_to_string(obj, pretty=False):
    """Convert dict to XML string"""
    try:
        indent = "  " if pretty else ""
        return ET.tostring(_dict_to_xml_element(obj), encoding='unicode')
    except Exception as e:
        raise RuntimeError(f"XML stringify error: {e}")


def _dict_to_xml_element(data):
    """Convert dict to XML element"""
    if isinstance(data, str):
        return ET.Element("item", text=data)
    if not isinstance(data, dict):
        return ET.Element("item", text=str(data))
    
    tag = data.get("@tag", "root")
    attrib = data.get("@attributes", {})
    text = data.get("#text", "")
    
    element = ET.Element(tag, attrib if isinstance(attrib, dict) else {})
    if text:
        element.text = str(text)
    
    for key, value in data.items():
        if key not in ("@tag", "@attributes", "#text"):
            if isinstance(value, list):
                for item in value:
                    element.append(_dict_to_xml_element({key: item} if isinstance(item, dict) else item))
            else:
                element.append(_dict_to_xml_element(value))
    return element


# TOML parsing
def ipp_toml_parse(toml_string):
    """Parse TOML string to dict"""
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            raise RuntimeError("toml library not installed (pip install tomli)")
    try:
        import io
        data = tomllib.loads(toml_string)
        return _python_to_ipp(data)
    except Exception as e:
        raise RuntimeError(f"TOML parse error: {e}")


def _python_to_ipp(obj):
    """Convert Python objects to Ipp objects"""
    from ipp.interpreter.interpreter import IppDict, IppList
    if isinstance(obj, dict):
        return IppDict({k: _python_to_ipp(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return IppList([_python_to_ipp(x) for x in obj])
    return obj


def ipp_toml_to_string(obj):
    """Convert dict to TOML string"""
    try:
        import tomllib
    except ImportError:
        try:
            import tomli_w
        except ImportError:
            raise RuntimeError("toml library not installed (pip install tomli tomli-w)")
    try:
        import io
        output = io.StringIO()
        obj = _ipp_to_python(obj)
        for key, value in obj.items():
            output.write(f"{key} = {_python_value_toml(value)}\n")
        return output.getvalue()
    except Exception as e:
        raise RuntimeError(f"TOML stringify error: {e}")


def _ipp_to_python(obj):
    """Convert Ipp objects to Python"""
    from ipp.interpreter.interpreter import IppDict, IppList
    if isinstance(obj, IppDict):
        return {k: _ipp_to_python(v) for k, v in obj.data.items()}
    if isinstance(obj, IppList):
        return [_ipp_to_python(x) for x in obj.elements]
    return obj


def _python_value_toml(value):
    """Format Python value as TOML"""
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, (int, float, bool)):
        return str(value).lower() if isinstance(value, bool) else str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_python_value_toml(x) for x in value) + "]"
    return str(value)


# YAML parsing
def ipp_yaml_parse(yaml_string):
    """Parse YAML string to dict"""
    try:
        import yaml
    except ImportError:
        raise RuntimeError("yaml library not installed (pip install pyyaml)")
    try:
        data = yaml.safe_load(yaml_string)
        return _python_to_ipp(data) if data else IppDict({})
    except Exception as e:
        raise RuntimeError(f"YAML parse error: {e}")


def ipp_yaml_to_string(obj, indent=2):
    """Convert dict to YAML string"""
    try:
        import yaml
    except ImportError:
        raise RuntimeError("yaml library not installed (pip install pyyaml)")
    try:
        obj = _ipp_to_python(obj)
        return yaml.dump(obj, default_flow_style=False, indent=indent)
    except Exception as e:
        raise RuntimeError(f"YAML stringify error: {e}")


# UUID generation
import uuid as uuid_module


def ipp_uuid4():
    """Generate random UUID"""
    return str(uuid_module.uuid4())


def ipp_uuid1():
    """Generate UUID from host ID and time"""
    return str(uuid_module.uuid1())


def ipp_uuid_nil():
    """Generate nil UUID"""
    return str(uuid_module.UUID(int=0))


# URL utilities
import urllib.parse as urlparse


def ipp_url_parse(url_string):
    """Parse URL to components"""
    from ipp.interpreter.interpreter import IppDict
    parsed = urlparse.urlparse(url_string)
    return IppDict({
        "scheme": parsed.scheme,
        "netloc": parsed.netloc,
        "path": parsed.path,
        "params": parsed.params,
        "query": parsed.query,
        "fragment": parsed.fragment
    })


def ipp_url_build(scheme="", netloc="", path="", params="", query="", fragment=""):
    """Build URL from components"""
    return urlparse.urlunparse((scheme, netloc, path, params, query, fragment))


def ipp_url_encode(query, safe=""):
    """URL encode a string"""
    return urlparse.quote(query, safe=safe)


def ipp_url_decode(query):
    """URL decode a string"""
    return urlparse.unquote(query)


def ipp_url_query_parse(query_string):
    """Parse query string to dict"""
    from ipp.interpreter.interpreter import IppDict
    parsed = urlparse.parse_qs(query_string)
    return IppDict({k: v[0] if len(v) == 1 else v for k, v in parsed.items()})


def ipp_url_query_build(params):
    """Build query string from dict"""
    if hasattr(params, 'data'):
        params = params.data
    return urlparse.urlencode(params)


# HTTP utilities
def ipp_http_get(url, headers=None):
    """Make HTTP GET request"""
    from ipp.interpreter.interpreter import IppDict
    try:
        import urllib.request
    except ImportError:
        raise RuntimeError("urllib not available")
    try:
        req = urllib.request.Request(url)
        if headers:
            for k, v in headers.items() if hasattr(headers, 'items') else headers:
                req.add_header(k, v)
        with urllib.request.urlopen(req) as response:
            return IppDict({
                "status": response.getcode(),
                "headers": dict(response.headers),
                "body": response.read().decode('utf-8')
            })
    except Exception as e:
        raise RuntimeError(f"HTTP GET error: {e}")


def ipp_http_post(url, data=None, headers=None):
    """Make HTTP POST request"""
    from ipp.interpreter.interpreter import IppDict
    try:
        import urllib.request
    except ImportError:
        raise RuntimeError("urllib not available")
    try:
        req = urllib.request.Request(url, data=data.encode('utf-8') if data else None, method='POST')
        if headers:
            for k, v in headers.items() if hasattr(headers, 'items') else headers:
                req.add_header(k, v)
        if data:
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        with urllib.request.urlopen(req) as response:
            return IppDict({
                "status": response.getcode(),
                "headers": dict(response.headers),
                "body": response.read().decode('utf-8')
            })
    except Exception as e:
        raise RuntimeError(f"HTTP POST error: {e}")


def ipp_http_put(url, data=None, headers=None):
    """Make HTTP PUT request"""
    from ipp.interpreter.interpreter import IppDict
    try:
        import urllib.request
    except ImportError:
        raise RuntimeError("urllib not available")
    try:
        req = urllib.request.Request(url, data=data.encode('utf-8') if data else None, method='PUT')
        if headers:
            for k, v in headers.items() if hasattr(headers, 'items') else headers:
                req.add_header(k, v)
        if data:
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        with urllib.request.urlopen(req) as response:
            return IppDict({
                "status": response.getcode(),
                "headers": dict(response.headers),
                "body": response.read().decode('utf-8')
            })
    except Exception as e:
        raise RuntimeError(f"HTTP PUT error: {e}")


def ipp_http_delete(url, headers=None):
    """Make HTTP DELETE request"""
    from ipp.interpreter.interpreter import IppDict
    try:
        import urllib.request
    except ImportError:
        raise RuntimeError("urllib not available")
    try:
        req = urllib.request.Request(url, method='DELETE')
        if headers:
            for k, v in headers.items() if hasattr(headers, 'items') else headers:
                req.add_header(k, v)
        with urllib.request.urlopen(req) as response:
            return IppDict({
                "status": response.getcode(),
                "headers": dict(response.headers),
                "body": response.read().decode('utf-8')
            })
    except Exception as e:
        raise RuntimeError(f"HTTP DELETE error: {e}")


def ipp_http_request(url, method='GET', data=None, headers=None):
    """Make generic HTTP request"""
    method = str(method).upper()
    if method == 'GET':
        return ipp_http_get(url, headers)
    elif method == 'POST':
        return ipp_http_post(url, data, headers)
    elif method == 'PUT':
        return ipp_http_put(url, data, headers)
    elif method == 'DELETE':
        return ipp_http_delete(url, headers)
    else:
        raise RuntimeError(f"Unsupported HTTP method: {method}")


# Compression utilities
import gzip
import zipfile
import io


def ipp_gzip_compress(data):
    """Compress data using gzip"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    compressed = gzip.compress(data)
    import base64
    return base64.b64encode(compressed).decode('utf-8')


def ipp_gzip_decompress(data):
    """Decompress gzip data"""
    import base64
    if isinstance(data, str):
        data = data.encode('utf-8')
    decompressed = gzip.decompress(base64.b64decode(data))
    return decompressed.decode('utf-8')


def ipp_zip_create(files):
    """Create ZIP archive from dict of filename->content"""
    import base64
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        if hasattr(files, 'data'):
            files = files.data
        for name, content in files.items():
            if isinstance(content, str):
                content = content.encode('utf-8')
            zf.writestr(name, content)
    return base64.b64encode(output.getvalue()).decode('utf-8')


def ipp_zip_extract(data):
    """Extract ZIP archive to dict"""
    import base64
    if isinstance(data, str):
        data = data.encode('utf-8')
    input_data = io.BytesIO(base64.b64decode(data))
    result = {}
    with zipfile.ZipFile(input_data, 'r') as zf:
        for name in zf.namelist():
            result[name] = zf.read(name).decode('utf-8')
    from ipp.interpreter.interpreter import IppDict
    return IppDict(result)


# Logging utilities
class Logger:
    def __init__(self, name="ipp", level="INFO"):
        import logging
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
    
    def debug(self, msg):
        self.logger.debug(msg)
    
    def info(self, msg):
        self.logger.info(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def error(self, msg):
        self.logger.error(msg)


def ipp_logger(name="ipp", level="INFO"):
    """Create logger"""
    return Logger(name, level)


# Collections utilities
class Deque:
    def __init__(self, items=None):
        from ipp.interpreter.interpreter import IppList
        self._items = list(items.elements) if hasattr(items, 'elements') else list(items) if items else []
    
    def push_front(self, item):
        self._items.insert(0, item)
    
    def push_back(self, item):
        self._items.append(item)
    
    def pop_front(self):
        if not self._items:
            raise RuntimeError("Deque is empty")
        return self._items.pop(0)
    
    def pop_back(self):
        if not self._items:
            raise RuntimeError("Deque is empty")
        return self._items.pop()
    
    def front(self):
        return self._items[0] if self._items else None
    
    def back(self):
        return self._items[-1] if self._items else None
    
    def len(self):
        return len(self._items)
    
    def is_empty(self):
        return len(self._items) == 0
    
    def __str__(self):
        return f"Deque({self._items})"


def ipp_deque(items=None):
    """Create deque"""
    return Deque(items)


def ipp_ordict():
    """Create ordered dict (preserves insertion order)"""
    from ipp.interpreter.interpreter import IppDict
    return IppDict({})


# Argument parsing
def ipp_argparse(args=None, description=""):
    """Simple argument parser"""
    import argparse
    parser = argparse.ArgumentParser(description=description)
    return parser


def ipp_args_add(parser, *args, **kwargs):
    """Add argument to parser"""
    parser.add_argument(*args, **kwargs)


def ipp_args_parse(parser, args=None):
    """Parse arguments"""
    from ipp.interpreter.interpreter import IppDict
    try:
        ns = parser.parse_args(args)
        return IppDict(vars(ns))
    except SystemExit:
        return IppDict({})


# Threading utilities
import threading
import time as time_module


class IppThread:
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        self._thread = None
        self._result = None
        self._error = None
    
    def start(self):
        def wrapper():
            try:
                self._result = self._target(*self._args)
            except Exception as e:
                self._error = e
        self._thread = threading.Thread(target=wrapper)
        self._thread.start()
    
    def join(self):
        if self._thread:
            self._thread.join()
        if self._error:
            raise self._error
        return self._result
    
    def is_alive(self):
        return self._thread and self._thread.is_alive()


def ipp_thread(target, *args):
    """Create and start thread"""
    thread = IppThread(target, *args)
    thread.start()
    return thread


def ipp_thread_sleep(seconds):
    """Sleep for seconds"""
    time_module.sleep(seconds)


def ipp_thread_current():
    """Get current thread name"""
    return threading.current_thread().name


# v1.3.3 SMTP + FTP
class IppSMTPClient:
    def __init__(self, server, port=587, use_tls=True, username=None, password=None):
        import smtplib
        from email.mime.text import MIMEText
        self.server = server
        self.port = port
        self.use_tls = use_tls
        self.username = username
        self.password = password
        self._smtp = None
        self.connected = False
        self._MIMEText = MIMEText
    
    def connect(self):
        import smtplib
        try:
            if self.use_tls:
                self._smtp = smtplib.SMTP(self.server, self.port)
                self._smtp.starttls()
            else:
                self._smtp = smtplib.SMTP(self.server, self.port)
            if self.username and self.password:
                self._smtp.login(self.username, self.password)
            self.connected = True
            return True
        except Exception as e:
            raise RuntimeError(f"SMTP connection failed: {e}")
    
    def disconnect(self):
        if self._smtp and self.connected:
            try:
                self._smtp.quit()
            except Exception:
                pass
            self.connected = False
    
    def send(self, from_addr, to_addrs, subject, body):
        if not self.connected:
            raise RuntimeError("Not connected to SMTP server")
        try:
            if isinstance(to_addrs, str):
                to_addrs = [to_addrs]
            msg = self._MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = from_addr
            msg['To'] = ', '.join(to_addrs)
            self._smtp.sendmail(from_addr, to_addrs, msg.as_string())
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to send email: {e}")


def ipp_smtp_connect(server, port=587, use_tls=True, username=None, password=None):
    client = IppSMTPClient(server, port, use_tls, username, password)
    client.connect()
    return client


def ipp_smtp_disconnect(client):
    if isinstance(client, IppSMTPClient):
        client.disconnect()
    return True


def ipp_smtp_send(client, from_addr, to_addrs, subject, body):
    if isinstance(client, IppSMTPClient):
        return client.send(from_addr, to_addrs, subject, body)
    raise RuntimeError("First argument must be an SMTP client")


class IppFTPClient:
    def __init__(self, host, user, password='', port=21):
        from ftplib import FTP
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self._ftp = None
        self.connected = False
        self._FTP = FTP
    
    def connect(self):
        try:
            self._ftp = self._FTP()
            self._ftp.connect(self.host, self.port)
            self._ftp.login(self.user, self.password)
            self.connected = True
            return True
        except Exception as e:
            raise RuntimeError(f"FTP connection failed: {e}")
    
    def disconnect(self):
        if self._ftp and self.connected:
            try:
                self._ftp.quit()
            except Exception:
                pass
            self.connected = False
    
    def list_files(self, path='.'):
        if not self.connected:
            raise RuntimeError("Not connected to FTP server")
        names = []
        self._ftp.retrlines(f'NLST {path}', names.append)
        return names
    
    def get_file(self, remote_path, local_path):
        if not self.connected:
            raise RuntimeError("Not connected to FTP server")
        with open(local_path, 'wb') as f:
            self._ftp.retrbinary(f'RETR {remote_path}', f.write)
        return True
    
    def put_file(self, local_path, remote_path):
        if not self.connected:
            raise RuntimeError("Not connected to FTP server")
        with open(local_path, 'rb') as f:
            self._ftp.storbinary(f'STOR {remote_path}', f)
        return True


def ipp_ftp_connect(host, user, password='', port=21):
    client = IppFTPClient(host, user, password, port)
    client.connect()
    return client


def ipp_ftp_disconnect(client):
    if isinstance(client, IppFTPClient):
        client.disconnect()
    return True


def ipp_ftp_list(client, path='.'):
    if isinstance(client, IppFTPClient):
        return client.list_files(path)
    raise RuntimeError("First argument must be an FTP client")


def ipp_ftp_get(client, remote_path, local_path):
    if isinstance(client, IppFTPClient):
        return client.get_file(remote_path, local_path)
    raise RuntimeError("First argument must be an FTP client")


def ipp_ftp_put(client, local_path, remote_path):
    if isinstance(client, IppFTPClient):
        return client.put_file(local_path, remote_path)
    raise RuntimeError("First argument must be an FTP client")


# v1.3.8 Networking + Collections
def ipp_http_serve(handler, host="localhost", port=8080):
    """Start a simple HTTP server. handler is a function that takes (method, path, headers, body) and returns (status, headers, body)."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class IppHandler(BaseHTTPRequestHandler):
        def _handle(self, method):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
            headers = dict(self.headers)
            try:
                status, resp_headers, resp_body = handler(method, self.path, headers, body)
                self.send_response(int(status))
                if resp_headers:
                    for k, v in resp_headers.items() if hasattr(resp_headers, 'items') else resp_headers:
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(str(resp_body).encode('utf-8'))
            except Exception as e:
                self.send_error(500, str(e))
        
        def do_GET(self):
            self._handle("GET")
        def do_POST(self):
            self._handle("POST")
        def do_PUT(self):
            self._handle("PUT")
        def do_DELETE(self):
            self._handle("DELETE")
        
        def log_message(self, format, *args):
            pass  # Suppress default logging
    
    server = HTTPServer((str(host), int(port)), IppHandler)
    print(f"Server running on http://{host}:{port}")
    server.serve_forever()
    return True


class IppPriorityQueue:
    """Priority queue using heapq"""
    def __init__(self):
        import heapq
        self._heap = []
        self._counter = 0
        self._heapq = heapq
    
    def push(self, item, priority=0):
        self._heapq.heappush(self._heap, (priority, self._counter, item))
        self._counter += 1
        return True
    
    def pop(self):
        if not self._heap:
            return None
        priority, counter, item = self._heapq.heappop(self._heap)
        return item
    
    def peek(self):
        if not self._heap:
            return None
        return self._heap[0][2]
    
    def is_empty(self):
        return len(self._heap) == 0
    
    def len(self):
        return len(self._heap)
    
    def __repr__(self):
        items = [str(item[2]) for item in sorted(self._heap)]
        return f"PriorityQueue([{', '.join(items)}])"


def ipp_priority_queue():
    """Create a new priority queue"""
    return IppPriorityQueue()


class IppTree:
    """Tree data structure"""
    def __init__(self, value=None, children=None):
        self.value = value
        self.children = children or []
    
    def add_child(self, child):
        if isinstance(child, IppTree):
            self.children.append(child)
        else:
            self.children.append(IppTree(child))
        return True
    
    def remove_child(self, index):
        if 0 <= index < len(self.children):
            return self.children.pop(index)
        return None
    
    def get_child(self, index):
        if 0 <= index < len(self.children):
            return self.children[index]
        return None
    
    def len(self):
        return len(self.children)
    
    def traverse_preorder(self):
        result = [self.value]
        for child in self.children:
            if isinstance(child, IppTree):
                result.extend(child.traverse_preorder())
            else:
                result.append(child)
        return result
    
    def traverse_postorder(self):
        result = []
        for child in self.children:
            if isinstance(child, IppTree):
                result.extend(child.traverse_postorder())
            else:
                result.append(child)
        result.append(self.value)
        return result
    
    def traverse_bfs(self):
        result = []
        queue = [self]
        while queue:
            node = queue.pop(0)
            result.append(node.value)
            for child in node.children:
                if isinstance(child, IppTree):
                    queue.append(child)
                else:
                    queue.append(IppTree(child))
        return result
    
    def find(self, value):
        if self.value == value:
            return True
        for child in self.children:
            if isinstance(child, IppTree):
                if child.find(value):
                    return True
            elif child == value:
                return True
        return False
    
    def depth(self):
        if not self.children:
            return 1
        return 1 + max((child.depth() if isinstance(child, IppTree) else 1) for child in self.children)
    
    def __repr__(self):
        return f"Tree({self.value}, {len(self.children)} children)"


def ipp_tree(value=None):
    """Create a new tree node"""
    return IppTree(value)


class IppGraph:
    """Graph data structure (directed or undirected)"""
    def __init__(self, directed=False):
        self.directed = directed
        self.nodes = {}
        self.edges = []
    
    def add_node(self, node):
        if node not in self.nodes:
            self.nodes[node] = []
        return True
    
    def add_edge(self, from_node, to_node, weight=None):
        self.add_node(from_node)
        self.add_node(to_node)
        self.nodes[from_node].append((to_node, weight))
        if not self.directed:
            self.nodes[to_node].append((from_node, weight))
        self.edges.append((from_node, to_node, weight))
        return True
    
    def remove_node(self, node):
        if node in self.nodes:
            del self.nodes[node]
            for n in self.nodes:
                self.nodes[n] = [(to, w) for to, w in self.nodes[n] if to != node]
            self.edges = [(f, t, w) for f, t, w in self.edges if f != node and t != node]
            return True
        return False
    
    def remove_edge(self, from_node, to_node):
        if from_node in self.nodes:
            self.nodes[from_node] = [(to, w) for to, w in self.nodes[from_node] if to != to_node]
        if not self.directed and to_node in self.nodes:
            self.nodes[to_node] = [(to, w) for to, w in self.nodes[to_node] if to != from_node]
        self.edges = [(f, t, w) for f, t, w in self.edges if not (f == from_node and t == to_node)]
        return True
    
    def get_neighbors(self, node):
        if node in self.nodes:
            return [n for n, w in self.nodes[node]]
        return []
    
    def has_node(self, node):
        return node in self.nodes
    
    def has_edge(self, from_node, to_node):
        if from_node in self.nodes:
            return any(to == to_node for to, w in self.nodes[from_node])
        return False
    
    def node_count(self):
        return len(self.nodes)
    
    def edge_count(self):
        return len(self.edges)
    
    def dfs(self, start):
        visited = set()
        result = []
        stack = [start]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                result.append(node)
                if node in self.nodes:
                    for neighbor, w in reversed(self.nodes[node]):
                        if neighbor not in visited:
                            stack.append(neighbor)
        return result
    
    def bfs(self, start):
        visited = set()
        result = []
        queue = [start]
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                result.append(node)
                if node in self.nodes:
                    for neighbor, w in self.nodes[node]:
                        if neighbor not in visited:
                            queue.append(neighbor)
        return result
    
    def shortest_path(self, start, end):
        import heapq
        if start not in self.nodes or end not in self.nodes:
            return None
        distances = {node: float('inf') for node in self.nodes}
        distances[start] = 0
        previous = {node: None for node in self.nodes}
        pq = [(0, start)]
        visited = set()
        
        while pq:
            dist, current = heapq.heappop(pq)
            if current in visited:
                continue
            visited.add(current)
            if current == end:
                break
            if current in self.nodes:
                for neighbor, weight in self.nodes[current]:
                    if neighbor in visited:
                        continue
                    w = weight if weight is not None else 1
                    new_dist = dist + w
                    if new_dist < distances.get(neighbor, float('inf')):
                        distances[neighbor] = new_dist
                        previous[neighbor] = current
                        heapq.heappush(pq, (new_dist, neighbor))
        
        if distances.get(end, float('inf')) == float('inf'):
            return None
        
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous.get(current)
        path.reverse()
        return path
    
    def __repr__(self):
        return f"Graph({self.node_count()} nodes, {self.edge_count()} edges)"


def ipp_graph(directed=False):
    """Create a new graph"""
    return IppGraph(directed)


# v1.3.8 WebSocket Support
class IppWebSocket:
    """WebSocket client for Ipp language"""
    def __init__(self, url):
        self.url = url
        self._ws = None
        self._connected = False
        self._error = None
        try:
            import websocket
            self._has_websocket = True
            self._websocket = websocket
        except ImportError:
            try:
                import websockets
                self._has_websocket = True
                self._websockets = websockets
                self._use_async = True
            except ImportError:
                self._has_websocket = False
    
    def connect(self):
        if not self._has_websocket:
            raise RuntimeError("WebSocket library not installed. Install with: pip install websocket-client")
        
        try:
            import websocket
            self._ws = websocket.create_connection(self.url)
            self._connected = True
            return True
        except Exception as e:
            self._error = str(e)
            raise RuntimeError(f"WebSocket connection failed: {e}")
    
    def send(self, message):
        if not self._connected:
            raise RuntimeError("WebSocket not connected")
        try:
            import websocket
            if isinstance(message, dict):
                import json
                message = json.dumps(message)
            self._ws.send(str(message))
            return True
        except Exception as e:
            self._error = str(e)
            raise RuntimeError(f"WebSocket send failed: {e}")
    
    def receive(self, timeout=None):
        if not self._connected:
            raise RuntimeError("WebSocket not connected")
        try:
            import websocket
            if timeout is not None:
                self._ws.settimeout(float(timeout))
            data = self._ws.recv()
            return data
        except Exception as e:
            self._error = str(e)
            return None
    
    def receive_json(self, timeout=None):
        data = self.receive(timeout)
        if data is None:
            return None
        try:
            import json
            return json.loads(data)
        except Exception:
            return data
    
    def is_connected(self):
        return self._connected
    
    def close(self):
        if self._connected and self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
            self._connected = False
    
    def __repr__(self):
        return f"<WebSocket url={self.url} connected={self._connected}>"


def ipp_websocket_connect(url):
    """Create and connect a WebSocket client"""
    ws = IppWebSocket(str(url))
    ws.connect()
    return ws


def ipp_websocket_send(ws, message):
    """Send a message via WebSocket"""
    if isinstance(ws, IppWebSocket):
        return ws.send(message)
    raise RuntimeError("First argument must be a WebSocket")


def ipp_websocket_receive(ws, timeout=None):
    """Receive a message via WebSocket"""
    if isinstance(ws, IppWebSocket):
        return ws.receive(timeout)
    raise RuntimeError("First argument must be a WebSocket")


def ipp_websocket_close(ws):
    """Close a WebSocket connection"""
    if isinstance(ws, IppWebSocket):
        ws.close()
        return True
    raise RuntimeError("First argument must be a WebSocket")


# Printf-style formatting FIX: BUG-NEW Standard Library
def ipp_printf(format_str, *args):
    """Print with C-style format string"""
    try:
        print(format_str % args, end='')
    except TypeError:
        print(format_str, end='')
    return None

def ipp_sprintf(format_str, *args):
    """Return formatted string"""
    try:
        return format_str % args
    except TypeError:
        return format_str

def ipp_scanf(format_str):
    """Read formatted input from stdin"""
    import re
    line = input()
    
    # Convert format string to regex
    fmt_pattern = format_str
    fmt_pattern = fmt_pattern.replace('%d', r'(-?\d+)')
    fmt_pattern = fmt_pattern.replace('%f', r'(-?\d+\.?\d*)')
    fmt_pattern = fmt_pattern.replace('%s', r'(\S+)')
    fmt_pattern = fmt_pattern.replace('%%', r'%')
    
    match = re.match(fmt_pattern, line)
    if not match:
        return []
    
    results = []
    for g in match.groups():
        if re.match(r'^-?\d+$', g):
            results.append(int(g))
        elif re.match(r'^-?\d+\.?\d*$', g):
            results.append(float(g))
        else:
            results.append(g)
    return results


BUILTINS = {
    "print": ipp_print,
    "printf": ipp_printf,
    "sprintf": ipp_sprintf,
    "scanf": ipp_scanf,
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
    "set": ipp_set,
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
    "file_read": ipp_read_file,  # Alias FIX: Standard Library
    "write_file": ipp_write_file,
    "file_write": ipp_write_file,  # Alias FIX: Standard Library
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
    
    # v0.11.0 Standard Library
    "datetime": ipp_datetime_now,
    "datetime_create": ipp_datetime_create,
    "path": ipp_path,
    "path_dirname": ipp_path_dirname,
    "path_basename": ipp_path_basename,
    "path_join": ipp_path_join,
    "path_exists": ipp_path_exists,
    "md5": ipp_md5,
    "sha256": ipp_sha256,
    "sha1": ipp_sha1,
    "sha512": ipp_sha512,
    "hash": ipp_hash,
    "base64_encode": ipp_base64_encode,
    "base64_decode": ipp_base64_decode,
    "base64_encode_bytes": ipp_base64_encode_bytes,
    "base64_decode_bytes": ipp_base64_decode_bytes,
    "csv_parse": ipp_csv_parse,
    "csv_parse_dict": ipp_csv_parse_dict,
    "csv_to_string": ipp_csv_to_string,
    "os_platform": ipp_os_platform,
    "env_get": ipp_os_getenv,
    "env_set": ipp_os_setenv,
    "list_env": ipp_os_listenv,
    "os_cwd": ipp_os_cwd,
    "os_chdir": ipp_os_chdir,
    "complex": ipp_complex,
    
    # v0.11.2 Additional Libraries
    "xml_parse": ipp_xml_parse,
    "xml_to_string": ipp_xml_to_string,
    "toml_parse": ipp_toml_parse,
    "toml_to_string": ipp_toml_to_string,
    "yaml_parse": ipp_yaml_parse,
    "yaml_to_string": ipp_yaml_to_string,
    "uuid4": ipp_uuid4,
    "uuid1": ipp_uuid1,
    "uuid_nil": ipp_uuid_nil,
    "url_parse": ipp_url_parse,
    "url_build": ipp_url_build,
    "url_encode": ipp_url_encode,
    "url_decode": ipp_url_decode,
    "url_query_parse": ipp_url_query_parse,
    "url_query_build": ipp_url_query_build,
    "http_get": ipp_http_get,
    "http_post": ipp_http_post,
    
    # v1.3.3 Networking
    "http_put": ipp_http_put,
    "http_delete": ipp_http_delete,
    "http_request": ipp_http_request,
    "smtp_connect": ipp_smtp_connect,
    "smtp_disconnect": ipp_smtp_disconnect,
    "smtp_send": ipp_smtp_send,
    "ftp_connect": ipp_ftp_connect,
    "ftp_disconnect": ipp_ftp_disconnect,
    "ftp_list": ipp_ftp_list,
    "ftp_get": ipp_ftp_get,
    "ftp_put": ipp_ftp_put,
    "gzip_compress": ipp_gzip_compress,
    "gzip_decompress": ipp_gzip_decompress,
    "zip_create": ipp_zip_create,
    "zip_extract": ipp_zip_extract,
    "logger": ipp_logger,
    "deque": ipp_deque,
    "ordict": ipp_ordict,
    "argparse": ipp_argparse,
    "args_add": ipp_args_add,
    "args_parse": ipp_args_parse,
    "thread": ipp_thread,
    "thread_sleep": ipp_thread_sleep,
    "thread_current": ipp_thread_current,
    
    # v1.3.8 Networking + Collections
    "http_serve": ipp_http_serve,
    "websocket_connect": ipp_websocket_connect,
    "websocket_send": ipp_websocket_send,
    "websocket_receive": ipp_websocket_receive,
    "websocket_close": ipp_websocket_close,
    "PriorityQueue": ipp_priority_queue,
    "Tree": ipp_tree,
    "Graph": ipp_graph,
    
    # v1.4.0 Generators
    "next": ipp_next,
    "is_generator": ipp_is_generator,
    
    # v1.4.0 Generators
    "next": ipp_next,
    "is_generator": ipp_is_generator,
    
    # v1.5.0 - Async/Await + Additional Builtins
    "async_run": ipp_async_run,
    "create_task": ipp_create_task,
    "is_coroutine": ipp_is_coroutine,
    "sleep": ipp_sleep,
    "seed": ipp_seed,
    "reverse": ipp_reverse,
    "now": ipp_now,
    "delta": ipp_delta,
    "format_duration": ipp_format_duration,
    "from_hex": ipp_from_hex,
    "to_hex": ipp_to_hex,
    "blend": ipp_blend,
    "hsl": ipp_hsl,
    "ease_in": ipp_ease_in,
    "ease_out": ipp_ease_out,
    "bounce": ipp_bounce,
    "spring": ipp_spring,
    "normal": ipp_normal,
    "read_lines": ipp_read_lines,
    "words": ipp_words,
    "truncate": ipp_truncate,
    "pad_left": ipp_pad_left,
    "pad_right": ipp_pad_right,
    "binary_search": ipp_binary_search,
    "group_by": ipp_group_by,
    "zip_with": ipp_zip_with,
    "find_all": ipp_find_all,
    "sub": ipp_sub,
    "escape": ipp_escape,
    "glob": ipp_glob,
    "pathfind": ipp_pathfind,
    "neighbors": ipp_neighbors,
    "flood_fill": ipp_flood_fill,
    "assert_eq": ipp_assert_eq,
    "inspect": ipp_inspect,
    # Canvas 2D Drawing (v1.5.3a) - Tkinter based
    "canvas_open": ipp_canvas_open,
    "canvas_rect": ipp_canvas_rect,
    "canvas_circle": ipp_canvas_circle,
    "canvas_line": ipp_canvas_line,
    "canvas_text": ipp_canvas_text,
    "canvas_clear": ipp_canvas_clear,
    "canvas_show": ipp_canvas_show,
}