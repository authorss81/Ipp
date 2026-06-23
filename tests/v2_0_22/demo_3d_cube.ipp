# v2.0.22 — 3D Rotating Cube Demo
# Requires PyOpenGL + pygame
# Usage: python main.py tests/v2_0_22/demo_3d_cube.ipp

import { init_3d, render_loop, create_colored_cube, draw_cube, delete_cube } from "ipp-gpu"

var WIDTH = 800
var HEIGHT = 600
var ctx = init_3d(WIDTH, HEIGHT, "Ipp GPU — 3D Rotating Cube")
var prog = ctx["program"]
var cube = create_colored_cube(prog)

# Projection matrix (45-degree FOV, 4:3 aspect, 0.1 near, 100 far)
var proj = gpu_mat4_perspective(0.785, WIDTH / HEIGHT, 0.1, 100.0)

# Camera: look at origin from distance 4
var eye = [0.0, 0.0, 4.0]
var center = [0.0, 0.0, 0.0]
var up = [0.0, 1.0, 0.0]
var view = gpu_mat4_look_at(eye, center, up)

var view_proj = gpu_mat4_multiply(proj, view)

var elapsed = 0.0

render_loop(ctx, func(dt, events) {
    for e in events {
        if e["type"] == "quit" { return "quit" }
        if e["type"] == "key_down" and e["key"] == "escape" { return "quit" }
    }

    elapsed = elapsed + dt

    # Model matrix: rotate around Y axis
    var model = gpu_mat4_identity()
    model = gpu_mat4_rotate(model, elapsed, 0, 1, 0)
    model = gpu_mat4_rotate(model, elapsed * 0.5, 1, 0, 0)

    var mvp = gpu_mat4_multiply(view_proj, model)

    gpu_clear(0.05, 0.05, 0.1, 1.0)
    gpu_set_uniform_matrix(prog, "u_mvp", mvp)
    draw_cube(cube)
})
