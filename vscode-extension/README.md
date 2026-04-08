# Ipp Language Support for VSCode

This extension provides language support for the Ipp programming language in Visual Studio Code.

## Features (v1.5.1)

- **Syntax Highlighting** — Full syntax highlighting for Ipp code
- **Code Snippets** — 15 built-in code snippets for common patterns:
  - `func` — Function declaration
  - `class` — Class declaration
  - `for` — For loop
  - `while` — While loop
  - `if` — If statement
  - `ife` — If-else statement
  - `match` — Match statement
  - `try` — Try-catch statement
  - `var` — Variable declaration
  - `list` — List literal
  - `dict` — Dictionary literal
  - `lambda` — Lambda function
  - `async` — Async function
  - `enum` — Enum declaration
  - `init` — Class constructor
- **Task Runner** — Run and check Ipp scripts from VSCode (Ctrl+Shift+B)
- **LSP Integration** — Language Server Protocol support:
  - Go-to-definition
  - Find all references
  - Symbol search
  - Hover information
  - Auto-completion
  - Rename symbol
  - Document symbols (outline)

## Requirements

- Visual Studio Code 1.70.0 or higher
- Python 3.8+ (for running Ipp scripts)
- Ipp language installed: `pip install ipp-lang`

## Extension Settings

This extension contributes the following settings:

* `ipp.enable`: Enable/disable the extension
* `ipp.trace.server`: Trace server communication between VS Code and the language server.
* `ipp.runnable.command`: Command to run Ipp scripts (default: `python main.py run`)

## Running Ipp Code

1. Open an Ipp file (`.ipp` extension)
2. Press `F5` to run the current file, or use the terminal:
   ```
   python main.py run yourfile.ipp
   ```
3. For syntax checking: `python main.py check yourfile.ipp`

## Commands

| Command | Description |
|---------|-------------|
| `ipp.run` | Run the current Ipp file |
| `ipp.check` | Check syntax of current file |
| `ipp.lsp` | Start the LSP server |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F5` | Run current file |
| `Ctrl+Shift+B` | Open task runner |

## Known Issues

- LSP server requires Python path to be configured
- Debugging support is experimental

## Release Notes

### 1.5.1

- Added code snippets (15 snippets)
- Added task runner for `ipp run` and `ipp check`
- Added LSP server integration
- Added hover information and auto-completion
- Added go-to-definition and find references

### 0.0.1

Initial release of Ipp language support for VSCode.
