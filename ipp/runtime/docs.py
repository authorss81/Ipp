"""Builtin documentation database — syntax, description, examples, returns."""

BUILTIN_DOCS = {}

def _doc(name, *, syntax="", desc="", example="", returns="", note=""):
    BUILTIN_DOCS[name] = {
        "syntax": syntax,
        "desc": desc,
        "example": example,
        "returns": returns,
        "note": note,
    }


_doc("print",
    syntax="print(value, ..., sep=' ')",
    desc="Print one or more values to stdout, separated by sep, followed by a newline.",
    example='print("Hello, World!")\nprint(1, 2, 3)\nprint("a", "b", sep="-")',
    returns="nil")

_doc("input",
    syntax="input(prompt='')",
    desc="Read a line from stdin, with optional prompt string.",
    example='var name = input("Enter name: ")',
    returns="string")

_doc("len",
    syntax="len(obj)",
    desc="Return the length of a string, list, dict, tuple, set, or other collection.",
    example='len("hello")     -> 5\nlen([1,2,3])     -> 3\nlen({"a":1})      -> 1',
    returns="number")

_doc("type",
    syntax="type(value)",
    desc="Return the type name of a value as a string (e.g. 'number', 'string', 'list', 'dict', 'bool', 'nil', 'function', 'class', 'tuple', 'set', 'generator').",
    example='type(42)          -> "number"\ntype("hi")        -> "string"\ntype([1,2])       -> "list"',
    returns="string")

_doc("str",
    syntax="str(value)",
    desc="Convert a value to its string representation.",
    example='str(42)           -> "42"\nstr(true)         -> "true"\nstr([1,2,3])      -> "[1, 2, 3]"',
    returns="string")

_doc("int",
    syntax="int(value, base=10)",
    desc="Convert a value to an integer. Supports string parsing with optional base (2, 8, 10, 16).",
    example='int(3.14)         -> 3\nint("42")         -> 42\nint("FF", 16)     -> 255',
    returns="number")

_doc("float",
    syntax="float(value)",
    desc="Convert a value to a floating-point number.",
    example='float(42)         -> 42.0\nfloat("3.14")     -> 3.14',
    returns="number")

_doc("bool",
    syntax="bool(value)",
    desc="Convert a value to a boolean. nil and false are falsy; all other values are truthy.",
    example='bool(1)           -> true\nbool(0)           -> true\nbool(nil)         -> false\nbool("")          -> true',
    returns="bool")

_doc("abs",
    syntax="abs(x)",
    desc="Return the absolute value of a number.",
    example='abs(-5)          -> 5\nabs(3.14)         -> 3.14',
    returns="number")

_doc("sqrt",
    syntax="sqrt(x)",
    desc="Return the square root of a number. For negative input, returns nil (may also throw).",
    example='sqrt(16)         -> 4.0\nsqrt(2)          -> 1.414...',
    returns="number")

_doc("min",
    syntax="min(a, b, ...)",
    desc="Return the smallest value among the arguments.",
    example='min(3, 7)        -> 3\nmin(10, 5, 8)    -> 5',
    returns="number")

_doc("max",
    syntax="max(a, b, ...)",
    desc="Return the largest value among the arguments.",
    example='max(3, 7)        -> 7\nmax(10, 5, 8)    -> 10',
    returns="number")

_doc("floor",
    syntax="floor(x)",
    desc="Return the largest integer less than or equal to x.",
    example='floor(3.7)       -> 3\nfloor(-1.5)      -> -2',
    returns="number")

_doc("ceil",
    syntax="ceil(x)",
    desc="Return the smallest integer greater than or equal to x.",
    example='ceil(3.2)        -> 4\nceil(-1.5)       -> -1',
    returns="number")

_doc("round",
    syntax="round(x, ndigits=0)",
    desc="Round x to ndigits decimal places.",
    example='round(3.14159)   -> 3\nround(3.14159, 2) -> 3.14',
    returns="number")

