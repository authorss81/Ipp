# v1.9.3: Multi-line strings """..."""

# ===== Basic multi-line string =====
var s = """
line one
line two
line three
"""
print(s)

var lines = s.strip().split("\n")
print(len(lines))
print(lines[0])
assert len(lines) == 3
assert lines[0] == "line one"
assert lines[1] == "line two"
assert lines[2] == "line three"

# ===== Empty triple-quoted string =====
var empty = """"""
assert empty == ""

# ===== Single quotes inside =====
var with_quote = """he said "hello" """
assert with_quote == 'he said "hello" '

# ===== Double quotes inside =====
var with_two = """a""b"""
assert with_two == 'a""b'

# ===== Escape sequences work =====
var with_escape = """tab\there"""
assert with_escape == "tab\there"

# ===== Single line triple-quoted =====
var single = """hello"""
assert single == "hello"

# ===== Preserve trailing newline =====
var trailing = """
content
"""
print("check trailing")
var stripped = trailing.strip()
assert stripped == "content"

# ===== f"""...""" multi-line f-strings =====
var name = "Alice"
var score = 95
var msg = f"""
Player: {name}
Score: {score}
"""
print("check f-string multiline")
var msg_lines = msg.strip().split("\n")
print(len(msg_lines))
assert len(msg_lines) == 2
assert msg_lines[0] == "Player: Alice"
assert msg_lines[1] == "Score: 95"

# ===== f""" with expressions =====
var x = 10
var y = 20
var result = f"""sum: {x + y}"""
assert result == "sum: 30"

# ===== f""" with inline bool =====
var threshold = 80
var grade = f"""
Name: {name}
Pass: {score >= threshold}
"""
var glines = grade.strip().split("\n")
print(len(glines))
print(glines[0])
print(glines[1])
assert glines[0] == "Name: Alice"
assert glines[1] == "Pass: true"

# ===== Multi-line string in expression =====
print("check concatenation")
var combined = ("""
A
""" + """
B
""").strip().split("\n")
assert combined[0] == "A"
assert combined[1] == "B"

# ===== len() works on multi-line strings =====
var multi = """abc
def
ghi"""
print("check len")
assert len(multi) == 11  # "abc\ndef\nghi" = 3+1+3+1+3 = 11

# ===== Type is string =====
print("check type")
assert type("""hello""") == "string"

print("v1.9.3: Multi-line string tests PASSED")
