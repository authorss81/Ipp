# v2.0.22 — GPU Demo: Rotating colored triangle
# Run: python main.py tests/v2_0_22/demo_gpu.ipp

import { init_window, render_loop } from "ipp-gpu"

var ctx = init_window(800, 600, "Ipp GPU — Rotating Triangle")

# Custom shader with time uniform for rotation
var vs_src = """
#version 330 core
layout(location = 0) in vec2 a_pos;
layout(location = 1) in vec3 a_color;
uniform float u_time;
out vec3 v_color;
void main() {
    float angle = u_time;
    float c = cos(angle);
    float s = sin(angle);
    vec2 rotated = vec2(a_pos.x * c - a_pos.y * s, a_pos.x * s + a_pos.y * c);
    gl_Position = vec4(rotated, 0.0, 1.0);
    v_color = a_color;
}
"""

var fs_src = """
#version 330 core
in vec3 v_color;
out vec4 frag_color;
void main() {
    frag_color = vec4(v_color, 1.0);
}
"""

# Compile shaders
var vs = gpu_create_shader("vertex", vs_src)
var fs = gpu_create_shader("fragment", fs_src)
var prog = gpu_create_program(vs, fs)
gpu_use_program(prog)
gpu_delete_shader(vs)
gpu_delete_shader(fs)

# Triangle: position(x,y) + color(r,g,b) — interleaved, 5 floats per vertex
var vertices = [
     0.0,  0.6,  1.0, 0.0, 0.0,   # top: red
    -0.5, -0.5,  0.0, 1.0, 0.0,   # bottom-left: green
     0.5, -0.5,  0.0, 0.0, 1.0,   # bottom-right: blue
]
var buf = gpu_create_buffer(vertices)
gpu_bind_buffer(buf)
gpu_vertex_attrib(prog, "a_pos", 2, 20, 0)
gpu_vertex_attrib(prog, "a_color", 3, 20, 8)

var elapsed = 0.0
var frame_count = 0

print("=== GPU Demo: Rotating Colored Triangle ===")
print("Close the window or press ESC to exit.")

render_loop(ctx, func(dt, events) {
    # Check for ESC or quit event
    for e in events {
        if e["type"] == "quit" { return "quit" }
        if e["type"] == "key_down" and e["key"] == "escape" { return "quit" }
    }

    elapsed = elapsed + dt
    frame_count = frame_count + 1

    gpu_clear(0.05, 0.05, 0.1, 1.0)
    gpu_set_uniform(prog, "u_time", elapsed)
    gpu_draw("triangles", 3)

    if frame_count % 60 == 0 {
        print("  Frame " + str(frame_count) + " | FPS: " + str(int(1.0 / dt)))
    }
})

print("Demo closed. Total frames: " + str(frame_count))
