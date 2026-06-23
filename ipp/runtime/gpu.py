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
        glClear, glClearColor, glCreateShader, glShaderSource,
        glCompileShader, glGetShaderiv, glGetShaderInfoLog,
        glCreateProgram, glAttachShader, glLinkProgram,
        glGetProgramiv, glGetProgramInfoLog, glUseProgram,
        glGenBuffers, glBindBuffer, glBufferData, glDeleteBuffers,
        glDeleteShader, glDeleteProgram,
        glVertexAttribPointer, glEnableVertexAttribArray,
        glDisableVertexAttribArray, glDrawArrays, glGetAttribLocation,
        glGetUniformLocation, glUniform1f, glUniform2f, glUniform3f,
        glUniform4f, glUniform1i, glUniform2i, glUniform3i, glUniform4i,
        glUniformMatrix4fv, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
        GL_TRIANGLES, GL_LINES, GL_POINTS, GL_TRIANGLE_STRIP,
        GL_FLOAT, GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_COMPILE_STATUS,
        GL_LINK_STATUS, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER,
    )
    HAS_OPENGL = True
except ImportError:
    HAS_OPENGL = False
    # Stub enums for test mode
    GL_COLOR_BUFFER_BIT = 1
    GL_DEPTH_BUFFER_BIT = 2
    GL_TRIANGLES = 4
    GL_LINES = 1
    GL_POINTS = 0
    GL_FLOAT = 0x1406
    GL_ARRAY_BUFFER = 0x8892
    GL_STATIC_DRAW = 0x88E4
    GL_VERTEX_SHADER = 0x8B31
    GL_FRAGMENT_SHADER = 0x8B30


_window = None
_surface = None
_width = 800
_height = 600
_open = False
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
    global _window, _surface, _width, _height, _open
    if _window is not None:
        return "[gpu already initialized]"
    if not HAS_PYGAME or not HAS_OPENGL:
        _width, _height = width, height
        _open = True
        print("[gpu] Stub mode: PyOpenGL/pygame not available")
        return "[gpu stub]"
    try:
        pygame.init()
        pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        _window = pygame.display.get_surface()
        _surface = pygame.display.get_surface()
        _width, _height = width, height
        _open = True
        glClearColor(0.0, 0.0, 0.0, 1.0)
        print(f"[gpu] OpenGL window initialized ({width}x{height})")
        return f"[gpu window {width}x{height}]"
    except Exception as e:
        _width, _height = width, height
        _open = True
        print(f"[gpu] Stub mode (init failed: {e})")
        return "[gpu stub]"


def ipp_gpu_close():
    """Close the OpenGL window (v2.0.22)."""
    global _window, _surface, _open
    for buf in list(_buffers):
        try:
            glDeleteBuffers(1, [buf])
        except Exception:
            pass
    _buffers.clear()
    for shader in list(_shaders):
        try:
            glDeleteShader(shader)
        except Exception:
            pass
    _shaders.clear()
    for prog in list(_programs):
        try:
            glDeleteProgram(prog)
        except Exception:
            pass
    _programs.clear()
    _open = False
    if HAS_PYGAME and pygame.get_init():
        pygame.quit()
    _window = None
    _surface = None
    return "[gpu closed]"


def ipp_gpu_is_open():
    """Return True if GPU window is open (v2.0.22)."""
    return _open


def ipp_gpu_size():
    """Return [width, height] of GPU window (v2.0.22)."""
    return [_width, _height]


# ── Clearing / Drawing ────────────────────────────────────────────────────────

def ipp_gpu_clear(r=0.0, g=0.0, b=0.0, a=1.0):
    """Clear the color buffer (v2.0.22)."""
    if not _open:
        return
    if HAS_OPENGL:
        glClearColor(r, g, b, a)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


def ipp_gpu_swap():
    """Swap buffers / present frame (v2.0.22)."""
    if not _open or not HAS_PYGAME:
        return
    try:
        pygame.display.flip()
    except Exception:
        pass