_doc("pow",
    syntax="pow(x, y)",
    desc="Return x raised to the power y. Same as x ** y.",
    example='pow(2, 10)       -> 1024\npow(5, 3)        -> 125',
    returns="number")

_doc("trunc",
    syntax="trunc(x)",
    desc="Truncate x toward zero, removing the fractional part.",
    example='trunc(3.7)       -> 3\ntrunc(-3.7)      -> -3',
    returns="number")

_doc("random",
    syntax="random()",
    desc="Return a random float in [0.0, 1.0).",
    example='var r = random()     -> 0.374...',
    returns="number")

_doc("randint",
    syntax="randint(low, high)",
    desc="Return a random integer in [low, high] (inclusive).",
    example='var d = randint(1, 6)  -> 4',
    returns="number")

_doc("seed",
    syntax="seed(value)",
    desc="Initialize the random number generator with a specific seed for reproducible results.",
    example='seed(42)\nrandint(1, 100)  -> deterministic',
    returns="nil")

_doc("range",
    syntax="range(end)\nrange(start, end)\nrange(start, end, step)",
    desc="Create a lazy iterable range of numbers. Step defaults to 1; start defaults to 0.",
    example='range(5)           -> 0,1,2,3,4\nrange(1,5)         -> 1,2,3,4\nrange(0,10,2)      -> 0,2,4,6,8',
    returns="range")

_doc("map",
    syntax="map(fn, iterable)",
    desc="Create a new list by applying fn to each element.",
    example='map(func(x) => x*2, [1,2,3])  -> [2, 4, 6]',
    returns="list")

_doc("filter",
    syntax="filter(fn, iterable)",
    desc="Create a new list with elements where fn returns true.",
    example='filter(func(x) => x > 2, [1,2,3,4])  -> [3, 4]',
    returns="list")

_doc("reduce",
    syntax="reduce(fn, iterable, initial=nil)",
    desc="Accumulate elements left-to-right using fn(acc, elem) => new_acc.",
    example='reduce(func(a,b) => a+b, [1,2,3,4,5])  -> 15',
    returns="any")

_doc("sorted",
    syntax="sorted(iterable, key=nil, reverse=false)",
    desc="Return a new sorted list from the elements of iterable.",
    example='sorted([3,1,4,1,5])  -> [1, 1, 3, 4, 5]',
    returns="list")

_doc("zip",
    syntax="zip(a, b, ...)",
    desc="Aggregate elements from multiple iterables into a list of tuples.",
    example='zip([1,2,3], ["a","b","c"])  -> [(1,"a"), (2,"b"), (3,"c")]',
    returns="list")

_doc("enumerate",
    syntax="enumerate(iterable, start=0)",
    desc="Pair each element with its index as (index, value) tuples.",
    example='enumerate(["a","b","c"])  -> [(0,"a"), (1,"b"), (2,"c")]',
    returns="list")

_doc("sum",
    syntax="sum(iterable, start=0)",
    desc="Sum all elements of an iterable.",
    example='sum([1,2,3,4,5])  -> 15',
    returns="number")

_doc("all",
    syntax="all(iterable)",
    desc="Return true if all elements of the iterable are truthy.",
    example='all([true, true])   -> true\nall([true, false]) -> false',
    returns="bool")

_doc("any",
    syntax="any(iterable)",
    desc="Return true if any element of the iterable is truthy.",
    example='any([false, true])  -> true\nany([false, false]) -> false',
    returns="bool")

_doc("assert",
    syntax="assert(condition, message='')",
    desc="If condition is false, throw an error with optional message. Used for testing.",
    example='assert(2+2 == 4)\nassert(2+2 == 5, "math is broken")',
    returns="nil")

_doc("exit",
    syntax="exit(code=0)",
    desc="Exit the program with the given status code (0 = success).",
    example='exit(0)\nexit(1)  # indicates error',
    returns="never (exits)")

