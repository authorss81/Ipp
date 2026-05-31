# Test basic property getter/setter (v1.8.7)
class Foo {
    var _val = 0

    prop hp {
        get {
            return self._val
        }
        set(v) {
            self._val = v
        }
    }
}

var f = Foo()
assert f.hp == 0
f.hp = 42
assert f.hp == 42
assert f._val == 42
print("OK")
