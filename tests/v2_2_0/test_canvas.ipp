# v2.2.0 canvas 2D drawing builtins
var win = canvas_open()
assert win == "[canvas window open]"

# Basic shapes
canvas_rect(10, 10, 100, 50, "red")
canvas_circle(200, 100, 40, "blue")
canvas_line(10, 200, 300, 200, "green")
canvas_text(150, 300, "Hello from Ipp!", "black")

# Enhanced drawing primitives (v2.2.0)
canvas_pixel(400, 50, "red")
canvas_fill("lightyellow")
canvas_bg("lightyellow")
var sz = canvas_size()
print("Canvas size: ", sz[0], "x", sz[1])
assert sz[0] > 0
assert sz[1] > 0
var col = canvas_color(255, 0, 0)
assert col == "#ff0000"
canvas_rect(50, 50, 100, 80, col)

canvas_clear()
canvas_show()

print("All v2.2.0 canvas tests passed")
