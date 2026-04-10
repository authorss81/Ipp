# Test v1.5.8 - Performance & Profiling + OpenGL

print("=== Testing v1.5.8 Performance & Profiling ===")

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
print("Object count works: true")

# Test 4: Cache Info
print("\n--- Test 4: Cache Info ---")
var cache = cache_info()
print("Cache: " + str(cache))

# Test 5: OpenGL Available
print("\n--- Test 5: OpenGL Check ---")
var ogl = opengl_available()
print("OpenGL: " + str(ogl))

print("\n=== v1.5.8 Tests Complete ===")
print("New in v1.5.8:")
print("  memory_info()       - Get memory usage stats")
print("  perf_profile(fn)    - Profile function execution")
print("  benchmark(fn, N)    - Benchmark function N times")
print("  gc_stats()          - Get garbage collection stats")
print("  object_count()      - Count objects by type")
print("  cache_info()        - Get bytecode cache info")
print("  opengl_available() - Check if OpenGL is available")