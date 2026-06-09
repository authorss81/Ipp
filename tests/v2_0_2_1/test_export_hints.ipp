# v2.0.2.1 — @export Range Hints + @onchange Callback
print("test export hints begin")

class Slider {
    @export(min=0, max=10) var value = 5

    @onchange("value")
    func on_change(old, new) {
        self.last_change = new - old
    }
}

var s = Slider()
assert s.value == 5
s.value = 8
assert s.last_change == 3
s.value = 3
assert s.last_change == -5

# Verify exports metadata includes hints
var ex = Slider.get_exports()
assert "value" in ex
var val, hints = ex["value"]
assert hints["min"] == 0
assert hints["max"] == 10

print("test export hints passed")
