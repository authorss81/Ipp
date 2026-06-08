var start = time.now()
time.sleep(0.01)
var elapsed = time.since(start)
assert elapsed >= 0.01
assert elapsed < 0.1

var ms = time.ms()
assert ms > 0

print("time builtins ok")
