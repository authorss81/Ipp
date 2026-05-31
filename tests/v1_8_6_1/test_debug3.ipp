var defaults = {"color": "red", "size": 10, "visible": true}
var custom = {"size": 20, "weight": 5}
var merged = {**defaults, **custom}
print(merged)

var a = {"x": 1, "y": 2}
var b = {"y": 99, "z": 3}
var c = {**a, **b}
print(c)

var base = {"debug": false, "version": "1.0"}
var dev = {**base, "debug": true, "extra": "dev-only"}
print(dev)
print("debug value:", dev["debug"])
print("debug == true:", dev["debug"] == true)
