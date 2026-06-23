# v2.0.23 — Physics Engine Visual Demo
# Bouncing balls + stacking boxes with canvas rendering.
# Usage: python main.py tests/v2_0_23/demo_physics.ipp

import { Space, Body, get_x, get_y } from "ipp-physics"

canvas_open(800, 600)
canvas_color("black")
canvas_bg("black")

# ── Physics ──
var space = Space(0, 9.81)
var SCALE = 30  # pixels per physics unit

# Ground
var ground = Body(space, "box", "static", 0, 18, 30, 1, 0.5, 1.0, 0.5, 0.3)

# Left wall
var wall_l = Body(space, "box", "static", -14, 10, 1, 20, 0.5)

# Right wall
var wall_r = Body(space, "box", "static", 14, 10, 1, 20, 0.5)

# Falling balls
var balls = []
for i in range(5) {
    var x = -10 + i * 5
    var b = Body(space, "circle", "dynamic", x, -5, 1, 1, 0.5, 1.0, 0.6, 0.3)
    balls = balls + [b]
}

# Stacking boxes
var boxes = []
for i in range(4) {
    var b = Body(space, "box", "dynamic", 0, -(i * 1.5), 1.5, 1.5, 0.5, 0.5, 0.2, 0.5)
    boxes = boxes + [b]
}

# Hit boxes
for i in range(3) {
    var b = Body(space, "box", "dynamic", 8, -(i * 2), 1, 1, 0.5, 0.3, 0.3, 0.8)
    boxes = boxes + [b]
}

var colors = []
for i in range(5) {
    colors = colors + [["red"], ["green"], ["blue"], ["yellow"], ["cyan"]]
}
for i in range(len(boxes)) {
    colors = colors + [["magenta"], ["white"], ["orange"]]
}

canvas_run(800, 600, func(dt) {
    canvas_color("black")
    canvas_bg("black")
    canvas_clear()

    physics_step(space, dt)

    # Draw all bodies
    var all_bodies = balls + boxes
    for i in range(len(all_bodies)) {
        var body = all_bodies[i]
        var cx = get_x(body) * SCALE + 400
        var cy = get_y(body) * SCALE + 200
        var c = colors[i][0]

        if body.shape == "box" {
            canvas_color(c)
            var hw = body.w * SCALE / 2
            var hh = body.h * SCALE / 2
            canvas_rect(cx - hw, cy - hh, body.w * SCALE, body.h * SCALE)
        } else {
            canvas_color(c)
            canvas_circle(cx, cy, body.radius * SCALE)
        }
    }

    # Collision effects: flash on hit
    canvas_color("white")
    var evts = physics_space_poll_collisions(space)
    for e in evts {
        canvas_text("HIT", 10, 10, 20)
    }

    canvas_color("gray")
    canvas_text("ESC to quit", 700, 10, 12)
})
