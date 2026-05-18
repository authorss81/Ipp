# v1.7.9.1.4 — Enhanced Colours & Syntax Highlighting Themes

# strip_ansi cleans ANSI escape sequences
var raw = "\x1b[38;2;100;200;255mHello\x1b[0m"
var clean = strip_ansi(raw)
assert clean == "Hello"

# \xHH hex escapes work
assert "\x61" == "a"
assert "\x5A" == "Z"
assert "\e"   == "\x1b"

# Version string
var v = ipp_version()
assert v.contains("1.7.9.1") == true

# Bold + colour sequences strip cleanly
var bold = "\x1b[1mBold\x1b[0m"
assert strip_ansi(bold) == "Bold"

# Plain string unchanged
assert strip_ansi("no escapes") == "no escapes"

# Empty string
assert strip_ansi("") == ""

# Multiple codes
var multi = "\x1b[1m\x1b[4munder bold\x1b[0m plain"
assert strip_ansi(multi) == "under bold plain"

# ESC shorthand \e
var esc_str = "\e[0m"
assert strip_ansi(esc_str) == ""

print("v1.7.9.1.4 theme tests passed")
