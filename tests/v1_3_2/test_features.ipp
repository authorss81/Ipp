# v1.3.2 Feature Tests
# Tests for BUG-NEW-M5 (VM Upvalues by Reference) and BUG-NEW-M6 (Set type)

print("=== v1.3.2 Tests ===")

# ─── BUG-NEW-M5: VM Upvalues by Reference ────────────────────────────────────

print("\n--- BUG-NEW-M5: VM Upvalues ---")

# Test 1: Basic closure captures variable by reference
func make_counter() {
    var count = 0
    func increment() {
        count = count + 1
        return count
    }
    return increment
}

var counter = make_counter()
print(counter())   # expected: 1
print(counter())   # expected: 2
print(counter())   # expected: 3

# Test 2: Two closures share the same upvalue
func make_pair() {
    var x = 10
    func getter() { return x }
    func setter(v) { x = v }
    return [getter, setter]
}

var pair = make_pair()
var get = pair[0]
var setter = pair[1]
print(get())       # expected: 10
setter(99)
print(get())       # expected: 99

# Test 3: Nested closures (transitive upvalue capture)
func outer() {
    var n = 0
    func middle() {
        func inner() {
            n = n + 1
            return n
        }
        return inner
    }
    return middle()
}

var fn = outer()
print(fn())        # expected: 1
print(fn())        # expected: 2

# Test 4: Closure in loop — each iteration captures its own value
var fns = []
var i = 0
while i < 3 {
    var captured = i
    func make_fn(v) {
        func f() { return v }
        return f
    }
    fns.push(make_fn(captured))
    i = i + 1
}
print(fns[0]())    # expected: 0
print(fns[1]())    # expected: 1
print(fns[2]())    # expected: 2

# Test 5: Upvalue survives enclosing scope exit (heap migration)
func make_adder(x) {
    func add(y) { return x + y }
    return add
}

var add5 = make_adder(5)
var add10 = make_adder(10)
print(add5(3))     # expected: 8
print(add10(3))    # expected: 13

# ─── BUG-NEW-M6: Set Data Type ───────────────────────────────────────────────

print("\n--- BUG-NEW-M6: Set Type ---")

# Test 6: Create empty set and add elements
var s = set()
s.add(1)
s.add(2)
s.add(3)
s.add(2)           # duplicate — ignored
print(s.len())     # expected: 3

# Test 7: set() from list removes duplicates
var nums = [1, 2, 2, 3, 3, 3, 4]
var unique = set(nums)
print(unique.len()) # expected: 4

# Test 8: contains / remove
var fruits = set()
fruits.add("apple")
fruits.add("banana")
fruits.add("cherry")
print(fruits.contains("banana"))  # expected: true
fruits.remove("banana")
print(fruits.contains("banana"))  # expected: false
print(fruits.len())               # expected: 2

# Test 9: type() returns "set"
print(type(s))     # expected: set

# Test 10: len() on set
var empty = set()
print(len(empty))  # expected: 0
empty.add("x")
print(len(empty))  # expected: 1

# Test 11: Set algebra — union
var a = set([1, 2, 3])
var b = set([3, 4, 5])
var u = a.union(b)
print(u.len())     # expected: 5

# Test 12: Set algebra — intersection
var inter = a.intersection(b)
print(inter.len()) # expected: 1
print(inter.contains(3)) # expected: true

# Test 13: Set algebra — difference
var diff = a.difference(b)
print(diff.len())  # expected: 2
print(diff.contains(1)) # expected: true
print(diff.contains(3)) # expected: false

# Test 14: is_subset / is_superset
var sub = set([1, 2])
print(sub.is_subset(a))    # expected: true
print(a.is_superset(sub))  # expected: true
print(b.is_subset(a))      # expected: false

# Test 15: clear()
var c = set([10, 20, 30])
print(c.len())  # expected: 3
c.clear()
print(c.len())  # expected: 0

print("\n=== All v1.3.2 tests complete ===")
