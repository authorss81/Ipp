# ipp-test: Unit test framework with describe/it/expect
# v2.0.14 — bundled stdlib package

export var _passed = 0
export var _failed = 0
export var _failures = []

export func describe(name, fn) {
    fn()
}

export func it(name, fn) {
    try {
        fn()
        _passed = _passed + 1
        print("  ok " + name)
    } catch e {
        _failed = _failed + 1
        _failures = _failures + [name + ": " + e]
        print("  FAIL " + name)
        print("    " + e)
    }
}

export func expect(val) {
    return Expectation(val)
}

export class Expectation {
    func init(val) { self.val = val }

    func to_equal(expected) {
        assert self.val == expected, "expected " + str(expected) + " but got " + str(self.val)
    }

    func to_be_true() {
        assert self.val == true, "expected true but got " + str(self.val)
    }

    func to_be_false() {
        assert self.val == false, "expected false but got " + str(self.val)
    }

    func to_contain(item) {
        assert self.val.contains(item) == true, str(self.val) + " does not contain " + str(item)
    }

    func to_be_nil() {
        assert self.val == nil, "expected nil but got " + str(self.val)
    }

    func to_be_close_to(expected, tol=0.001) {
        assert isclose(self.val, expected), "expected ~" + str(expected) + " but got " + str(self.val)
    }

    func to_throw() {
        var threw = false
        try { self.val() } catch e { threw = true }
        assert threw == true, "expected function to throw but it did not"
    }

    func negate() { return NotExpectation(self.val) }
}

export class NotExpectation {
    func init(val) { self.val = val }

    func to_equal(expected) {
        assert self.val != expected, "expected not " + str(expected) + " but got " + str(self.val)
    }

    func to_be_true() {
        assert self.val != true, "expected not true"
    }

    func to_contain(item) {
        assert self.val.contains(item) == false, str(self.val) + " contains " + str(item)
    }
}

export func run_all() {
    print("=== Test Results ===")
    print("Passed: " + str(_passed))
    print("Failed: " + str(_failed))
    if _failed > 0 {
        print("Failures:")
        for f in _failures {
            print("  FAIL " + f)
        }
        return false
    }
    return true
}
