#!/usr/bin/env python3
"""GPU Rendering Backend — hardware-accelerated 3D via OpenGL (v2.0.22)."""

import sys
import os

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    pygame = None
    HAS_PYGAME = False

try:
    from OpenGL.GL import (
        glClear, glClearColor, glClearDepth, glCreateShader, glShaderSource,
        glCompileShader, glGetShaderiv, glGetShaderInfoLog,
        glCreateProgram, glAttachShader, glLinkProgram,
        glGetProgramiv, glGetProgramInfoLog, glUseProgram,
        glGenBuffers, glBindBuffer, glBufferData, glDeleteBuffers,
        glDeleteShader, glDeleteProgram,
        glVertexAttribPointer, glEnableVertexAttribArray,
        glDisableVertexAttribArray, glDrawArrays, glGetAttribLocation,
        glGetUniformLocation, glUniform1f, glUniform2f, glUniform3f,
        glUniform4f, glUniform1i, glUniform2i, glUniform3i, glUniform4i,
        glUniformMatrix4fv, glEnable, glDisable, glDepthFunc, glViewport,
        GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
        GL_TRIANGLES, GL_LINES, GL_POINTS,
        GL_FLOAT, GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER, GL_STATIC_DRAW,
        GL_COMPILE_STATUS, GL_LINK_STATUS, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER,
        GL_DEPTH_TEST, GL_LEQUAL, GL_TRUE, GL_FALSE, GL_UNSIGNED_SHORT,
        glDrawElements, glGenVertexArrays, glBindVertexArray,
        glDeleteVertexArrays, glGenTextures, glBindTexture, glTexImage2D,
        glTexParameteri, glDeleteTextures, glActiveTexture, GL_TEXTURE_2D,
        GL_RGBA, GL_UNSIGNED_BYTE, GL_NEAREST, GL_LINEAR,
        GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_TEXTURE_WRAP_S,
        GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE, GL_TEXTURE0,
    )
    HAS_OPENGL = True
except ImportError:
    HAS_OPENGL = False
    GL_COLOR_BUFFER_BIT = 1
    GL_DEPTH_BUFFER_BIT = 2
    GL_TRIANGLES = 4
    GL_LINES = 1
    GL_POINTS = 0
    GL_FLOAT = 0x1406
    GL_ARRAY_BUFFER = 0x8892
    GL_ELEMENT_ARRAY_BUFFER = 0x8893
    GL_STATIC_DRAW = 0x88E4
    GL_VERTEX_SHADER = 0x8B31
    GL_FRAGMENT_SHADER = 0x8B30
    GL_UNSIGNED_SHORT = 0x1403
    glDrawElements = lambda *a: None
    glGenVertexArrays = lambda n: 0
    glBindVertexArray = lambda v: None
    glDeleteVertexArrays = lambda n, a: None
    glGenTextures = lambda n: 0
    glBindTexture = lambda t, i: None
    glTexImage2D = lambda *a: None
    glTexParameteri = lambda *a: None
    glDeleteTextures = lambda t: None
    glActiveTexture = lambda u: None
    GL_TEXTURE_2D = 0x0DE1
    GL_RGBA = 0x1908
    GL_UNSIGNED_BYTE = 0x1401
    GL_NEAREST = 0x2600
    GL_LINEAR = 0x2601
    GL_TEXTURE_MIN_FILTER = 0x2801
    GL_TEXTURE_MAG_FILTER = 0x2800
    GL_TEXTURE_WRAP_S = 0x2802
    GL_TEXTURE_WRAP_T = 0x2803
    GL_CLAMP_TO_EDGE = 0x812F
    GL_TEXTURE0 = 0x84C0

# Safe fallback: GL_TRIANGLE_STRIP may fail to resolve via lazy loading on headless CI
if HAS_OPENGL:
    try:
        from OpenGL.GL import GL_TRIANGLE_STRIP
    except Exception:
        GL_TRIANGLE_STRIP = 0x0005
else:
    GL_TRIANGLE_STRIP = 0x0005