def ipp_gpu_draw(mode="triangles", count=0):
    """Draw arrays (v2.0.22). mode: triangles, lines, points."""
    if not _open or not HAS_OPENGL:
        return
    gl_mode = _draw_mode_map.get(mode, GL_TRIANGLES)
    glDrawArrays(gl_mode, 0, count)


# ── Shaders ────────────────────────────────────────────────────────────────────

def ipp_gpu_create_shader(shader_type, source):
    """Compile a shader (v2.0.22). shader_type: 'vertex' or 'fragment'."""
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
    """Link a shader program from vertex and fragment shader IDs (v2.0.22)."""
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
    """Activate a shader program (v2.0.22)."""
    if HAS_OPENGL:
        glUseProgram(program_id)


def ipp_gpu_delete_shader(shader_id):
    """Delete a shader (v2.0.22)."""
    _shaders.discard(shader_id)
    if HAS_OPENGL:
        glDeleteShader(shader_id)


def ipp_gpu_delete_program(program_id):
    """Delete a shader program (v2.0.22)."""
    _programs.discard(program_id)
    if HAS_OPENGL:
        glDeleteProgram(program_id)


# ── Buffers ────────────────────────────────────────────────────────────────────

def ipp_gpu_create_buffer(data):
    """Create a VBO with vertex data (list of floats) (v2.0.22)."""
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
    """Bind a VBO (v2.0.22)."""
    if HAS_OPENGL:
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)


def ipp_gpu_delete_buffer(buffer_id):
    """Delete a VBO (v2.0.22)."""
    _buffers.discard(buffer_id)
    if HAS_OPENGL:
        glDeleteBuffers(1, [buffer_id])


# ── Vertex Attributes ─────────────────────────────────────────────────────────

def ipp_gpu_vertex_attrib(program_id, name, size, stride=0, offset=0):
    """Set up a vertex attribute pointer (v2.0.22). Returns attribute location."""
    if not HAS_OPENGL:
        return 0
    loc = glGetAttribLocation(program_id, name)
    if loc < 0:
        return -1
    glVertexAttribPointer(loc, size, GL_FLOAT, False, stride, offset)
    glEnableVertexAttribArray(loc)
    return loc


def ipp_gpu_enable_attrib(location):
    """Enable a vertex attribute array (v2.0.22)."""
    if HAS_OPENGL:
        glEnableVertexAttribArray(location)


def ipp_gpu_disable_attrib(location):
    """Disable a vertex attribute array (v2.0.22)."""
    if HAS_OPENGL:
        glDisableVertexAttribArray(location)


# ── Uniforms ──────────────────────────────────────────────────────────────────

def ipp_gpu_set_uniform(program_id, name, value):
    """Set a uniform value (v2.0.22). Supports float, int, list of 2/3/4 values."""
    if not HAS_OPENGL or not _open:
        return
    loc = glGetUniformLocation(program_id, name)
    if loc < 0:
        return
    if isinstance(value, (int, float)):
        if isinstance(value, int):
            glUniform1i(loc, value)
        else:
            glUniform1f(loc, value)
    elif isinstance(value, (list, tuple)):
        types = set(type(v) for v in value)
        if len(value) == 2:
            if int in types:
                glUniform2i(loc, int(value[0]), int(value[1]))
            else:
                glUniform2f(loc, float(value[0]), float(value[1]))
        elif len(value) == 3:
            glUniform3f(loc, float(value[0]), float(value[1]), float(value[2]))
        elif len(value) == 4:
            glUniform4f(loc, float(value[0]), float(value[1]), float(value[2]), float(value[3]))


def ipp_gpu_set_uniform_matrix(program_id, name, matrix):
    """Set a 4x4 matrix uniform (list of 16 floats, column-major) (v2.0.22)."""
    if not HAS_OPENGL or not _open:
        return
    loc = glGetUniformLocation(program_id, name)
    if loc < 0:
        return
    import array
    flat = array.array('f', matrix)
    glUniformMatrix4fv(loc, 1, False, flat.tobytes())
