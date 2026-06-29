# v2.0.25 — breakpoint() in class methods
print("=== v2.0.25 breakpoint in class ===")

class Counter {
    var count = 0

    func init(n) {
        self.count = n
        breakpoint()
    }

    func increment() {
        breakpoint()
        self.count = self.count + 1
    }

    func get_count() {
        return self.count
    }
}

var c = Counter(10)
assert c.get_count() == 10
print("  PASS: breakpoint in init")

c.increment()
assert c.get_count() == 11
print("  PASS: breakpoint in method")

class Box {
    var val = nil

    func store(v) {
        breakpoint()
        self.val = v
    }
    func retrieve() {
        breakpoint()
        return self.val
    }
}

var b = Box()
b.store(42)
assert b.retrieve() == 42
print("  PASS: breakpoint in store/retrieve")

print("All v2.0.25 class edge case tests passed!")
