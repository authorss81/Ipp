# v2.0.22 — GPU Rendering Backend tests

print("=== v2.0.22 GPU Rendering tests ===")

# ── gpu_init / close ──
var result = gpu_init(640, 480, "Ipp GPU Test")
assert gpu_is_open() == true
var sz = gpu_size()
assert sz[0] == 640
assert sz[1] == 480
print("  gpu_init/size: OK")

# ── clear ──
gpu_clear(0.2, 0.2, 0.3, 1.0)
gpu_swap()
print("  gpu_clear/swap: OK")

# ── shader compilation ──
var vs_src = """
#version 330 core
layout(location = 0) in vec2 a_pos;
void main() {
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
"""
var fs_src = """
#version 330 core
out vec4 frag_color;
void main() {
    frag_color = vec4(1.0, 0.0, 0.0, 1.0);
}
"""
var vs = gpu_create_shader("vertex", vs_src)
assert vs != nil
assert vs > 0
var fs = gpu_create_shader("fragment", fs_src)
assert fs != nil
var prog = gpu_create_program(vs, fs)
assert prog != nil
gpu_use_program(prog)
gpu_delete_shader(vs)
gpu_delete_shader(fs)
print("  shader compilation + program: OK")

# ── buffer creation ──
var vertices = [0.0, 0.5,   -0.5, -0.5,   0.5, -0.5]
var buf = gpu_create_buffer(vertices)
assert buf != nil
gpu_bind_buffer(buf)
gpu_vertex_attrib(prog, "a_pos", 2, 0, 0)
gpu_draw("triangles", 3)
gpu_swap()
gpu_delete_buffer(buf)
print("  buffer + draw: OK")

# ── uniforms ──
gpu_clear(0.0, 0.0, 0.0, 1.0)
var fs_uniform = """
#version 330 core
uniform vec4 u_color;
out vec4 frag_color;
void main() {
    frag_color = u_color;
}
"""
var fs2 = gpu_create_shader("fragment", fs_uniform)
var prog2 = gpu_create_program(vs, fs2)
gpu_use_program(prog2)
gpu_delete_shader(fs2)
gpu_set_uniform(prog2, "u_color", [0.0, 1.0, 0.0, 1.0])

var buf2 = gpu_create_buffer(vertices)
gpu_bind_buffer(buf2)
gpu_vertex_attrib(prog2, "a_pos", 2, 0, 0)
gpu_draw("triangles", 3)
gpu_swap()
gpu_delete_buffer(buf2)
gpu_delete_program(prog2)
print("  uniform: OK")

# ── cleanup ──
gpu_delete_program(prog)
gpu_close()
assert gpu_is_open() == false
print("  gpu_close: OK")

# ── matrix uniform ──
gpu_init()
var fs_mat = """
#version 330 core
uniform mat4 u_transform;
out vec4 frag_color;
void main() {
    frag_color = vec4(u_transform[0][0], 0.0, 0.0, 1.0);
}
"""
var vs_m = gpu_create_shader("vertex", vs_src)
var fs_m = gpu_create_shader("fragment", fs_mat)
var pgm = gpu_create_program(vs_m, fs_m)
gpu_use_program(pgm)
gpu_delete_shader(vs_m)
gpu_delete_shader(fs_m)
gpu_set_uniform_matrix(pgm, "u_transform", [
    1.0, 0.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 0.0,
    0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 1.0,
])
gpu_clear(0.1, 0.1, 0.2, 1.0)
gpu_draw("triangles", 3)
gpu_swap()
gpu_delete_program(pgm)
gpu_close()
print("  matrix uniform: OK")

# ── draw modes ──
for mode in ["triangles", "lines", "points"] {
    gpu_init()
    gpu_clear(0.0, 0.0, 0.0, 1.0)
    gpu_draw(mode, 0)
    gpu_close()
}
print("  draw modes: OK")

print("All v2.0.22 GPU tests passed!")
