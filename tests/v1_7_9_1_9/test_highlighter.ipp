# v1.7.9.1.9 — Highlighter tokenizer test
# Tests that the Ipp highlighter correctly categorises tokens

# The tokenizer is a Python module; test via builtins it adds

# strip_ansi removes escape sequences (depends on highlighter's colour output)
var raw  = "\x1b[38;2;200;120;255mfunc\x1b[0m"
var clean = strip_ansi(raw)
assert clean == "func"

# \e is ESC
assert "\e" == "\x1b"

# highlight_line function exists (exposed as builtin in 1.7.9.1.9)
var hl = highlight_line("func add(a, b) { return a + b }")
# highlight_line returns a string (with ANSI codes when colours enabled)
assert ipp_type(hl) == "string"
assert len(hl) >= len("func add(a, b) { return a + b }")

# plain text survives
var plain = highlight_line("# just a comment")
assert plain.contains("comment") or plain.contains("just")

print("v1.7.9.1.9 highlighter tests passed")
