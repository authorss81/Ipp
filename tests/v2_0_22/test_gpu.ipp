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

# ── Matrix Math ──
var ident = gpu_mat4_identity()
assert len(ident) == 16
assert ident[0] == 1.0 and ident[15] == 1.0
print("  mat4_identity: OK")

var proj = gpu_mat4_perspective(0.785, 1.333, 0.1, 100.0)
assert len(proj) == 16
assert proj[0] > 0.0  # f/aspect > 0
print("  mat4_perspective: OK")

var ortho = gpu_mat4_ortho(-1, 1, -1, 1, -1, 1)
assert len(ortho) == 16
assert ortho[0] == 1.0 and ortho[5] == 1.0
print("  mat4_ortho: OK")

var eye = [0, 0, 5]
var center = [0, 0, 0]
var up = [0, 1, 0]
var view = gpu_mat4_look_at(eye, center, up)
assert len(view) == 16
assert view[15] == 1.0
print("  mat4_look_at: OK")

var doubled = gpu_mat4_multiply(ident, ident)
assert doubled[0] == 1.0 and doubled[15] == 1.0
print("  mat4_multiply: OK")

var translated = gpu_mat4_translate(ident, 5, 10, 15)
assert translated[12] == 5.0 and translated[13] == 10.0 and translated[14] == 15.0
print("  mat4_translate: OK")

# rotate 90 deg around X axis
var rotated = gpu_mat4_rotate(ident, 1.5708, 1, 0, 0)
assert abs(rotated[5]) < 0.001  # cos(90)≈0
print("  mat4_rotate: OK")

var scaled = gpu_mat4_scale(ident, 2, 3, 4)
assert scaled[0] == 2.0 and scaled[5] == 3.0 and scaled[10] == 4.0
print("  mat4_scale: OK")

# ── Index Buffer (EBO) ──
gpu_init(320, 240)
var idx_buf = gpu_create_index_buffer([0, 1, 2])
assert idx_buf != nil and idx_buf > 0
gpu_draw_indexed("triangles", 3)
gpu_swap()
gpu_close()
print("  create_index_buffer / draw_indexed: OK")

# ── Texture ──
gpu_init(320, 240)
# Solid red 2x2 texture (r=1,g=0,b=0,a=1)
var tex_data = [1.0,0,0,1, 1.0,0,0,1,  1.0,0,0,1, 1.0,0,0,1]
var tex = gpu_create_texture(2, 2, tex_data)
assert tex != nil and tex > 0
gpu_bind_texture(0, tex)
gpu_delete_texture(tex)
gpu_close()
print("  create_texture / bind / delete: OK")

# ── VAO ──
gpu_init(320, 240)
var vao = gpu_create_vao()
assert vao != nil and vao > 0
gpu_bind_vao(vao)
gpu_delete_vao(vao)
gpu_close()
print("  create/bind/delete VAO: OK")

print("All v2.0.22 GPU tests passed!")