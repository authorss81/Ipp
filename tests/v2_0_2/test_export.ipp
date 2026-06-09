# v2.0.2 — @export Annotation for Editor-Visible Variables
print("test export begin")

class Enemy {
    @export var speed = 100.0
    @export var health = 50
}

var e = Enemy()
assert e.speed == 100.0
assert e.health == 50

# Exports are introspectable
var exports = Enemy.get_exports()
assert "speed" in exports
assert "health" in exports
assert exports["speed"] == 100.0

print("test export passed")
