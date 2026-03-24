# Test game helpers

import "game_helpers.ipp"

var v1 = Vector2(3, 4)
var v2 = Vector2(1, 2)
print(v1.add(v2))
print(v1.length())

var v3 = Vector3(1, 2, 3)
print(v3)

print(lerp(0, 10, 0.5))
print(clamp(15, 0, 10))

print("=== Done ===")
