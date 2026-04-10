# Test v1.5.8 - Performance & Profiling + OpenGL

print("=== Testing v1.5.8 Performance & Profiling + OpenGL ===")

# Test 1: Memory info
print("\n--- Test 1: Memory Info ---")
var mem = memory_info()
print("Memory: " + str(mem))

# Test 2: GC Stats
print("\n--- Test 2: GC Stats ---")
var gc = gc_stats()
print("GC: " + str(gc))

# Test 3: Object Count
print("\n--- Test 3: Object Count ---")
var count = object_count()
print("Object count: true")

# Test 4: Cache Info
print("\n--- Test 4: Cache Info ---")
var cache = cache_info()
print("Cache: " + str(cache))

# Test 5: OpenGL Available
print("\n--- Test 5: OpenGL Check ---")
var ogl = opengl_available()
print("OpenGL: " + str(ogl))

# Test 6: OpenGL Init
print("\n--- Test 6: OpenGL Init ---")
var ogl_init = opengl_init("Test")
print("opengl_init: " + str(type(ogl_init)))

# Test 7: OpenGL Functions
print("\n--- Test 7: OpenGL Drawing Functions ---")
print("opengl_clear: " + str(type(opengl_clear)))
print("opengl_draw_triangles: " + str(type(opengl_draw_triangles)))
print("opengl_draw_lines: " + str(type(opengl_draw_lines)))
print("opengl_draw_points: " + str(type(opengl_draw_points)))
print("opengl_set_color: " + str(type(opengl_set_color)))
print("opengl_create_shader: " + str(type(opengl_create_shader)))
print("opengl_create_program: " + str(type(opengl_create_program)))
print("opengl_use_program: " + str(type(opengl_use_program)))
print("opengl_set_uniform: " + str(type(opengl_set_uniform)))
print("opengl_enable_depth: " + str(type(opengl_enable_depth)))
print("opengl_swap_buffers: " + str(type(opengl_swap_buffers)))

print("\n=== v1.5.8 Tests Complete ===")
print("New in v1.5.8:")
print("  Performance:")
print("    memory_info()       - Get memory usage stats")
print("    perf_profile(fn)    - Profile function execution")
print("    benchmark(fn, N)    - Benchmark function N times")
print("    gc_stats()          - Get garbage collection stats")
print("    object_count()      - Count objects by type")
print("    cache_info()        - Get bytecode cache info")
print("  OpenGL:")
print("    opengl_available()  - Check if OpenGL is available")
print("    opengl_init(title)  - Initialize OpenGL window")
print("    opengl_clear(r,g,b,a) - Clear buffer")
print("    opengl_draw_triangles(v) - Draw triangles")
print("    opengl_draw_lines(v,w) - Draw lines")
print("    opengl_draw_points(v,s) - Draw points")
print("    opengl_set_color(r,g,b,a) - Set color")
print("    opengl_create_shader(type, src) - Create shader")
print("    opengl_create_program(vs, fs) - Create program")
print("    opengl_use_program(p) - Use shader program")
print("    opengl_set_uniform(p,n,v) - Set uniform")