_doc("sleep",
    syntax="sleep(seconds)",
    desc="Pause execution for the specified number of seconds.",
    example='sleep(0.5)  # pause 500ms\nsleep(1)    # pause 1 second',
    returns="nil")

_doc("time",
    syntax="time()",
    desc="Return the current Unix timestamp (seconds since epoch) as a float.",
    example='var t = time()\nprint(t)  -> 1782701547...',
    returns="number")

_doc("now",
    syntax="now()",
    desc="Return the current local date/time as a formatted string.",
    example='print(now())  -> "2026-06-29T08:22:27"',
    returns="string")

_doc("sin",
    syntax="sin(radians)",
    desc="Return the sine of an angle in radians.",
    example='sin(0)    -> 0.0\nsin(pi/2) -> 1.0',
    returns="number")

_doc("cos",
    syntax="cos(radians)",
    desc="Return the cosine of an angle in radians.",
    example='cos(0)    -> 1.0\ncos(pi)   -> -1.0',
    returns="number")

_doc("tan",
    syntax="tan(radians)",
    desc="Return the tangent of an angle in radians.",
    example='tan(0)    -> 0.0\ntan(pi/4) -> 0.999...',
    returns="number")

_doc("asin",
    syntax="asin(x)",
    desc="Return the arc sine of x in radians (inverse of sin).",
    example='asin(0) -> 0.0\nasin(1) -> 1.5708',
    returns="number")

_doc("acos",
    syntax="acos(x)",
    desc="Return the arc cosine of x in radians (inverse of cos).",
    example='acos(1) -> 0.0\nacos(0) -> 1.5708',
    returns="number")

_doc("atan",
    syntax="atan(x)",
    desc="Return the arc tangent of x in radians (inverse of tan).",
    example='atan(0) -> 0.0\natan(1) -> 0.7854',
    returns="number")

_doc("atan2",
    syntax="atan2(y, x)",
    desc="Return the arc tangent of y/x, using the signs of both to determine the quadrant.",
    example='atan2(1, 0) -> 1.5708\natan2(0, 1) -> 0.0',
    returns="number")

_doc("degrees",
    syntax="degrees(radians)",
    desc="Convert an angle from radians to degrees.",
    example='degrees(pi)    -> 180.0\ndegrees(pi/2)  -> 90.0',
    returns="number")

_doc("radians",
    syntax="radians(degrees)",
    desc="Convert an angle from degrees to radians.",
    example='radians(180)   -> 3.14159...\nradians(90)    -> 1.5708...',
    returns="number")

_doc("pi",
    syntax="pi",
    desc="The mathematical constant pi (3.14159...). Use as a variable, not a function call.",
    example='print(pi)          -> 3.14159\nprint(2 * pi)        -> 6.28318\nprint(pi * r * r)    -> circle area',
    returns="number")

_doc("e",
    syntax="e",
    desc="The mathematical constant e (2.71828...). Use as a variable.",
    example='print(e)           -> 2.71828\nprint(log(e))        -> 1.0',
    returns="number")

_doc("log",
    syntax="log(x, base=e)",
    desc="Return the logarithm of x to the given base (defaults to natural log).",
    example='log(e)      -> 1.0\nlog(100, 10) -> 2.0',
    returns="number")

_doc("log10",
    syntax="log10(x)",
    desc="Return the base-10 logarithm of x.",
    example='log10(100)  -> 2.0\nlog10(1000) -> 3.0',
    returns="number")

_doc("hypot",
    syntax="hypot(x, y)",
    desc="Return sqrt(x*x + y*y) — the Euclidean distance from origin.",
    example='hypot(3, 4) -> 5.0\nhypot(5, 12) -> 13.0',
    returns="number")

_doc("factorial",
    syntax="factorial(n)",
    desc="Return n! (n factorial) for non-negative integers.",
    example='factorial(5)  -> 120\nfactorial(10) -> 3628800',
    returns="number")