_window_surface = None
_width = 800
_height = 600
_open = False
_depth_enabled = False
_clock = None
_shader_type_map = {
    "vertex": GL_VERTEX_SHADER,
    "fragment": GL_FRAGMENT_SHADER,
}
_draw_mode_map = {
    "triangles": GL_TRIANGLES,
    "lines": GL_LINES,
    "points": GL_POINTS,
    "triangle_strip": GL_TRIANGLE_STRIP,
}
_buffers = set()
_shaders = set()
_programs = set()


# ── Init / Close ──────────────────────────────────────────────────────────────

def ipp_gpu_init(width=800, height=600, title="Ipp GPU"):
    """Initialize OpenGL window (v2.0.22)."""
    global _window_surface, _width, _height, _open, _clock
    if _open:
        return "[gpu already initialized]"
    if not HAS_PYGAME or not HAS_OPENGL:
        _width, _height = width, height
        _open = True
        print("[gpu] Stub mode: PyOpenGL/pygame not available")
        return "[gpu stub]"
    try:
        pygame.init()
        pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        _window_surface = pygame.display.get_surface()
        _width, _height = width, height
        _open = True
        _clock = pygame.time.Clock()
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LEQUAL)
        glViewport(0, 0, width, height)
        print(f"[gpu] OpenGL window initialized ({width}x{height})")
        return f"[gpu window {width}x{height}]"
    except Exception as e:
        _width, _height = width, height
        _open = True
        print(f"[gpu] Stub mode (init failed: {e})")
        return "[gpu stub]"


def ipp_gpu_close():
    """Close the OpenGL window (v2.0.22)."""
    global _window_surface, _open, _clock
    _open = False
    _window_surface = None
    _clock = None
    _depth_enabled = False
    for buf in list(_buffers):
        try: glDeleteBuffers(1, [buf])
        except Exception: pass
    _buffers.clear()
    for shader in list(_shaders):
        try: glDeleteShader(shader)
        except Exception: pass
    _shaders.clear()
    for prog in list(_programs):
        try: glDeleteProgram(prog)
        except Exception: pass
    _programs.clear()
    if HAS_PYGAME and pygame.get_init():
        pygame.display.quit()
        pygame.quit()
    return "[gpu closed]"


def ipp_gpu_is_open():
    return _open


def ipp_gpu_size():
    return [_width, _height]


def ipp_gpu_viewport(x, y, w, h):
    if HAS_OPENGL:
        glViewport(x, y, w, h)


# ── Depth ─────────────────────────────────────────────────────────────────────

def ipp_gpu_enable_depth():
    global _depth_enabled
    if HAS_OPENGL:
        glEnable(GL_DEPTH_TEST)
    _depth_enabled = True


def ipp_gpu_disable_depth():
    global _depth_enabled
    if HAS_OPENGL:
        glDisable(GL_DEPTH_TEST)
    _depth_enabled = False


# ── Event polling ─────────────────────────────────────────────────────────────
# Returns a list of event dicts: {"type": "quit"|"key_down"|"mouse_move"|...}
# The window auto-closes on QUIT event.

def ipp_gpu_poll_events():
    """Poll window events (v2.0.22). Returns list of event dicts."""
    global _open
    if not _open or not HAS_PYGAME:
        return []
    result = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            _open = False
            result.append({"type": "quit"})
        elif event.type == pygame.KEYDOWN:
            result.append({
                "type": "key_down",
                "key": pygame.key.name(event.key),
                "scancode": event.scancode,
            })
        elif event.type == pygame.KEYUP:
            result.append({
                "type": "key_up",
                "key": pygame.key.name(event.key),
            })
        elif event.type == pygame.MOUSEMOTION:
            result.append({
                "type": "mouse_move",
                "x": event.pos[0],
                "y": event.pos[1],
            })
        elif event.type == pygame.MOUSEBUTTONDOWN:
            result.append({
                "type": "mouse_down",
                "button": event.button,
                "x": event.pos[0],
                "y": event.pos[1],
            })
        elif event.type == pygame.MOUSEBUTTONUP:
            result.append({
                "type": "mouse_up",
                "button": event.button,
                "x": event.pos[0],
                "y": event.pos[1],
            })
    return result


