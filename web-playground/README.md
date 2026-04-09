# Ipp Web Playground

A web-based code editor and execution environment for the Ipp programming language.

## Features

- **Monaco Editor** - VSCode's code editor for syntax highlighting
- **Code Execution** - Run Ipp code in the browser
- **Real-time Output** - See your results instantly
- **Shareable** - Share code snippets via URL (coming soon)

## How to Use

1. Open `index.html` in a web browser
2. Write your Ipp code in the editor
3. Press **Run** or **F5** to execute
4. View output in the right panel

## Example Code

```ipp
func fibonacci(n) {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

print("Fibonacci sequence:")
for i in 0..10 {
    print(str(i) + ": " + str(fibonacci(i)))
}
```

## Requirements

- Modern web browser (Chrome, Firefox, Edge, Safari)
- Internet connection (for Monaco Editor CDN)

## Running Locally

```bash
# Using Python's built-in server
cd web-playground
python -m http.server 8080
# Then open http://localhost:8080
```

## Next Steps (v1.5.2b)

- [ ] Connect WASM runtime for actual Ipp execution
- [ ] Add code sharing via URL
- [ ] Add save/load code snippets
- [ ] Add more syntax highlighting for Ipp

---

**Version**: v1.5.2b  
**Part of**: Ipp Language v1.5.2