_doc("gcd",
    syntax="gcd(a, b)",
    desc="Return the greatest common divisor of a and b.",
    example='gcd(12, 8)  -> 4\ngcd(100, 75) -> 25',
    returns="number")

_doc("lcm",
    syntax="lcm(a, b)",
    desc="Return the least common multiple of a and b.",
    example='lcm(4, 6)   -> 12\nlcm(12, 18) -> 36',
    returns="number")

_doc("sign",
    syntax="sign(x)",
    desc="Return 1 for positive numbers, -1 for negative, 0 for zero.",
    example='sign(5)    -> 1\nsign(-3)   -> -1\nsign(0)    -> 0',
    returns="number")

_doc("clamp",
    syntax="clamp(x, min_val, max_val)",
    desc="Constrain x to the range [min_val, max_val].",
    example='clamp(5, 0, 10)   -> 5\nclamp(15, 0, 10)  -> 10\nclamp(-5, 0, 10)  -> 0',
    returns="number")

_doc("lerp",
    syntax="lerp(a, b, t)",
    desc="Linearly interpolate between a and b by t (0 = a, 1 = b).",
    example='lerp(0, 10, 0.5)  -> 5.0\nlerp(0, 100, 0.25) -> 25.0',
    returns="number")

_doc("map_range",
    syntax="map_range(value, in_min, in_max, out_min, out_max)",
    desc="Re-map a value from one range to another.",
    example='map_range(0.5, 0, 1, 0, 100)  -> 50.0\nmap_range(0, 0, 1, 0, 100)    -> 0.0',
    returns="number")

_doc("isclose",
    syntax="isclose(a, b, rel_tol=1e-9, abs_tol=0.0)",
    desc="Return true if a and b are approximately equal within tolerances.",
    example='isclose(0.1+0.2, 0.3)  -> true',
    returns="bool")

_doc("upper",
    syntax="upper(s)",
    desc="Return a copy of the string converted to uppercase.",
    example='upper("hello")  -> "HELLO"',
    returns="string")

_doc("lower",
    syntax="lower(s)",
    desc="Return a copy of the string converted to lowercase.",
    example='lower("HELLO")  -> "hello"',
    returns="string")

_doc("strip",
    syntax="strip(s)",
    desc="Return a copy of the string with leading and trailing whitespace removed.",
    example='strip("  hello  ")  -> "hello"',
    returns="string")

_doc("split",
    syntax="split(s, sep=' ')",
    desc="Split a string into a list of substrings separated by sep.",
    example='split("a b c")       -> ["a", "b", "c"]\nsplit("a,b,c", ",") -> ["a", "b", "c"]',
    returns="list")

_doc("join",
    syntax="join(sep, parts)",
    desc="Join a list of strings with sep as the separator.",
    example='join(", ", ["a","b","c"])  -> "a, b, c"',
    returns="string")

_doc("replace",
    syntax="replace(s, old, new)",
    desc="Return a copy of s with all occurrences of old replaced by new.",
    example='replace("hello world", "world", "ipp")  -> "hello ipp"',
    returns="string")

_doc("find",
    syntax="find(s, sub)",
    desc="Return the index of the first occurrence of sub in s, or -1 if not found.",
    example='find("hello", "l")   -> 2\nfind("hello", "z")   -> -1',
    returns="number")

_doc("starts_with",
    syntax="starts_with(s, prefix)",
    desc="Return true if s starts with the given prefix.",
    example='starts_with("hello", "he")  -> true',
    returns="bool")

_doc("ends_with",
    syntax="ends_with(s, suffix)",
    desc="Return true if s ends with the given suffix.",
    example='ends_with("hello", "lo")  -> true',
    returns="bool")

_doc("contains",
    syntax="contains(s, sub)",
    desc="Return true if s contains the substring sub.",
    example='contains("hello", "ell")  -> true\ncontains("hello", "xyz") -> false',
    returns="bool")

