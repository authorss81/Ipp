#!/usr/bin/env python3
"""Simple Ipp interpreter that can run in browser via WASM."""

import sys
import os

# Simple Ipp interpreter for browser
IPP_INTERPRETER_JS = '''
// Simple Ipp interpreter for browser
const IppRuntime = {
    // Global environment
    env: {},
    
    // Built-in functions
    builtins: {
        print: (...args) => console.log(...args),
        len: (arr) => arr.length,
        str: (x) => String(x),
        int: (x) => parseInt(x),
        float: (x) => parseFloat(x),
        abs: (x) => Math.abs(x),
        min: (...args) => Math.min(...args),
        max: (...args) => Math.max(...args),
        range: (start, end) => {
            const arr = [];
            for (let i = start; i < end; i++) arr.push(i);
            return arr;
        },
        type: (x) => typeof x,
        assert: (cond, msg) => {
            if (!cond) throw new Error('Assertion failed: ' + msg);
        },
    },
    
    // Execute Ipp code
    execute: function(code) {
        // Simple eval for demonstration
        // In production, parse and execute AST
        try {
            // Basic transformations
            let js = code
                .replace(/func\\s+(\\w+)\\s*\\(([^)]*)\\)\\s*\\{/g, 'function $1($2) {')
                .replace(/return\\s+([^;]+);?/g, 'return $1;')
                .replace(/var\\s+(\\w+)\\s*=\\s*(.+);/g, 'let $1 = $2;')
                .replace(/let\\s+(\\w+)\\s*=\\s*(.+);/g, 'let $1 = $2;')
                .replace(/for\\s+(\\w+)\\s+in\\s+(.+)\\s*\\{/g, 'for (let $1 of $2) {')
                .replace(/if\\s+(.+)\\s*\\{/g, 'if ($1) {')
                .replace(/else\\s*\\{/g, 'else {')
                .replace(/this\\.(\\w+)/g, 'this.$1');
            
            // Add builtins to scope
            const scope = { ...this.builtins };
            
            // Execute
            const fn = new Function(...Object.keys(scope), js);
            fn(...Object.values(scope));
            
            return { success: true };
        } catch (e) {
            return { success: false, error: e.message };
        }
    },
    
    // Run specific function
    runFunction: function(name, args) {
        if (this.env[name]) {
            return this.env[name](...args);
        }
        throw new Error('Function not found: ' + name);
    },
};

// Make available globally
window.IppRuntime = IppRuntime;
'''


def generate_js_runtime(output_file=None):
    """Generate JavaScript runtime for browser."""
    js = IPP_INTERPRETER_JS
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(js)
    
    return js


def main():
    print("Ipp Web Playground Runtime Generator")
    print("Usage: python -m ipp.wasm.runtime output.js")
    
    # Generate default runtime
    js = generate_js_runtime("ipp-runtime.js")
    print(f"Generated ipp-runtime.js ({len(js)} bytes)")


if __name__ == "__main__":
    main()