# ── Delta time ────────────────────────────────────────────────────────────────

def ipp_gpu_dt():
    """Return seconds since last call (v2.0.22)."""
    global _clock
    if _clock is not None and HAS_PYGAME:
        return _clock.tick() / 1000.0
    return 0.016


# ── Clearing / Drawing ────────────────────────────────────────────────────────

def ipp_gpu_clear(r=0.0, g=0.0, b=0.0, a=1.0):
    if not _open: return
    if HAS_OPENGL:
        bits = GL_COLOR_BUFFER_BIT
        if _depth_enabled:
            bits |= GL_DEPTH_BUFFER_BIT
        glClearColor(r, g, b, a)
        glClear(bits)


def ipp_gpu_swap():
    if not _open or not HAS_PYGAME: return
    try: pygame.display.flip()
    except Exception: pass


def ipp_gpu_draw(mode="triangles", count=0):
    if not _open or not HAS_OPENGL: return
    gl_mode = _draw_mode_map.get(mode, GL_TRIANGLES)
    glDrawArrays(gl_mode, 0, count)


# ── Shaders ────────────────────────────────────────────────────────────────────

def ipp_gpu_create_shader(shader_type, source):
    if not HAS_OPENGL:
        shader_id = len(_shaders) + 1
        _shaders.add(shader_id)
        return shader_id
    gl_type = _shader_type_map.get(shader_type)
    if gl_type is None:
        raise ValueError(f"Unknown shader type: {shader_type}. Use 'vertex' or 'fragment'.")
    shader = glCreateShader(gl_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    status = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not status:
        log = glGetShaderInfoLog(shader)
        glDeleteShader(shader)
        raise RuntimeError(f"Shader compile error: {log.decode() if isinstance(log, bytes) else log}")
    _shaders.add(shader)
    return shader


def ipp_gpu_create_program(vertex_shader, fragment_shader):
    if not HAS_OPENGL:
        prog_id = len(_programs) + 1
        _programs.add(prog_id)
        return prog_id
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    status = glGetProgramiv(program, GL_LINK_STATUS)
    if not status:
        log = glGetProgramInfoLog(program)
        glDeleteProgram(program)
        raise RuntimeError(f"Program link error: {log.decode() if isinstance(log, bytes) else log}")
    _programs.add(program)
    return program


def ipp_gpu_use_program(program_id):
    if HAS_OPENGL:
        glUseProgram(program_id)


def ipp_gpu_delete_shader(shader_id):
    _shaders.discard(shader_id)
    if HAS_OPENGL: glDeleteShader(shader_id)


def ipp_gpu_delete_program(program_id):
    _programs.discard(program_id)
    if HAS_OPENGL: glDeleteProgram(program_id)


# ── Buffers ────────────────────────────────────────────────────────────────────

def ipp_gpu_create_buffer(data):
    if not HAS_OPENGL:
        buf_id = len(_buffers) + 1
        _buffers.add(buf_id)
        return buf_id
    import array
    buf = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, buf)
    flat = array.array('f', data)
    glBufferData(GL_ARRAY_BUFFER, flat.tobytes(), GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    _buffers.add(buf)
    return buf


def ipp_gpu_bind_buffer(buffer_id):
    if HAS_OPENGL: glBindBuffer(GL_ARRAY_BUFFER, buffer_id)


def ipp_gpu_delete_buffer(buffer_id):
    _buffers.discard(buffer_id)
    if HAS_OPENGL: glDeleteBuffers(1, [buffer_id])


# ── Vertex Attributes ─────────────────────────────────────────────────────────

def ipp_gpu_vertex_attrib(program_id, name, size, stride=0, offset=0):
    if not HAS_OPENGL: return 0
    loc = glGetAttribLocation(program_id, name)
    if loc < 0: return -1
    glVertexAttribPointer(loc, size, GL_FLOAT, GL_FALSE, stride, offset)
    glEnableVertexAttribArray(loc)
    return loc


def ipp_gpu_enable_attrib(location):
    if HAS_OPENGL: glEnableVertexAttribArray(location)


def ipp_gpu_disable_attrib(location):
    if HAS_OPENGL: glDisableVertexAttribArray(location)


# ── Uniforms ──────────────────────────────────────────────────────────────────

def ipp_gpu_set_uniform(program_id, name, value):
    if not HAS_OPENGL or not _open: return
    loc = glGetUniformLocation(program_id, name)
    if loc < 0: return
    if isinstance(value, (int, float)):
        if isinstance(value, int): glUniform1i(loc, value)
        else: glUniform1f(loc, value)
    elif isinstance(value, (list, tuple)):
        types = set(type(v) for v in value)
        if len(value) == 2:
            if int in types: glUniform2i(loc, int(value[0]), int(value[1]))
            else: glUniform2f(loc, float(value[0]), float(value[1]))
        elif len(value) == 3:
            glUniform3f(loc, float(value[0]), float(value[1]), float(value[2]))
        elif len(value) == 4:
            glUniform4f(loc, float(value[0]), float(value[1]), float(value[2]), float(value[3]))


def ipp_gpu_set_uniform_matrix(program_id, name, matrix):
    if not HAS_OPENGL or not _open: return
    loc = glGetUniformLocation(program_id, name)
    if loc < 0: return
    import array
    flat = array.array('f', matrix)
    glUniformMatrix4fv(loc, 1, GL_FALSE, flat.tobytes())


# ── Matrix Math Builtins ────────────────────────────────────────────────────
# All return 16-element float lists in column-major order.

import math as _math

def ipp_gpu_mat4_identity():
    return [1.0,0,0,0, 0,1.0,0,0, 0,0,1.0,0, 0,0,0,1.0]

def ipp_gpu_mat4_perspective(fov_y, aspect, z_near, z_far):
    f = 1.0 / _math.tan(fov_y / 2.0)
    nf = 1.0 / (z_near - z_far)
    return [f/aspect,0,0,0, 0,f,0,0, 0,0,(z_far+z_near)*nf,-1, 0,0,2*z_far*z_near*nf,0]

def ipp_gpu_mat4_ortho(left, right, bottom, top, near, far):
    return [2/(right-left),0,0,0, 0,2/(top-bottom),0,0, 0,0,-2/(far-near),0, -(right+left)/(right-left),-(top+bottom)/(top-bottom),-(far+near)/(far-near),1]

def ipp_gpu_mat4_look_at(eye, center, up):
    import math as _math2
    ex, ey, ez = eye[0], eye[1], eye[2]
    cx, cy, cz = center[0], center[1], center[2]
    ux, uy, uz = up[0], up[1], up[2]
    fwd = [cx-ex, cy-ey, cz-ez]
    fl = _math2.sqrt(fwd[0]**2 + fwd[1]**2 + fwd[2]**2)
    if fl: fwd = [fwd[0]/fl, fwd[1]/fl, fwd[2]/fl]
    side = [fwd[1]*uz-fwd[2]*uy, fwd[2]*ux-fwd[0]*uz, fwd[0]*uy-fwd[1]*ux]
    sl = _math2.sqrt(side[0]**2 + side[1]**2 + side[2]**2)
    if sl: side = [side[0]/sl, side[1]/sl, side[2]/sl]
    u = [side[1]*fwd[2]-side[2]*fwd[1], side[2]*fwd[0]-side[0]*fwd[2], side[0]*fwd[1]-side[1]*fwd[0]]
    return [side[0],u[0],-fwd[0],0, side[1],u[1],-fwd[1],0, side[2],u[2],-fwd[2],0, -side[0]*ex-side[1]*ey-side[2]*ez, -u[0]*ex-u[1]*ey-u[2]*ez, fwd[0]*ex+fwd[1]*ey+fwd[2]*ez, 1]

def _mat4_mul(a, b):
    out = [0.0]*16
    for i in range(4):
        ai0, ai1, ai2, ai3 = a[i], a[i+4], a[i+8], a[i+12]
        out[i]    = ai0*b[0] + ai1*b[1] + ai2*b[2]  + ai3*b[3]
        out[i+4]  = ai0*b[4] + ai1*b[5] + ai2*b[6]  + ai3*b[7]
        out[i+8]  = ai0*b[8] + ai1*b[9] + ai2*b[10] + ai3*b[11]
        out[i+12] = ai0*b[12] + ai1*b[13] + ai2*b[14] + ai3*b[15]
    return out

def ipp_gpu_mat4_multiply(a, b):
    return _mat4_mul(a, b)

def ipp_gpu_mat4_translate(m, x, y, z):
    tr = [1.0,0,0,0, 0,1.0,0,0, 0,0,1.0,0, x,y,z,1.0]
    return _mat4_mul(m, tr)

def ipp_gpu_mat4_rotate(m, angle, ax, ay, az):
    c, s = _math.cos(angle), _math.sin(angle)
    nc = 1.0 - c
    x, y, z = ax, ay, az
    l = _math.sqrt(x*x + y*y + z*z)
    if l: x/=l; y/=l; z/=l
    r = [c+x*x*nc, x*y*nc+z*s, x*z*nc-y*s, 0,
         x*y*nc-z*s, c+y*y*nc, y*z*nc+x*s, 0,
         x*z*nc+y*s, y*z*nc-x*s, c+z*z*nc, 0,
         0, 0, 0, 1.0]
    return _mat4_mul(m, r)

def ipp_gpu_mat4_scale(m, x, y, z):
    sc = [x,0,0,0, 0,y,0,0, 0,0,z,0, 0,0,0,1.0]
    return _mat4_mul(m, sc)


# ── Index Buffer (EBO) ─────────────────────────────────────────────────────

def ipp_gpu_create_index_buffer(data):
    if not HAS_OPENGL:
        buf_id = len(_buffers) + 1000
        _buffers.add(buf_id)
        return buf_id
    import array
    buf = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buf)
    flat = array.array('H', data)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, flat.tobytes(), GL_STATIC_DRAW)
    _buffers.add(buf)
    return buf