_doc("length",
    syntax="length(obj)",
    desc="Alias for len(). Return the length of a collection.",
    example='length("hello")  -> 5\nlength([1,2,3])  -> 3',
    returns="number")

_doc("append",
    syntax="append(list, value)",
    desc="Append value to the end of the list. Modifies the list in place.",
    example='var lst = [1,2]\nappend(lst, 3)\nprint(lst)  -> [1, 2, 3]',
    returns="nil")

_doc("insert",
    syntax="insert(list, index, value)",
    desc="Insert value at the given index in the list.",
    example='var lst = [1,3]\ninsert(lst, 1, 2)\nprint(lst)  -> [1, 2, 3]',
    returns="nil")

_doc("remove",
    syntax="remove(list, index)",
    desc="Remove and return the element at the given index.",
    example='var lst = [1,2,3]\nvar v = remove(lst, 1)\nprint(v)     -> 2\nprint(lst)   -> [1, 3]',
    returns="any")

_doc("pop",
    syntax="pop(list)",
    desc="Remove and return the last element of the list.",
    example='var lst = [1,2,3]\nvar v = pop(lst)\nprint(v)     -> 3\nprint(lst)   -> [1, 2]',
    returns="any")

_doc("clear",
    syntax="clear(list)",
    desc="Remove all elements from the list.",
    example='var lst = [1,2,3]\nclear(lst)\nprint(lst)  -> []',
    returns="nil")

_doc("keys",
    syntax="keys(dict)",
    desc="Return a list of all keys in the dictionary.",
    example='keys({"a":1, "b":2})  -> ["a", "b"]',
    returns="list")

_doc("values",
    syntax="values(dict)",
    desc="Return a list of all values in the dictionary.",
    example='values({"a":1, "b":2})  -> [1, 2]',
    returns="list")

_doc("items",
    syntax="items(dict)",
    desc="Return a list of (key, value) tuples from the dictionary.",
    example='items({"a":1, "b":2})  -> [("a", 1), ("b", 2)]',
    returns="list")

_doc("has_key",
    syntax="has_key(dict, key)",
    desc="Return true if dict contains the given key.",
    example='has_key({"a":1}, "a")  -> true\nhas_key({"a":1}, "b") -> false',
    returns="bool")

_doc("set",
    syntax="set(dict, key, value)",
    desc="Set dict[key] = value. Modifies the dictionary in place.",
    example='var d = {"a":1}\nset(d, "b", 2)\nprint(d)  -> {"a":1, "b":2}',
    returns="nil")

_doc("json_parse",
    syntax="json_parse(s)",
    desc="Parse a JSON string into an Ipp value (dict, list, string, number, bool, nil).",
    example='var d = json_parse(\'{"a":1, "b":2}\')\nprint(d["a"])  -> 1',
    returns="any")

_doc("json_stringify",
    syntax="json_stringify(value, indent=nil)",
    desc="Convert an Ipp value to a JSON string. Optional indent for pretty-printing.",
    example='json_stringify({"a":1, "b":2})  -> \'{"a":1,"b":2}\'',
    returns="string")

_doc("sha256",
    syntax="sha256(s)",
    desc="Return the SHA-256 hex digest of the string s.",
    example='sha256("hello")  -> "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"',
    returns="string")

_doc("md5",
    syntax="md5(s)",
    desc="Return the MD5 hex digest of the string s.",
    example='md5("hello")  -> "5d41402abc4b2a76b9719d911017c592"',
    returns="string")

_doc("sha1",
    syntax="sha1(s)",
    desc="Return the SHA-1 hex digest of the string s.",
    example='sha1("hello")  -> "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"',
    returns="string")

_doc("base64_encode",
    syntax="base64_encode(s)",
    desc="Encode a string to Base64.",
    example='base64_encode("Hello, World!")  -> "SGVsbG8sIFdvcmxkIQ=="',
    returns="string")

