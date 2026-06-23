# v2.0.23 — Physics Engine Visual Demo
# Bouncing balls + stacking boxes with canvas rendering.
# Usage: python main.py tests/v2_0_23/demo_physics.ipp

import { Space, Body, get_x, get_y } from "ipp-physics"

canvas_open()

var space = Space(0, 9.81)
var SCALE = 30

var ground = Body(space, "box", "static", 0, 18, 30, 1)
var wall_l = Body(space, "box", "static", -14, 10, 1, 20)
var wall_r = Body(space, "box", "static", 14, 10, 1, 20)

var all_bodies = []
var colors = ["red", "green", "blue", "yellow", "cyan"]

for i in range(5) {
    var x = -10 + i * 5
    var b = Body(space, "circle", "dynamic", x, -5, 1, 1, 0.5, 1.0, 0.6, 0.3)
    all_bodies = all_bodies + [b]
}

for i in range(4) {
    var b = Body(space, "box", "dynamic", 0, -(i * 1.5), 1.5, 1.5, 0.5, 0.5, 0.2, 0.5)
    all_bodies = all_bodies + [b]
    colors = colors + ["magenta"]
}
for i in range(3) {
    var b = Body(space, "box", "dynamic", 8, -(i * 2), 1, 1, 0.5, 0.3, 0.3, 0.8)
    all_bodies = all_bodies + [b]
    colors = colors + ["orange"]
}

canvas_run(func(dt) {
    canvas_clear("black")
    physics_step(space, dt)

    for i in range(len(all_bodies)) {
        var body = all_bodies[i]
        var cx = get_x(body) * SCALE + 300
        var cy = get_y(body) * SCALE + 300

        if body.shape == "box" {
            canvas_rect(cx - body.w * SCALE / 2, cy - body.h * SCALE / 2,
                       body.w * SCALE, body.h * SCALE, colors[i])
        } else {
            canvas_circle(cx, cy, body.radius * SCALE, colors[i])
        }
    }
}, 60)
