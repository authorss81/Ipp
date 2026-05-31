var defaults = {"color": "red", "size": 10, "visible": true}
var custom = {"size": 20, "weight": 5}

# Basic merge
var merged = {**defaults, **custom}
assert merged["color"] == "red"
assert merged["size"] == 20
assert merged["weight"] == 5
assert merged["visible"] == true

# Order matters: later keys win
var a = {"x": 1, "y": 2}
var b = {"y": 99, "z": 3}
var c = {**a, **b}
assert c["x"] == 1
assert c["y"] == 99
assert c["z"] == 3

# Inline additions alongside spread
var base = {"debug": false, "version": "1.0"}
var dev = {**base, "debug": true, "extra": "dev-only"}
assert dev["debug"] == true
assert dev["version"] == "1.0"
assert dev["extra"] == "dev-only"

# Single spread
var alone = {**defaults}
assert alone["color"] == "red"
assert alone["size"] == 10

# Empty spread (no-op)
var empty = {}
var result = {**empty, "a": 1}
assert result["a"] == 1

# Three-way merge with inline
var x = {"a": 1}
var y = {"b": 2}
var z = {"c": 3}
var all = {**x, **y, **z, "d": 4}
assert all == {"a": 1, "b": 2, "c": 3, "d": 4}

# Override chain
var low = {"value": 10, "priority": "low"}
var high = {"value": 99, "priority": "high"}
var final = {**low, **high}
assert final["value"] == 99
assert final["priority"] == "high"

print("All dict spread tests passed!")