_doc("base64_decode",
    syntax="base64_decode(s)",
    desc="Decode a Base64-encoded string back to the original string.",
    example='base64_decode("SGVsbG8sIFdvcmxkIQ==")  -> "Hello, World!"',
    returns="string")

_doc("read_file",
    syntax="read_file(path)",
    desc="Read the entire contents of a file as a string.",
    example='var content = read_file("data.txt")\nprint(content)',
    returns="string")

_doc("write_file",
    syntax="write_file(path, content)",
    desc="Write content to a file, overwriting any existing content.",
    example='write_file("hello.txt", "Hello, World!")  -> true',
    returns="bool")

_doc("append_file",
    syntax="append_file(path, content)",
    desc="Append content to the end of a file.",
    example='append_file("log.txt", "new line\\n")  -> true',
    returns="bool")

_doc("file_exists",
    syntax="file_exists(path)",
    desc="Return true if a file or directory exists at the given path.",
    example='file_exists("data.txt")  -> true',
    returns="bool")

_doc("delete_file",
    syntax="delete_file(path)",
    desc="Delete the file at the given path.",
    example='delete_file("temp.txt")  -> true',
    returns="bool")

_doc("list_dir",
    syntax="list_dir(path='.')",
    desc="List the contents of a directory as a list of filenames.",
    example='list_dir(".")  -> ["file1.ipp", "src", "tests", ...]',
    returns="list")

_doc("http_get",
    syntax="http_get(url, headers=nil)",
    desc="Perform an HTTP GET request and return the response body.",
    example='var resp = http_get("https://api.example.com/data")\nprint(resp)',
    returns="string")

_doc("http_post",
    syntax="http_post(url, body='', headers=nil)",
    desc="Perform an HTTP POST request with an optional body and return the response.",
    example='var resp = http_post("https://api.example.com/data", \'{"key":"value"}\')',
    returns="string")

_doc("regex",
    syntax="regex(pattern, flags='')",
    desc="Compile a regex pattern. Supports flags: i (case-insensitive), m (multiline), s (dotall).",
    example='var re = regex("[0-9]+")\nprint(re)  -> "[0-9]+"',
    returns="regex")

_doc("printf",
    syntax="printf(fmt, ...)",
    desc="Print a formatted string using printf-style format specifiers.",
    example='printf("Value: %d, Name: %s\\n", 42, "test")\n-> "Value: 42, Name: test"',
    returns="nil")

_doc("sprintf",
    syntax="sprintf(fmt, ...)",
    desc="Return a formatted string using printf-style format specifiers (without printing).",
    example='var s = sprintf("Hello %s, you are %d years old", "Alice", 30)',
    returns="string")

_doc("inspect",
    syntax="inspect(value)",
    desc="Print a detailed inspection of a value, showing its type and structure.",
    example='inspect([1,2,3])  -> [1, 2, 3]\ninspect({"a":1})  -> {"a": 1}',
    returns="nil")

_doc("glob",
    syntax="glob(pattern)",
    desc="Return a list of files matching the glob pattern.",
    example='glob("*.ipp")  -> ["main.ipp", "utils.ipp", ...]',
    returns="list")

_doc("breakpoint",
    syntax="breakpoint()",
    desc="Pause execution and enter the debugger at the current line (v2.0.25+).",
    example='func calc(x) {\n    breakpoint()\n    return x * 2\n}',
    returns="nil")

_doc("uuid",
    syntax="uuid()",
    desc="Generate a random UUID (v4) string.",
    example='uuid()  -> "70b5953b-10ce-4a8e-ab81-049758c6439d"',
    returns="string")

_doc("get_env",
    syntax="get_env(name)",
    desc="Get the value of an environment variable, or nil if not set.",
    example='get_env("PATH")  -> "/usr/bin:/bin"',
    returns="string or nil")

_doc("get_args",
    syntax="get_args()",
    desc="Return a list of command-line arguments passed to the script.",
    example='get_args()  -> ["script.ipp", "arg1", "arg2"]',
    returns="list")

