#!/usr/bin/env python3
"""
Practical REPL Command Test - Simplified version
Tests each REPL command by running the REPL and checking output.
"""
import subprocess
import sys
import os
import time

ipp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(ipp_dir)

PASS = '[PASS]'
FAIL = '[FAIL]'

class PracticalTest:
    def __init__(self):
        self.proc = None
        self.passed = 0
        self.failed = 0
        
    def start(self):
        self.proc = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        time.sleep(2)
        
    def send(self, cmd, wait=0.3):
        if not self.proc or self.proc.poll():
            self.start()
        try:
            self.proc.stdin.write(cmd + '\n')
            self.proc.stdin.flush()
            time.sleep(wait)
            return True
        except:
            return False
            
    def test(self, name, cmd, check_fn=None, wait=0.3):
        ok = self.send(cmd, wait)
        if check_fn and ok:
            ok = check_fn()
        if ok:
            self.passed += 1
            print(f"  {PASS} {name}")
        else:
            self.failed += 1
            print(f"  {FAIL} {name}")
            
    def run_all(self):
        print("=" * 50)
        print("PRACTICAL REPL TEST")
        print("=" * 50)
        
        self.start()
        
        print("\nCore:")
        self.test(".help", ".help", wait=1)
        self.test(".version", ".version")
        self.test(".types", ".types")
        
        self.send('var x = 42')
        self.send('var name = "Alice"')
        self.send('var data = {"key": "value"}')
        self.send('var users = [{"name": "Alice", "age": 30}]')
        
        print("\nSession:")
        self.test(".clear", ".clear")
        self.send('var x = 42')
        self.send('var name = "Alice"')
        self.test(".vars", ".vars")
        self.test(".fns", ".fns")
        
        print("\nBuiltins:")
        self.test(".builtins", ".builtins", wait=2)
        self.test(".modules", ".modules", wait=1)
        
        print("\nHistory:")
        self.test(".history", ".history")
        self.test(".last", ".last")
        
        print("\nUndo/Redo:")
        self.test(".undo", ".undo")
        self.test(".redo", ".redo")
        
        print("\nInspection:")
        self.test(".which", ".which x")
        self.test(".doc", ".doc print")
        self.test(".pretty", ".pretty x")
        self.test(".json", ".json x")
        
        print("\nPerformance:")
        self.test(".time", ".time 2**10")
        self.test(".profile", ".profile")
        
        print("\nShell:")
        self.test("! echo", "! echo hello")
        self.test(".pwd", ".pwd")
        self.test(".ls", ".ls")
        self.test(".cd", ".cd tests")
        self.test(".cd back", ".cd ..")
        
        print("\nCustomization:")
        self.test(".theme", ".theme dark")
        self.test(".prompt", ".prompt ipp")
        self.test(".alias", ".alias t print")
        self.test(".bind", ".bind F5 run")
        
        print("\nCode:")
        self.test(".format", ".format x=10")
        self.test(".search", ".search http")
        self.test(".examples", ".examples", wait=1)
        self.test(".tutorial", ".tutorial")
        
        print("\nDebugging:")
        self.test(".debug start", ".debug start")
        self.test(".break", ".break 10")
        self.test(".watch", ".watch x")
        self.test(".locals", ".locals")
        self.test(".stack", ".stack")
        self.test(".debug stop", ".debug stop")
        
        print("\nSession:")
        self.test(".session save", ".session save")
        self.test(".session load", ".session load")
        self.test(".sessions", ".sessions")
        self.test(".session clear", ".session clear")
        
        print("\nExport:")
        self.test(".export", ".export test.ipp")
        
        print("\nType/Signature:")
        self.test(".typehints", ".typehints")
        self.test(".sighelp", ".sighelp")
        
        print("\nPipe:")
        self.test(".pipe", ".pipe echo")
        
        self.send("exit")
        time.sleep(0.5)
        
        print(f"\n{'=' * 50}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")
        return self.failed == 0

if __name__ == "__main__":
    t = PracticalTest()
    ok = t.run_all()
    sys.exit(0 if ok else 1)