def ipp_gpu_bind_index_buffer(buffer_id):
    if HAS_OPENGL: glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffer_id)

def ipp_gpu_draw_indexed(mode="triangles", count=0):
    if not _open or not HAS_OPENGL: return
    gl_mode = _draw_mode_map.get(mode, GL_TRIANGLES)
    glDrawElements(gl_mode, count, GL_UNSIGNED_SHORT, None)


# ── Textures ────────────────────────────────────────────────────────────────

_textures = {}

def ipp_gpu_create_texture(width, height, data):
    if not HAS_OPENGL:
        tid = len(_textures) + 1
        _textures[tid] = None
        return tid
    import array
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    pixels = array.array('B', (max(0, min(255, int(v * 255))) for v in data))
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels.tobytes())
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    _textures[tex] = tex
    return tex

def ipp_gpu_load_texture(path):
    if not HAS_OPENGL or not HAS_PYGAME:
        return 0
    try:
        img = pygame.image.load(path)
        img_data = pygame.image.tostring(img, 'RGBA', True)
        w, h = img.get_width(), img.get_height()
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        _textures[tex] = tex
        return tex
    except Exception as e:
        print(f"[gpu] Failed to load texture '{path}': {e}")
        return 0

def ipp_gpu_bind_texture(unit, texture_id):
    if not HAS_OPENGL: return
    glActiveTexture(GL_TEXTURE0 + unit)
    glBindTexture(GL_TEXTURE_2D, texture_id)

def ipp_gpu_delete_texture(texture_id):
    _textures.pop(texture_id, None)
    if HAS_OPENGL:
        glDeleteTextures([texture_id])


# ── VAO (Vertex Array Object) ──────────────────────────────────────────────

_vaos = set()

def ipp_gpu_create_vao():
    if not HAS_OPENGL:
        vaoid = len(_vaos) + 1
        _vaos.add(vaoid)
        return vaoid
    vao = glGenVertexArrays(1)
    _vaos.add(vao)
    return vao

def ipp_gpu_bind_vao(vao_id):
    if not HAS_OPENGL: return
    glBindVertexArray(vao_id)

def ipp_gpu_delete_vao(vao_id):
    _vaos.discard(vao_id)
    if HAS_OPENGL:
        glDeleteVertexArrays(1, [vao_id])
