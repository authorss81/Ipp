#!/usr/bin/env python3
"""Ipp Language Server Protocol (LSP) implementation."""

import sys
import os
import json
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipp.lexer.lexer import tokenize
from ipp.parser.parser import parse
from ipp.parser.ast import *
from ipp.interpreter.interpreter import Interpreter


class IppLanguageServer:
    def __init__(self):
        self.documents = {}
        self.symbols = {}
        self.diagnostics = {}
        self.interpreter = Interpreter()
        
    def parse_document(self, uri: str, content: str):
        """Parse Ipp document and collect symbols."""
        try:
            tokens = list(tokenize(content))
            ast = parse(tokens)
            self.documents[uri] = {"content": content, "ast": ast, "tokens": tokens}
            self._extract_symbols(uri, ast)
            return {"ast": ast, "tokens": tokens}
        except Exception as e:
            self.documents[uri] = {"content": content, "error": str(e)}
            return None
    
    def _extract_symbols(self, uri: str, ast: Program):
        """Extract all symbols (functions, classes, variables) from AST."""
        symbols = []
        
        class SymbolExtractor(NodeVisitor):
            def __init__(self):
                self.current_scope = []
                self.symbols = []
                
            def visit_function_decl(self, node: FunctionDecl):
                symbol = {
                    "name": node.name,
                    "kind": 12,  # Function
                    "location": {"uri": uri, "range": self._node_range(node)},
                    "containerName": ".".join(self.current_scope) if self.current_scope else None
                }
                self.symbols.append(symbol)
                self.current_scope.append(node.name)
                self.visit_children(node)
                self.current_scope.pop()
                
            def visit_class_decl(self, node: ClassDecl):
                symbol = {
                    "name": node.name,
                    "kind": 6,  # Class
                    "location": {"uri": uri, "range": self._node_range(node)},
                    "containerName": None
                }
                self.symbols.append(symbol)
                self.current_scope.append(node.name)
                self.visit_children(node)
                self.current_scope.pop()
                
            def visit_var_decl(self, node: VarDecl):
                symbol = {
                    "name": node.name,
                    "kind": 5,  # Variable
                    "location": {"uri": uri, "range": self._node_range(node)},
                    "containerName": ".".join(self.current_scope) if self.current_scope else None
                }
                self.symbols.append(symbol)
                
            def _node_range(self, node):
                return {
                    "start": {"line": getattr(node, "line", 0), "character": 0},
                    "end": {"line": getattr(node, "line", 0), "character": 100}
                }
        
        extractor = SymbolExtractor()
        extractor.visit(ast)
        self.symbols[uri] = extractor.symbols
    
    def get_symbols(self, uri: str) -> List[Dict]:
        """Get all symbols in a document."""
        return self.symbols.get(uri, [])
    
    def get_diagnostics(self, uri: str) -> List[Dict]:
        """Get diagnostics (errors/warnings) for a document."""
        doc = self.documents.get(uri)
        if not doc or "error" in doc:
            return []
        
        diagnostics = []
        try:
            tokens = doc.get("tokens", list(tokenize(doc["content"])))
            ast = doc.get("ast", parse(tokens))
        except Exception as e:
            diagnostics.append({
                "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 10}},
                "severity": 1,
                "message": str(e)
            })
        
        return diagnostics
    
    def goto_definition(self, uri: str, position: Dict) -> Optional[Dict]:
        """Go to definition of symbol at position."""
        doc = self.documents.get(uri)
        if not doc:
            return None
        
        line = position.get("line", 0)
        char = position.get("character", 0)
        
        for sym in self.symbols.get(uri, []):
            loc = sym.get("location", {})
            rng = loc.get("range", {})
            start = rng.get("start", {})
            if start.get("line", 0) == line:
                return loc
        
        return None
    
    def find_references(self, uri: str, position: Dict) -> List[Dict]:
        """Find all references to symbol at position."""
        references = []
        doc = self.documents.get(uri)
        if not doc:
            return references
        
        line = position.get("line", 0)
        
        for sym in self.symbols.get(uri, []):
            loc = sym.get("location", {})
            rng = loc.get("range", {})
            start = rng.get("start", {})
            if start.get("line", 0) == line:
                references.append(loc)
        
        return references
    
    def get_completions(self, uri: str, position: Dict) -> List[Dict]:
        """Get completions at position."""
        completions = []
        
        keywords = ["var", "let", "func", "class", "if", "else", "elif", "for", "while",
                    "return", "break", "continue", "import", "try", "catch", "throw",
                    "finally", "match", "case", "default", "async", "await", "nil", "true", "false"]
        
        for kw in keywords:
            completions.append({
                "label": kw,
                "kind": 14,  # Keyword
                "insertText": kw
            })
        
        try:
            from ipp.runtime.builtins import BUILTINS
            for name in BUILTINS:
                completions.append({
                    "label": name,
                    "kind": 6,  # Function
                    "detail": "Ipp builtin"
                })
        except ImportError:
            pass
        
        for sym in self.symbols.get(uri, []):
            kind_map = {12: 6, 6: 7, 5: 5}
            completions.append({
                "label": sym["name"],
                "kind": kind_map.get(sym["kind"], 1),
                "detail": sym.get("containerName", "")
            })
        
        return completions
    
    def get_hover(self, uri: str, position: Dict) -> Optional[Dict]:
        """Get hover information at position."""
        doc = self.documents.get(uri)
        if not doc:
            return None
        
        line = position.get("line", 0)
        
        for sym in self.symbols.get(uri, []):
            loc = sym.get("location", {})
            rng = loc.get("range", {})
            start = rng.get("start", {})
            if start.get("line", 0) == line:
                kind_name = {12: "function", 6: "class", 5: "variable"}.get(sym["kind"], "symbol")
                return {
                    "contents": f"{sym['name']} ({kind_name})"
                }
        
        return None
    
    def rename(self, uri: str, position: Dict, new_name: str) -> Optional[Dict]:
        """Rename symbol at position."""
        doc = self.documents.get(uri)
        if not doc:
            return None
        
        changes = []
        line = position.get("line", 0)
        
        for sym in self.symbols.get(uri, []):
            loc = sym.get("location", {})
            rng = loc.get("range", {})
            start = rng.get("start", {})
            if start.get("line", 0) == line:
                changes.append({
                    "range": rng,
                    "newText": new_name
                })
        
        if changes:
            return {"documentChanges": [{"changes": changes}]}
        return None


