# v1.9.12: export keyword — explicit public API

export func area_circle(r) {
    return 3.14159 * r * r
}

export func area_rect(w, h) {
    return w * h
}

export var GOLDEN_RATIO = 1.6180339887

# Private — not exported
func _validate_positive(x) {
    assert x > 0, "value must be positive"
}
var _calculation_count = 0
