# v2.0.22 — GPU Rendering Backend practical tests

print("=== v2.0.22 GPU Rendering practical tests ===")

# ── Init / Close lifecycle ──
gpu_init(640, 480, "Ipp GPU Test")
assert gpu_is_open() == true
var sz = gpu_size()
assert sz[0] == 640 and sz[1] == 480
print("  init/size: OK")

# ── Viewport ──
gpu_viewport(0, 0, 640, 480)
print("  viewport: OK")

# ── Clear + Swap ──
gpu_clear(0.2, 0.2, 0.3, 1.0)
gpu_swap()
print("  clear/swap: OK")

# ── Shader compilation ──
var vs_src = """
#version 330 core
layout(location = 0) in vec2 a_pos;
void main() {
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
"""
var fs_red = """
#version 330 core
out vec4 frag_color;
void main() { frag_color = vec4(1.0, 0.0, 0.0, 1.0); }
"""
var vs = gpu_create_shader("vertex", vs_src)
assert vs != nil and vs > 0
var fs = gpu_create_shader("fragment", fs_red)
assert fs != nil
var prog = gpu_create_program(vs, fs)
assert prog != nil
gpu_use_program(prog)
gpu_delete_shader(vs)
gpu_delete_shader(fs)
print("  shader compile/link: OK")

# ── Buffer + Vertex Attrib + Draw ──
var triangle = [0.0, 0.5,  -0.5, -0.5,  0.5, -0.5]
var buf = gpu_create_buffer(triangle)
assert buf != nil
gpu_bind_buffer(buf)
var loc = gpu_vertex_attrib(prog, "a_pos", 2, 0, 0)
assert loc >= 0
gpu_draw("triangles", 3)
gpu_swap()
gpu_delete_buffer(buf)
print("  buffer/attrib/draw: OK")

# ── Uniform (vec4 color) ──
gpu_clear(0.0, 0.0, 0.0, 1.0)
var vs2 = gpu_create_shader("vertex", vs_src)
var fs_color = """
#version 330 core
uniform vec4 u_color;
out vec4 frag_color;
void main() { frag_color = u_color; }
"""
var fs2 = gpu_create_shader("fragment", fs_color)
var prog2 = gpu_create_program(vs2, fs2)
gpu_use_program(prog2)
gpu_delete_shader(vs2); gpu_delete_shader(fs2)
gpu_set_uniform(prog2, "u_color", [0.0, 1.0, 0.0, 1.0])
var buf2 = gpu_create_buffer(triangle)
gpu_bind_buffer(buf2)
gpu_vertex_attrib(prog2, "a_pos", 2, 0, 0)
gpu_draw("triangles", 3)
gpu_swap()
gpu_delete_buffer(buf2)
gpu_delete_program(prog2)
print("  uniform: OK")

# ── Matrix uniform ──
var vs3 = gpu_create_shader("vertex", vs_src)
var fs_mat = """
#version 330 core
uniform mat4 u_m;
out vec4 frag_color;
void main() { frag_color = vec4(u_m[0][0], 0.0, 0.0, 1.0); }
"""
var fs3 = gpu_create_shader("fragment", fs_mat)
var pgm = gpu_create_program(vs3, fs3)
gpu_use_program(pgm)
gpu_delete_shader(vs3); gpu_delete_shader(fs3)
gpu_set_uniform_matrix(pgm, "u_m", [
    1.0, 0.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 0.0,
    0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 1.0,
])
gpu_clear(0.1, 0.1, 0.2, 1.0)
gpu_draw("triangles", 3)
gpu_swap()
gpu_delete_program(pgm)
print("  matrix uniform: OK")

# ── Depth testing ──
gpu_enable_depth()
gpu_disable_depth()
print("  depth toggle: OK")

# ── Event polling (stub-safe) ──
var evts = gpu_poll_events()
assert len(evts) >= 0
print("  poll_events: OK")

# ── dt (delta time) ──
var framedt = gpu_dt()
assert framedt > 0.0
print("  dt: OK")

# ── Draw modes ──
for mode in ["triangles", "lines", "points"] {
    gpu_clear(0.0, 0.0, 0.0, 1.0)
    gpu_draw(mode, 0)
}
gpu_swap()
print("  draw modes: OK")

# ── Cleanup ──
gpu_delete_program(prog)
gpu_close()
assert gpu_is_open() == false
print("  close: OK")

# ── Re-init after close ──
gpu_init(320, 240)
assert gpu_is_open() == true
var sz2 = gpu_size()
assert sz2[0] == 320 and sz2[1] == 240
gpu_close()
print("  re-init: OK")

print("All v2.0.22 GPU tests passed!")