_doc("methods",
    syntax="methods(obj)",
    desc="Return a list of method names available on an Ipp object.",
    example='class Dog { func bark() {} }\nvar d = Dog()\nmethods(d)  -> ["bark", "init"]',
    returns="list")

_doc("fields",
    syntax="fields(obj)",
    desc="Return a dict of field name/value pairs for an Ipp object.",
    example='class Dog { func init() { this.name = "Rex" } }\nvar d = Dog()\nfields(d)  -> {"name": "Rex"}',
    returns="dict")

_doc("write_file",
    syntax="write_file(path, content)",
    desc="Write string content to a file, overwriting if it exists.",
    example='write_file("data.txt", "Hello World")  -> true',
    returns="bool")

_doc("read_file",
    syntax="read_file(path)",
    desc="Read the entire contents of a file as a string.",
    example='var data = read_file("data.txt")',
    returns="string or nil")

_doc("delete_file",
    syntax="delete_file(path)",
    desc="Delete a file from the filesystem.",
    example='delete_file("temp.txt")  -> true',
    returns="bool")

_doc("list_dir",
    syntax="list_dir(path='.')",
    desc="List the contents of a directory as a list of strings.",
    example='list_dir()        -> ["file1.txt", "folder/"]\nlist_dir("/home") -> ["user1", "user2"]',
    returns="list")

_doc("sleep",
    syntax="sleep(seconds)",
    desc="Pause execution for the given number of seconds.",
    example='sleep(1)    # pause 1 second\nsleep(0.5)  # pause 500ms',
    returns="nil")

_doc("now",
    syntax="now()",
    desc="Return the current date/time as an ISO 8601 string.",
    example='now()  -> "2026-07-01T12:00:00.000000"',
    returns="string")

_doc("printf",
    syntax="printf(format, ...)",
    desc="Print formatted string with % placeholders (like C printf).",
    example='printf("Value: %d, Name: %s", 42, "Alice")',
    returns="nil")

_doc("sprintf",
    syntax="sprintf(format, ...)",
    desc="Return a formatted string with % placeholders (like C sprintf).",
    example='sprintf("Pi ≈ %.2f", 3.14159)  -> "Pi ≈ 3.14"',
    returns="string")

_doc("glob",
    syntax="glob(pattern)",
    desc="Return a list of file paths matching the given glob pattern.",
    example='glob("*.ipp")  -> ["main.ipp", "test.ipp"]',
    returns="list")

_doc("insert",
    syntax="insert(list, index, value)",
    desc="Insert a value into a list at the given index, shifting elements right.",
    example='var a = [1, 3, 4]\ninsert(a, 1, 2)\nprint(a)  -> [1, 2, 3, 4]',
    returns="nil")

_doc("pop",
    syntax="pop(list, index=-1)",
    desc="Remove and return the element at the given index (default last).",
    example='var a = [1, 2, 3]\nvar v = pop(a)\nprint(v)  -> 3\nprint(a)  -> [1, 2]',
    returns="any")

_doc("clear",
    syntax="clear(list_or_dict)",
    desc="Remove all elements from a list or all keys from a dict.",
    example='var a = [1, 2, 3]\nclear(a)\nprint(a)  -> []',
    returns="nil")

_doc("uuid",
    syntax="uuid()",
    desc="Generate a random UUID v4 string.",
    example='uuid()  -> "70b5953b-10ce-4a8e-ab81-049758c6439d"',
    returns="string")

_doc("get_env",
    syntax="get_env(name)",
    desc="Get the value of an environment variable, or nil if not set.",
    example='get_env("PATH")  -> "/usr/bin:/bin"',
    returns="string or nil")

_doc("get_args",
    syntax="get_args()",
    desc="Return a list of command-line arguments passed to the script.",
    example='get_args()  -> ["script.ipp", "arg1", "arg2"]',
    returns="list")

