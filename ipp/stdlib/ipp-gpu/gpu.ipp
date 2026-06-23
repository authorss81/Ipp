# ipp-gpu — GPU Rendering wrapper (v2.0.22)
# Practical usage:
#   import { init_window, render_loop } from "ipp-gpu"
#   var ctx = init_window(800, 600)
#   render_loop(ctx, func(dt, events) { ... })

# Default shaders with time + color uniforms
export var VERTEX_SHADER_SRC = """
#version 330 core
layout(location = 0) in vec2 a_pos;
layout(location = 1) in vec3 a_color;
out vec3 v_color;
void main() {
    gl_Position = vec4(a_pos, 0.0, 1.0);
    v_color = a_color;
}
"""

export var FRAGMENT_SHADER_SRC = """
#version 330 core
in vec3 v_color;
out vec4 frag_color;
void main() {
    frag_color = vec4(v_color, 1.0);
}
"""

# ── Context object ──
# Stores window, program, buffers for automatic cleanup

export func init_window(width=800, height=600, title="Ipp GPU") {
    var result = gpu_init(width, height, title)
    var vs = gpu_create_shader("vertex", VERTEX_SHADER_SRC)
    var fs = gpu_create_shader("fragment", FRAGMENT_SHADER_SRC)
    var prog = gpu_create_program(vs, fs)
    gpu_use_program(prog)
    gpu_delete_shader(vs)
    gpu_delete_shader(fs)
    return {"window": result, "program": prog, "width": width, "height": height}
}

# ── Full render loop ──
# Usage:
#   render_loop(ctx, func(dt, events) {
#       gpu_clear(0.1, 0.1, 0.2, 1.0)
#       # ... draw calls ...
#       # events is a list of event dicts from gpu_poll_events()
#       # Return "quit" to exit the loop
#   })
export func render_loop(ctx, render_fn) {
    while gpu_is_open() {
        var events = gpu_poll_events()
        var dt = gpu_dt()
        var should_quit = render_fn(dt, events)
        gpu_swap()
        if should_quit == "quit" { break }
    }
    gpu_close()
}

# ── Quick triangle demo ──
# Draws a colored triangle centered in NDC space.
# vertices: list of [x, y, r, g, b]
export func draw_colored_triangle(prog, vertices) {
    var buf = gpu_create_buffer(vertices)
    gpu_bind_buffer(buf)
    gpu_vertex_attrib(prog, "a_pos", 2, 20, 0)
    gpu_vertex_attrib(prog, "a_color", 3, 20, 8)
    gpu_draw("triangles", 3)
    gpu_delete_buffer(buf)
}
