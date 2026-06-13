# Test v2.0.6: Template Strings t"..." for Safe HTML/SQL

# Basic template string — auto-escapes HTML
var player_name = "<script>alert('xss')</script>"
var safe = t"<p>Hello, {player_name}!</p>"
assert safe == "<p>Hello, &lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;!</p>"

# Template with numeric values
var score = 42
var msg = t"Your score: {score}"
assert msg == "Your score: 42"

# Template with expression
var a = 10
var b = 20
var result = t"Sum: {a + b}"
assert result == "Sum: 30"

# Template with no interpolations (plain text)
var plain = t"Hello, World!"
assert plain == "Hello, World!"

# Escaped braces {{ }}
var with_braces = t"Literal braces: {{hello}}"
assert with_braces == "Literal braces: {hello}"

# Multiple interpolations
var x = "<b>bold</b>"
var y = "<i>italic</i>"
var multi = t"x={x}, y={y}"
assert multi == "x=&lt;b&gt;bold&lt;/b&gt;, y=&lt;i&gt;italic&lt;/i&gt;"

# Values that don't need escaping
var name = "Alice"
var no_escape = t"Hello, {name}!"
assert no_escape == "Hello, Alice!"

# Numbers are auto-stringified and safe
var num = 100
var num_t = t"Count: {num}"
assert num_t == "Count: 100"

# Boolean values
var flag = true
var bool_t = t"Flag: {flag}"
assert bool_t == "Flag: true"

# HTML entities in the literal parts are NOT escaped (they're literal)
var literal_html = t"<p>literal</p>"
assert literal_html == "<p>literal</p>"

# Mixed: literal HTML safe, interpolated HTML escaped
var evil = "<script>"
var mixed = t"<div>{evil}</div>"
assert mixed == "<div>&lt;script&gt;</div>"

# Ampersand escaping
var amp = "a & b"
var amp_t = t"{amp}"
assert amp_t == "a &amp; b"

# Double-quote escaping
var dq = 'he said "hello"'
var dq_t = t"{dq}"
assert dq_t == "he said &quot;hello&quot;"

# Single-quote escaping
var sq = "it's"
var sq_t = t"{sq}"
assert sq_t == "it&#39;s"

print("All template string tests passed!")
