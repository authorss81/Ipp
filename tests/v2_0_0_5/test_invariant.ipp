# v2.0.0.5 — @invariant decorator test
# Tests that class invariants are enforced after field mutations in debug mode

class BoundedInt {
    @invariant(func(self) {
        return self.val >= self.min_val and self.val <= self.max_val
    })
    func init(val, min_val, max_val) {
        self.val = val
        self.min_val = min_val
        self.max_val = max_val
    }
    func set(v) { self.val = v }
    func set_min(v) { self.min_val = v }
    func get() { return self.val }
}

# Test valid operations
inst = BoundedInt(50, 0, 100)
assert(inst.get() == 50)

inst.set(75)
assert(inst.get() == 75)

inst.set(0)
assert(inst.get() == 0)

inst.set(100)
assert(inst.get() == 100)

# Test invariant violation is caught
var caught = false
try {
    inst.set(-5)
} catch e {
    caught = true
}
assert(caught, "Expected invariant violation for value -5")

caught = false
try {
    inst.set(200)
} catch e {
    caught = true
}
assert(caught, "Expected invariant violation for value 200")

# Test field mutation through non-method path
inst2 = BoundedInt(10, 0, 20)
caught = false
try {
    inst2.set(-1)
} catch e {
    caught = true
}
assert(caught, "Expected invariant violation for -1")

# Multiple @invariant decorators
class MultiInvariant {
    @invariant(func(self) { return self.x > 0 })
    @invariant(func(self) { return self.y < 100 })
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func set_x(v) { self.x = v }
    func set_y(v) { self.y = v }
}

mi = MultiInvariant(10, 50)
assert(mi.x == 10)
assert(mi.y == 50)

# Violate first invariant
caught = false
try {
    mi.set_x(-5)
} catch e {
    caught = true
}
assert(caught, "Expected invariant violation for x <= 0")

# Violate second invariant
caught = false
try {
    mi.set_y(200)
} catch e {
    caught = true
}
assert(caught, "Expected invariant violation for y >= 100")

print("All invariant tests passed")