def main():
    """Main LSP server loop."""
    import sys
    
    server = IppLanguageServer()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            msg_id = request.get("id")
            
            response = {"id": msg_id, "jsonrpc": "2.0"}
            
            if method == "initialize":
                response["result"] = {
                    "capabilities": {
                        "textDocumentSync": 1,
                        "definitionProvider": True,
                        "referencesProvider": True,
                        "completionProvider": {"triggerCharacters": [".", "("]},
                        "hoverProvider": True,
                        "documentSymbolProvider": True,
                        "renameProvider": True
                    }
                }
            
            elif method == "textDocument/didChange":
                uri = params.get("textDocument", {}).get("uri")
                content = params.get("contentChanges", [{}])[0].get("text", "")
                server.parse_document(uri, content)
                response["result"] = None
            
            elif method == "textDocument/definition":
                uri = params.get("textDocument", {}).get("uri")
                pos = params.get("position", {})
                result = server.goto_definition(uri, pos)
                response["result"] = result
            
            elif method == "textDocument/references":
                uri = params.get("textDocument", {}).get("uri")
                pos = params.get("position", {})
                result = server.find_references(uri, pos)
                response["result"] = result
            
            elif method == "textDocument/completion":
                uri = params.get("textDocument", {}).get("uri")
                pos = params.get("position", {})
                result = server.get_completions(uri, pos)
                response["result"] = result
            
            elif method == "textDocument/hover":
                uri = params.get("textDocument", {}).get("uri")
                pos = params.get("position", {})
                result = server.get_hover(uri, pos)
                response["result"] = result
            
            elif method == "textDocument/documentSymbol":
                uri = params.get("textDocument", {}).get("uri")
                result = server.get_symbols(uri)
                response["result"] = result
            
            elif method == "textDocument/rename":
                uri = params.get("textDocument", {}).get("uri")
                pos = params.get("position", {})
                new_name = params.get("newName", "")
                result = server.rename(uri, pos, new_name)
                response["result"] = result
            
            elif method == "initialized":
                response["result"] = None
            
            elif method == "shutdown":
                response["result"] = None
            
            else:
                response["result"] = None
            
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": msg_id if 'msg_id' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
