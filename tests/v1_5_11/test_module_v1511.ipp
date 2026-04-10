# Test v1.5.11 - Module System

print("=== Testing v1.5.11 Module System ===")

# Test 1: Module cache info
print("\n--- Test 1: Module Cache Info ---")
var cache = module_cache_info()
print("Cache: " + str(cache))

# Test 2: Import module
print("\n--- Test 2: Import Module ---")
var imp = import_module("tests/v05/hello.ipp")
print("Import: " + str(imp))

# Test 3: List exports
print("\n--- Test 3: List Exports ---")
var exports = list_exports({})
print("Empty exports: " + str(exports))

# Test 4: Package info
print("\n--- Test 4: Package Info ---")
var pkg1 = package_info("ipp")
print("ipp: " + str(pkg1))
var pkg2 = package_info("examples")
print("examples: " + str(pkg2))

# Test 5: Reload module
print("\n--- Test 5: Reload Module ---")
var reload = reload_module("test")
print("Reload: " + str(reload))

print("\n=== v1.5.11 Tests Complete ===")
print("New in v1.5.11:")
print("  module_cache_info()  - Get module cache info")
print("  import_module(path) - Import module by path")
print("  list_exports(env)   - List module exports")
print("  package_info(path)  - Check if path is package")
print("  reload_module(name) - Reload module")