_doc("inspect",
    syntax="inspect(obj, label=nil)",
    desc="Register an object for live overlay inspection in the canvas window.",
    example='var player = {"x": 100, "y": 200}\ninspect(player, "Player")',
    returns="nil")

_doc("breakpoint",
    syntax="breakpoint()",
    desc="Pause execution and enter the debugger at this line.",
    example='func test() {\n    breakpoint()\n    print("after debug")\n}',
    returns="nil")

_doc("key_name",
    syntax="key_name(scancode)",
    desc="Convert a scancode integer or key string to its normalized key name.",
    example='key_name(65)     -> "a"\nkey_name("Enter") -> "enter"',
    returns="string")

_doc("key_down",
    syntax="key_down(key)",
    desc="Check if a key is currently held down.",
    example='if key_down("space") { print("jumping!") }',
    returns="bool")

_doc("key_up",
    syntax="key_up(key)",
    desc="Check if a key was just released.",
    example='if key_up("space") { print("landed!") }',
    returns="bool")

_doc("ascii",
    syntax="ascii(char)",
    desc="Return the ASCII code of a character.",
    example='ascii("A") -> 65\nascii(" ") -> 32',
    returns="number")

_doc("chr",
    syntax="chr(code)",
    desc="Return the character for the given ASCII/Unicode code point.",
    example='chr(65) -> "A"\nchr(32) -> " "',
    returns="string")

_doc("ord",
    syntax="ord(char)",
    desc="Alias for ascii — return the code point of a character.",
    example='ord("A") -> 65',
    returns="number")

_doc("hex",
    syntax="hex(number)",
    desc="Return the hexadecimal string representation of a number.",
    example='hex(255) -> "ff"',
    returns="string")

_doc("bin",
    syntax="bin(number)",
    desc="Return the binary string representation of a number.",
    example='bin(10) -> "1010"',
    returns="string")

_doc("assert_eq",
    syntax="assert_eq(a, b)",
    desc="Assert that two values are equal; print error message if not.",
    example='assert_eq(2+2, 4)  # passes silently\nassert_eq(1, 2)    # prints error',
    returns="nil")

_doc("isclose",
    syntax="isclose(a, b, rel_tol=1e-9)",
    desc="Check if two floats are approximately equal within a relative tolerance.",
    example='isclose(0.1+0.2, 0.3) -> true',
    returns="bool")

_doc("sign",
    syntax="sign(x)",
    desc="Return 1 for positive numbers, -1 for negative, 0 for zero.",
    example='sign(5)  -> 1\nsign(-3) -> -1\nsign(0)  -> 0',
    returns="number")

_doc("gcd",
    syntax="gcd(a, b)",
    desc="Return the greatest common divisor of two numbers.",
    example='gcd(12, 8) -> 4\ngcd(100, 75) -> 25',
    returns="number")

_doc("lcm",
    syntax="lcm(a, b)",
    desc="Return the least common multiple of two numbers.",
    example='lcm(4, 6)  -> 12\nlcm(12, 18) -> 36',
    returns="number")

_doc("hypot",
    syntax="hypot(x, y)",
    desc="Return sqrt(x^2 + y^2), the hypotenuse of a right triangle.",
    example='hypot(3, 4) -> 5.0',
    returns="number")

_doc("factorial",
    syntax="factorial(n)",
    desc="Return n! (n factorial), the product of 1..n.",
    example='factorial(5)  -> 120\nfactorial(10) -> 3628800',
    returns="number")

_doc("all",
    syntax="all(list)",
    desc="Return true if all elements in the list are truthy.",
    example='all([true, true, false]) -> false\nall([1, 2, 3])       -> true',
    returns="bool")

_doc("any",
    syntax="any(list)",
    desc="Return true if any element in the list is truthy.",
    example='any([false, false, true]) -> true\nany([0, nil, false])    -> false',
    returns="bool")
