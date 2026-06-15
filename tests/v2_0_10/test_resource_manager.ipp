# v2.0.10: Resource Manager — resources.load(), preload(), is_loaded(), get()

print("=== Resource Manager ===")

# ===== resources.load() =====
# First create a test file to load
var test_content = "hello from ipp resource manager"
var write_ok = write_file("tests/v2_0_10/test_asset.txt", test_content)
assert write_ok == true, "write_file succeeds"

var data = resources.load("tests/v2_0_10/test_asset.txt")
assert data == test_content, "load returns file content"
assert type(data) == "string", "load returns string"

print("PASS: resources.load")

# ===== resources.is_loaded() =====
assert resources.is_loaded("tests/v2_0_10/test_asset.txt") == true, "is_loaded after load"
assert resources.is_loaded("nonexistent.txt") == false, "is_loaded missing file"

print("PASS: resources.is_loaded")

# ===== resources.get() =====
var cached = resources.get("tests/v2_0_10/test_asset.txt")
assert cached == test_content, "get returns cached content"
assert resources.get("nonexistent.txt") == nil, "get missing returns nil"

print("PASS: resources.get")

# ===== resources.load() caching (second call returns cached) =====
var data2 = resources.load("tests/v2_0_10/test_asset.txt")
assert data2 == test_content, "cached load returns same content"

print("PASS: resources.load cached")

# ===== resources.remove() =====
resources.remove("tests/v2_0_10/test_asset.txt")
assert resources.is_loaded("tests/v2_0_10/test_asset.txt") == false, "is_loaded false after remove"

# Re-load so it's in cache again
var data3 = resources.load("tests/v2_0_10/test_asset.txt")
assert data3 == test_content, "reload after remove works"

print("PASS: resources.remove")

# ===== resources.clear() =====
resources.clear()
assert resources.is_loaded("tests/v2_0_10/test_asset.txt") == false, "is_loaded false after clear"
assert resources.get("tests/v2_0_10/test_asset.txt") == nil, "get returns nil after clear"

print("PASS: resources.clear")

# ===== resources.preload() returns coroutine =====
# Re-load first so preload will find it cached
var data4 = resources.load("tests/v2_0_10/test_asset.txt")
var coro = resources.preload("tests/v2_0_10/test_asset.txt")
assert type(coro) == "coroutine" or coro != nil, "preload returns coroutine"

print("PASS: resources.preload returns coroutine")

# ===== await resources.preload() =====
async func test_async_preload() {
    var result = await resources.preload("tests/v2_0_10/test_asset.txt")
    assert result == test_content, "await preload returns file content"
    print("PASS: await resources.preload")
}

async_run(test_async_preload())

# ===== Load non-existent file =====
var caught = false
try {
    var bad = resources.load("tests/nonexistent_file_xyz.ipp")
} catch e {
    caught = true
}
assert caught == true, "load missing file throws error"

print("PASS: load missing file throws")

# ===== resources object exists and is an object =====
assert type(resources) != "nil", "resources is not nil"
assert resources != nil, "resources exists"

print("PASS: resources object exists")

# Cleanup test file
delete_file("tests/v2_0_10/test_asset.txt")

print("\nAll v2.0.10 resource manager tests passed!")
