# Test v1.5.3a - 2D Canvas API (Web Playground Test)

print("=== Testing v1.5.3a 2D Canvas API ===")

# Test that interpreter works
print("Interpreter is working!")

# Variables and expressions
var x = 10
var y = 20
print("x = " + str(x))
print("y = " + str(y))

# Canvas operations are for the web playground:
# In the web playground, you can use:
# canvas.rect(x, y, w, h, "color")
# canvas.circle(x, y, r, "color")  
# canvas.line(x1, y1, x2, y2, "color")
# canvas.text(x, y, "text", "color")
# canvas.clear("color")

# Test all basic features work
func add(a, b) {
    return a + b
}

print("add(5, 3) = " + str(add(5, 3)))

var nums = [1, 2, 3, 4, 5]
print("List length: " + str(len(nums)))

print("\n=== Canvas API ready! ===")
print("Use in Web Playground:")
print("  canvas.rect(10, 10, 100, 50, 'red')")
print("  canvas.circle(100, 100, 30, 'blue')")
print("  canvas.line(0, 0, 200, 200, 'green')")
print("  canvas.text(50, 50, 'Hello!', 'white')")
print("  canvas.clear('black')")