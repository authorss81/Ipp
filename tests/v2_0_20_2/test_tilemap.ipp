import { Camera, TilemapRenderer } from "ipp-canvas"

# Camera offset math
var cam = Camera(100, 50)
var screen_pos = cam.world_to_screen(150, 80)
assert screen_pos[0] == 50
assert screen_pos[1] == 30

var world_pos = cam.screen_to_world(50, 30)
assert world_pos[0] == 150
assert world_pos[1] == 80

cam.move(10, 5)
assert cam.x == 110
assert cam.y == 55

# Camera defaults
var cam2 = Camera()
assert cam2.x == 0
assert cam2.y == 0

# Tilemap render without crash
var map_data = [
    [0, 0, 1, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 1, 0, 0],
]
var palette = {}
palette["0"] = "black"
palette["1"] = "green"
var renderer = TilemapRenderer(map_data, 32, 32, palette)
renderer.draw()
renderer.draw(cam, 600, 400)

print("All v2.0.20.2 tilemap tests passed!")
