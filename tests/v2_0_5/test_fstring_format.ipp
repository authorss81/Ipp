# v2.0.5 — f-string format spec {expr:format_spec}
# Tests for Python-style format specifiers inside f-string braces

# Basic float formatting
var pi_val = 3.14159
assert f"pi = {pi_val:.2f}" == "pi = 3.14"
assert f"{pi_val:.4f}" == "3.1416"
assert f"{pi_val:.0f}" == "3"

# Integer formatting
var score = 42
assert f"{score}" == "42"
assert f"{score:>10}" == "        42"
assert f"{score:<10}" == "42        "
assert f"{score:^10}" == "    42    "

# Hex formatting
var n = 255
assert f"hex: {n:#x}" == "hex: 0xff"
assert f"{n:x}" == "ff"
assert f"{n:#X}" == "0XFF"

# String padding
var s = "hello"
assert f"'{s:>10}'" == "'     hello'"
assert f"'{s:<10}'" == "'hello     '"
assert f"'{s:^10}'" == "'  hello   '"

# Percentage
var pct = 0.875
assert f"{pct:.1%}" == "87.5%"
assert f"{pct:.0%}" == "88%"

# Zero padding
assert f"{42:05d}" == "00042"
assert f"{-7:05d}" == "-0007"

# Sign handling
assert f"{42:+d}" == "+42"
assert f"{-42:+d}" == "-42"
assert f"{42: d}" == " 42"
assert f"{-42: d}" == "-42"

# Combined with expressions
var x = 10
var y = 3
assert f"{x / y:.3f}" == "3.333"

# Format spec with string method calls
var name = "Alice"
assert f"Hello {name.upper():>10}" == "Hello      ALICE"

# Thousands separator
var big = 1234567
assert f"{big:,}" == "1,234,567"

# Scientific notation
var tiny = 0.000123
assert f"{tiny:.2e}" == "1.23e-04"

# Nested braces don't interfere
assert f"{{literal}}" == "{literal}"

# Mixed format and non-format segments
assert f"{42:>5} items for ${3.5:.2f}" == "   42 items for $3.50"

# Format spec with whitespace after colon
assert f"{42:>5}" == "   42"

# Edge cases
assert f"{0:.1f}" == "0.0"
assert f"{1:.0f}" == "1"
assert f"{999:06d}" == "000999"

print("All f-string format spec tests passed!")
