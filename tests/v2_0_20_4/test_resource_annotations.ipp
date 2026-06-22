# v2.0.20.4 - Resource Annotations (@texture, @sound, @tilemap)
# Tests that resource annotations on class fields generate proper loading calls.

print("=== v2.0.20.4 Resource Annotation Tests ===")

# Test 1: @texture with nonexistent file should set field to nil
class TestTexture {
    @texture("nonexistent.png")
    var sprite = nil
    func init() {}
}
var t = TestTexture()
assert(type(t.sprite) == "nil", "Test 1 FAIL: @texture with missing file should leave nil")

# Test 2: @texture with valid file should load image
class TestTextureValid {
    @texture("tests/v2_0_20_4/fixtures/dummy.png")
    var img = nil
    func init() {}
}
var tv = TestTextureValid()
assert(type(tv.img) != "nil", "Test 2 FAIL: @texture with valid file should not be nil")
assert(type(tv.img) == "Image", "Test 2 FAIL: @texture should return an Image, got " + type(tv.img))

# Test 3: @sound annotation with nonexistent file should still create Sound object
class TestSound {
    @sound("nonexistent.wav")
    var sfx = nil
    func init() {}
}
var s = TestSound()
print("  Sound field type:", type(s.sfx))

# Test 4: @tilemap annotation
class TestTilemap {
    @tilemap("nonexistent.json")
    var map = nil
    func init() {}
}
var tm = TestTilemap()
assert(type(tm.map) == "nil", "Test 4 FAIL: @tilemap with missing file should leave nil")

# Test 5: Class without annotations still works
class Plain {
    var x = 42
    func init() {}
}
var p = Plain()
assert(p.x == 42, "Test 5 FAIL: plain class field should be 42")

# Test 6: Multiple annotations on different fields
class MultiAnnotate {
    @texture("nonexistent_a.png")
    var tex = nil
    @sound("nonexistent_b.wav")
    var snd = nil
    func init() {}
}
var m = MultiAnnotate()
assert(type(m.tex) == "nil", "Test 6a FAIL: @texture should be nil for missing file")
assert(m.tex == nil, "Test 6b FAIL: @texture should be nil for missing file")
print("  Multi-annotate texture:", type(m.tex), "sound:", type(m.snd))

# Test 7: Verify load_texture builtin works directly
var direct_img = load_texture("tests/v2_0_20_4/fixtures/dummy.png", "direct_test")
assert(type(direct_img) == "Image", "Test 7 FAIL: load_texture should return Image")

# Test 8: @texture field value is same as load_texture result
var tv2 = TestTextureValid()
var direct = load_texture("tests/v2_0_20_4/fixtures/dummy.png", "compare_test")
assert(type(tv2.img) == type(direct), "Test 8 FAIL: annotated field should match direct load type")

print("All v2.0.20.4 resource annotation tests passed!")
