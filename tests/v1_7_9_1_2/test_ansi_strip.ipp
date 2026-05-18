# v1.7.9.1.2 — REPL ANSI escape code fixes
# Tests strip_ansi builtin and \x hex escape support

# Basic string ops still work
var s = "hello world"
assert s.contains("hello") == true
assert s.upper() == "HELLO WORLD"

# ipp_version() returns current version string
var v = ipp_version()
assert v.contains("1.7.9.1") == true

# \x1b is ESC — v1.7.9.1.2 adds \xHH hex escape support
var esc_char = "\x1b"
assert len(esc_char) == 1

# \e is also ESC — new shorthand
var esc2 = "\e"
assert esc2 == esc_char

# strip_ansi removes ANSI colour codes
var raw = "\x1b[38;2;80;200;255mtest\x1b[0m"
var clean = strip_ansi(raw)
assert clean == "test"

# Bold + colour sequence
var bold = "\x1b[1m\x1b[38;5;51mBold Blue\x1b[0m"
assert strip_ansi(bold) == "Bold Blue"

# Plain string passes through unchanged
assert strip_ansi("no escapes here") == "no escapes here"

# Empty string
assert strip_ansi("") == ""

# Multiple codes in sequence
var multi = "\x1b[1m\x1b[4munderlined bold\x1b[0m plain"
assert strip_ansi(multi) == "underlined bold plain"

# \xHH for other characters
var tab_like = "\x09"   # horizontal tab
assert len(tab_like) == 1

# Hex digits all lowercase work
var a_char = "\x61"  # 'a'
assert a_char == "a"

print("v1.7.9.1.2 ANSI tests passed")
