# ipp-gpu — GPU Rendering wrapper (v2.0.22)

# Default vertex shader (position + color)
export var DEFAULT_VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec2 a_pos;
layout(location = 1) in vec3 a_color;
out vec3 v_color;
void main() {
    gl_Position = vec4(a_pos, 0.0, 1.0);
    v_color = a_color;
}
"""

# Default fragment shader
export var DEFAULT_FRAGMENT_SHADER = """
#version 330 core
in vec3 v_color;
out vec4 frag_color;
void main() {
    frag_color = vec4(v_color, 1.0);
}
"""

# Export low-level GPU builtins for convenience
export var _gpu_init = gpu_init
export var _gpu_close = gpu_close
export var _gpu_clear = gpu_clear
export var _gpu_swap = gpu_swap
export var _gpu_draw = gpu_draw
export var _gpu_create_shader = gpu_create_shader
export var _gpu_create_program = gpu_create_program
export var _gpu_use_program = gpu_use_program
export var _gpu_delete_shader = gpu_delete_shader
export var _gpu_delete_program = gpu_delete_program
export var _gpu_create_buffer = gpu_create_buffer
export var _gpu_bind_buffer = gpu_bind_buffer
export var _gpu_delete_buffer = gpu_delete_buffer
export var _gpu_vertex_attrib = gpu_vertex_attrib
export var _gpu_enable_attrib = gpu_enable_attrib
export var _gpu_disable_attrib = gpu_disable_attrib
export var _gpu_set_uniform = gpu_set_uniform
export var _gpu_set_uniform_matrix = gpu_set_uniform_matrix
export var _gpu_is_open = gpu_is_open
export var _gpu_size = gpu_size

# ── High-level wrappers ──

# Wrapper: init window with default shaders
export func init(width=800, height=600, title="Ipp GPU") {
    var result = gpu_init(width, height, title)
    var vs = gpu_create_shader("vertex", DEFAULT_VERTEX_SHADER)
    var fs = gpu_create_shader("fragment", DEFAULT_FRAGMENT_SHADER)
    var prog = gpu_create_program(vs, fs)
    gpu_use_program(prog)
    gpu_delete_shader(vs)
    gpu_delete_shader(fs)
    return {"window": result, "program": prog}
}

# Wrapper: draw a colored triangle (simplest GPU test)
export func draw_triangle(x1, y1, r1, g1, b1,
                          x2, y2, r2, g2, b2,
                          x3, y3, r3, g3, b3) {
    # Interleaved: pos.x, pos.y, color.r, color.g, color.b
    var vertices = [
        x1, y1, r1, g1, b1,
        x2, y2, r2, g2, b2,
        x3, y3, r3, g3, b3,
    ]
    var buf = gpu_create_buffer(vertices)
    gpu_bind_buffer(buf)
    # attrib 0 = position (2 floats, stride 20, offset 0)
    gpu_vertex_attrib(0, "a_pos", 2, 20, 0)
    # attrib 1 = color (3 floats, stride 20, offset 8)
    gpu_vertex_attrib(0, "a_color", 3, 20, 8)
    gpu_draw("triangles", 3)
    gpu_delete_buffer(buf)
}

# Wrapper: full render loop using canvas_run-style callback
export func render_loop(render_fn, fps=60) {
    while gpu_is_open() {
        var dt = 1.0 / fps
        render_fn(dt)
        gpu_swap()
    }
}
