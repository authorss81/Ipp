# Test property edge cases (v1.8.7)
# 1. Read-only property (no setter)
class ReadOnly {
    prop val {
        get {
            return 42
        }
    }
}

var ro = ReadOnly()
assert ro.val == 42

# 2. Write-only property (no getter — not really useful but valid syntax)
class WriteOnly {
    var _x = 0
    prop x {
        set(v) {
            self._x = v
        }
    }
}
var wo = WriteOnly()
wo.x = 99
assert wo._x == 99

# 3. Property with custom setter param name
class CustomParam {
    var _name = ""
    prop name {
        get {
            return self._name
        }
        set(val) {
            self._name = val
        }
    }
}
var cp = CustomParam()
cp.name = "hello"
assert cp.name == "hello"
assert cp._name == "hello"

# 4. Property returning computed value
class Computed {
    var _x = 10
    var _y = 20
    prop sum {
        get {
            return self._x + self._y
        }
    }
}
var comp = Computed()
assert comp.sum == 30

# 5. Multiple properties on same class
class MultiProp {
    var _a = 1
    var _b = 2
    prop a {
        get { return self._a }
        set(v) { self._a = v }
    }
    prop b {
        get { return self._b }
        set(v) { self._b = v }
    }
}
var mp = MultiProp()
assert mp.a == 1
assert mp.b == 2
mp.a = 10
mp.b = 20
assert mp.a == 10
assert mp.b == 20

# 6. Property with side effects in getter
class SideEffect {
    var _count = 0
    prop val {
        get {
            self._count = self._count + 1
            return self._count
        }
    }
}
var se = SideEffect()
assert se.val == 1
assert se.val == 2
assert se.val == 3
assert se._count == 3

print("OK")
