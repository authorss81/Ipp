# v1.3.2 Bug Fix Tests

print("=== v1.3.2 Bug Fix Tests ===")

# ─── v1.1.0: Class instantiation + property assignment ───────────────────────
print("\n--- Class instantiation ---")

class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __add__(other) {
        return Vec2(self.x + other.x, self.y + other.y)
    }
    func __str__() {
        return "(" + str(self.x) + ", " + str(self.y) + ")"
    }
}

var a = Vec2(1, 2)
var b = Vec2(3, 4)
print(a.x)      # Should print 1
print(a.y)      # Should print 2
print(b.x)      # Should print 3

var c = a + b
print(c.x)      # Should print 4
print(c.y)      # Should print 6

# ─── BUG-N6: __str__ called by print ─────────────────────────────────────────
print("\n--- __str__ method ---")

class Point {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __str__() {
        return "Point(" + str(self.x) + ", " + str(self.y) + ")"
    }
}

var p = Point(5, 10)
print(p)           # Should print: Point(5, 10)
print(str(p))      # Should print: Point(5, 10)

# ─── BUG-N1: Private member protection ───────────────────────────────────────
print("\n--- Private members ---")

class Bank {
    func init(balance) {
        self.balance = balance
        self.__pin = 1234
    }
    func getPin() {
        return self.__pin    # internal access OK
    }
    func getBalance() {
        return self.balance
    }
}

var account = Bank(1000)
print(account.balance)       # Should print: 1000
print(account.getBalance())  # Should print: 1000
print(account.getPin())      # Should print: 1234

var error_caught = false
try {
    var x = account.__pin    # Should throw: private field access
} catch e {
    error_caught = true
    print("Private access blocked: " + str(error_caught))
}

# ─── BUG-N2: Recursion limit ─────────────────────────────────────────────────
print("\n--- Recursion limit ---")

func fib(n) {
    if n <= 1 { return n }
    return fib(n - 1) + fib(n - 2)
}

print(fib(10))   # Should print: 55

var rec_error_caught = false
try {
    func inf() { return inf() }
    inf()
} catch e {
    rec_error_caught = true
    print("Recursion limit hit: " + str(rec_error_caught))
}

print("\n=== All v1.3.2 tests passed! ===")
# v1.3.2 Feature Tests
# Tests for BUG-NEW-M5 (VM Upvalues by Reference) and BUG-NEW-M6 (Set type)
=======
>>>>>>> Stashed changes

print("=== v1.3.2 Bug Fix Tests ===")

# ─── v1.1.0: Class instantiation + property assignment ───────────────────────
print("\n--- Class instantiation ---")

class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __add__(other) {
        return Vec2(self.x + other.x, self.y + other.y)
    }
    func __str__() {
        return "(" + str(self.x) + ", " + str(self.y) + ")"
    }
}

var a = Vec2(1, 2)
var b = Vec2(3, 4)
print(a.x)      # Should print 1
print(a.y)      # Should print 2
print(b.x)      # Should print 3

var c = a + b
print(c.x)      # Should print 4
print(c.y)      # Should print 6

# ─── BUG-N6: __str__ called by print ─────────────────────────────────────────
print("\n--- __str__ method ---")

class Point {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __str__() {
        return "Point(" + str(self.x) + ", " + str(self.y) + ")"
    }
}

var p = Point(5, 10)
print(p)           # Should print: Point(5, 10)
print(str(p))      # Should print: Point(5, 10)

# ─── BUG-N1: Private member protection ───────────────────────────────────────
print("\n--- Private members ---")

class Bank {
    func init(balance) {
        self.balance = balance
        self.__pin = 1234
    }
    func getPin() {
        return self.__pin    # internal access OK
    }
    func getBalance() {
        return self.balance
    }
}

var account = Bank(1000)
print(account.balance)       # Should print: 1000
print(account.getBalance())  # Should print: 1000
print(account.getPin())      # Should print: 1234

var error_caught = false
try {
    var x = account.__pin    # Should throw: private field access
} catch e {
    error_caught = true
    print("Private access blocked: " + str(error_caught))
}

# ─── BUG-N2: Recursion limit ─────────────────────────────────────────────────
print("\n--- Recursion limit ---")

func fib(n) {
    if n <= 1 { return n }
    return fib(n - 1) + fib(n - 2)
}

print(fib(10))   # Should print: 55

var rec_error_caught = false
try {
    func inf() { return inf() }
    inf()
} catch e {
    rec_error_caught = true
    print("Recursion limit hit: " + str(rec_error_caught))
}

print("\n=== All v1.3.2 tests passed! ===")
