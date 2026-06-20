import { Canvas, Color, run, _resolve_color, RED, GREEN, BLUE, WHITE, BLACK, YELLOW, CYAN, ORANGE, MAGENTA, GRAY } from "ipp-canvas"

# ── Color Tests ──
var red = Color(255, 0, 0)
assert red.hex() == "#ff0000", "Color red hex"
assert type(red.hex()) == "string", "Color hex is string"

var green = Color(0, 255, 0)
assert green.hex() == "#00ff00", "Color green hex"

var blue = Color(0, 0, 255)
assert blue.hex() == "#0000ff", "Color blue hex"

# Named color exports
assert RED.hex() == "#ff0000", "RED"
assert GREEN.hex() == "#00ff00", "GREEN"
assert BLUE.hex() == "#0000ff", "BLUE"
assert WHITE.hex() == "#ffffff", "WHITE"
assert BLACK.hex() == "#000000", "BLACK"
assert YELLOW.hex() == "#ffff00", "YELLOW"
assert CYAN.hex() == "#00ffff", "CYAN"
assert ORANGE.hex() == "#ffa500", "ORANGE"
assert MAGENTA.hex() == "#ff00ff", "MAGENTA"
assert GRAY.hex() == "#808080", "GRAY"

# from_hex
var from_hex = Color.from_hex("#ff8800")
assert from_hex.hex() == "#ff8800", "Color.from_hex with #"

var from_hex2 = Color.from_hex("aabbcc")
assert from_hex2.hex() == "#aabbcc", "Color.from_hex without #"

# _resolve_color
assert _resolve_color("#ff0000") == "#ff0000", "resolve string pass-through"
assert _resolve_color(RED) == "#ff0000", "resolve Color object"
assert _resolve_color("blue") == "blue", "resolve named color"

# Color type check
assert red is Color, "red is Color"

# ── Canvas API Tests (headless — tkinter stubbed) ──
var c = Canvas()
assert c != nil, "Canvas created"

# Methods exist and are chainable
assert c.rect(10, 10, 50, 50, "red") is Canvas, "rect chainable"
assert c.circle(100, 100, 30, "blue") is Canvas, "circle chainable"
assert c.line(0, 0, 200, 200, "green") is Canvas, "line chainable"
assert c.text(50, 50, "Hello", "black") is Canvas, "text chainable"
assert c.pixel(10, 10, "red") is Canvas, "pixel chainable"
assert c.fill("white") is Canvas, "fill chainable"
assert c.clear() is Canvas, "clear chainable"
assert c.bg("white") is Canvas, "bg chainable"

# Methods accept Color objects
assert c.rect(10, 10, 50, 50, RED) is Canvas, "rect with Color"
assert c.circle(100, 100, 30, BLUE) is Canvas, "circle with Color"
assert c.line(0, 0, 200, 200, GREEN) is Canvas, "line with Color"

# size and update
var sz = c.size()
assert sz == [0, 0] or type(sz) == "list", "canvas size"
assert c.update() != nil, "canvas update"

# Open (no-op when tkinter is stubbed)
c.open()
assert c != nil, "canvas open"

# run function exists
assert run != nil, "run function exists"

print("All v2.0.20 canvas tests passed!")
