# Ipp Web Playground

A web-based code editor and execution environment for the Ipp programming language.

## Features

- **CodeMirror Editor** - Syntax highlighting for Ipp
- **Code Execution** - Run Ipp code in the browser (JS implementation)
- **Canvas Drawing** - 2D graphics API with canvas.rect, canvas.circle, etc.
- **3D Math Support** - vec4, mat4, quat demonstrations
- **Scene Graph** - Simulated 3D scene nodes
- **Real-time Output** - See your results instantly
- **Shareable** - Share code snippets via URL
- **Multiple Demos** - Canvas, 3D Math, Web APIs, Game demos
- **Dark Theme** - Beautiful Dracula-inspired UI

## Demo Tabs

- 🎨 **Canvas** - 2D drawing with shapes, lines, text
- 🌐 **3D Scene** - Scene graph and wireframe rendering
- 🔢 **3D Math** - vec4, mat4, quat operations
- 🌐 **Web APIs** - JSON, strings, arrays, type checking
- 🎮 **Game** - Simple game animation demo

## How to Use

1. Open `index.html` in a web browser
2. Write your Ipp code in the editor
3. Press **Run** or **Ctrl+Enter** to execute
4. View output in the right panel
5. See canvas/3D preview below output

## Keyboard Shortcuts

- **Ctrl+Enter** - Run code
- **Ctrl+S** - Save to file
- **Ctrl+O** - Load from file
- **Escape** - Close help panel

## Example Code

```ipp
# Canvas Drawing
canvas.clear("#1a1b26")
canvas.rect(20, 20, 100, 40, "#7aa2f7")
canvas.circle(150, 40, 25, "#bb9af7")
canvas.line(20, 80, 200, 80, "#7dcfff")
canvas.text(20, 120, "Hello Ipp!", "#c0caf5")

print("Drawing complete!")

# Variables and Math
var x = 10
var y = 20
print("x + y = " + str(x + y))

# Functions
func greet(name) {
    return "Hello, " + name + "!"
}
print(greet("Ipp"))
```

## Canvas API

```ipp
canvas.clear(color)           # Clear canvas with color
canvas.rect(x, y, w, h, color) # Draw rectangle
canvas.circle(x, y, r, color) # Draw circle
canvas.line(x1, y1, x2, y2, color) # Draw line
canvas.text(x, y, text, color)     # Draw text
```

## Requirements

- Modern web browser (Chrome, Firefox, Edge, Safari)
- Internet connection (for CodeMirror CDN)

## Running Locally

```bash
# Using Python's built-in server
cd web-playground
python -m http.server 8080
# Then open http://localhost:8080
```

## Version

**Version**: v1.5.18  
**Part of**: Ipp Language v1.5.18