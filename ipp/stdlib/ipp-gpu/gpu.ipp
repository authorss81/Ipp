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

# ── 3D Shaders ──

export var VERTEX_3D_SRC = """
#version 330 core
layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec3 a_color;
uniform mat4 u_mvp;
out vec3 v_color;
void main() {
    gl_Position = u_mvp * vec4(a_pos, 1.0);
    v_color = a_color;
}
"""

export var FRAGMENT_3D_SRC = """
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

# ── 3D Context ──
export func init_3d(width=800, height=600, title="Ipp GPU 3D") {
    var result = gpu_init(width, height, title)
    var vs = gpu_create_shader("vertex", VERTEX_3D_SRC)
    var fs = gpu_create_shader("fragment", FRAGMENT_3D_SRC)
    var prog = gpu_create_program(vs, fs)
    gpu_use_program(prog)
    gpu_delete_shader(vs)
    gpu_delete_shader(fs)
    gpu_enable_depth()
    return {"window": result, "program": prog, "width": width, "height": height}
}

# ── Full render loop ──
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
export func draw_colored_triangle(prog, vertices) {
    var buf = gpu_create_buffer(vertices)
    gpu_bind_buffer(buf)
    gpu_vertex_attrib(prog, "a_pos", 2, 20, 0)
    gpu_vertex_attrib(prog, "a_color", 3, 20, 8)
    gpu_draw("triangles", 3)
    gpu_delete_buffer(buf)
}

# ── Quick 3D cube ──
# Returns { vao, vertex_count } for a colored cube.
# Caller must set u_mvp uniform before drawing.
export func create_colored_cube(prog) {
    var vertices = [
        # Front face (red)
        -0.5, -0.5, 0.5, 1.0, 0.0, 0.0,
         0.5, -0.5, 0.5, 1.0, 0.0, 0.0,
         0.5,  0.5, 0.5, 1.0, 0.0, 0.0,
        -0.5,  0.5, 0.5, 1.0, 0.0, 0.0,
        # Back face (green)
         0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
        -0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
        -0.5,  0.5, -0.5, 0.0, 1.0, 0.0,
         0.5,  0.5, -0.5, 0.0, 1.0, 0.0,
        # Top face (blue)
        -0.5, 0.5,  0.5, 0.0, 0.0, 1.0,
         0.5, 0.5,  0.5, 0.0, 0.0, 1.0,
         0.5, 0.5, -0.5, 0.0, 0.0, 1.0,
        -0.5, 0.5, -0.5, 0.0, 0.0, 1.0,
        # Bottom face (yellow)
        -0.5, -0.5, -0.5, 1.0, 1.0, 0.0,
         0.5, -0.5, -0.5, 1.0, 1.0, 0.0,
         0.5, -0.5,  0.5, 1.0, 1.0, 0.0,
        -0.5, -0.5,  0.5, 1.0, 1.0, 0.0,
        # Right face (magenta)
         0.5, -0.5,  0.5, 1.0, 0.0, 1.0,
         0.5, -0.5, -0.5, 1.0, 0.0, 1.0,
         0.5,  0.5, -0.5, 1.0, 0.0, 1.0,
         0.5,  0.5,  0.5, 1.0, 0.0, 1.0,
        # Left face (cyan)
        -0.5, -0.5, -0.5, 0.0, 1.0, 1.0,
        -0.5, -0.5,  0.5, 0.0, 1.0, 1.0,
        -0.5,  0.5,  0.5, 0.0, 1.0, 1.0,
        -0.5,  0.5, -0.5, 0.0, 1.0, 1.0,
    ]
    var indices = [
        0,1,2, 0,2,3,       # front
        4,5,6, 4,6,7,       # back
        8,9,10, 8,10,11,    # top
        12,13,14, 12,14,15,  # bottom
        16,17,18, 16,18,19,  # right
        20,21,22, 20,22,23,  # left
    ]
    var vao = gpu_create_vao()
    gpu_bind_vao(vao)
    var buf = gpu_create_buffer(vertices)
    gpu_bind_buffer(buf)
    gpu_vertex_attrib(prog, "a_pos", 3, 24, 0)
    gpu_vertex_attrib(prog, "a_color", 3, 24, 12)
    var ebo = gpu_create_index_buffer(indices)
    return {"vao": vao, "count": 36, "program": prog, "idx_buf": ebo, "vtx_buf": buf}
}

export func draw_cube(cube) {
    gpu_bind_vao(cube["vao"])
    gpu_use_program(cube["program"])
    gpu_draw_indexed("triangles", cube["count"])
}

export func delete_cube(cube) {
    gpu_delete_vao(cube["vao"])
    gpu_delete_buffer(cube["vtx_buf"])
    gpu_delete_buffer(cube["idx_buf"])
}
