# v2.0.9: Scene tree with parent-child hierarchy

print("=== SceneNode hierarchy ===")

# ===== Basic parent-child =====
var root = node("root")
var child = node("child")
root.add_child(child)

assert child.get_parent() == root, "child parent is root"
assert child.get_parent().name == "root", "child parent name"

var children = root.get_children()
assert len(children) == 1, "root has 1 child"
assert children[0].name == "child", "first child name"

print("PASS: parent-child add/query")

# ===== remove_child =====
var removed = root.remove_child(child)
assert removed == true, "remove_child returns true"
assert child.get_parent() == nil, "child parent cleared after remove"
assert len(root.get_children()) == 0, "root has 0 children after remove"

print("PASS: remove_child")

# ===== find_node (recursive) =====
var grandparent = node("grandparent")
var parent_node = node("parent")
var target = node("target")

grandparent.add_child(parent_node)
parent_node.add_child(target)

var found = grandparent.find_node("target")
assert found == target, "find_node finds nested child"
assert found.name == "target", "found node name"

var not_found = grandparent.find_node("nonexistent")
assert not_found == nil, "find_node returns nil for missing"

print("PASS: find_node recursive")

# ===== get_world_transform =====
var my_scene = scene("test_hierarchy")

var root_node = node("root")
root_node.position = vec3(10, 20, 30)

var leaf = node("leaf")
leaf.position = vec3(1, 2, 3)

root_node.add_child(leaf)

# World transform of leaf should chain root + leaf translation
var wt = leaf.get_world_transform()
# wt is a 16-element matrix (4x4 column-major)
# Translation is at indices 3, 7, 11
assert abs(wt[3] - 11.0) < 0.001, "world x = root.x + leaf.x"
assert abs(wt[7] - 22.0) < 0.001, "world y = root.y + leaf.y"
assert abs(wt[11] - 33.0) < 0.001, "world z = root.z + leaf.z"

print("PASS: get_world_transform chains translations")

# ===== get_world_position =====
var wp = leaf.get_world_position()
assert abs(wp.x - 11.0) < 0.001, "world pos x"
assert abs(wp.y - 22.0) < 0.001, "world pos y"
assert abs(wp.z - 33.0) < 0.001, "world pos z"

print("PASS: get_world_position")

# ===== Scene root management =====
var scene2 = scene("rooted")
var child_a = node("A")
var child_b = node("B")

scene2.set_root(child_a)
assert scene2.get_root() == child_a, "scene root is A"
assert scene2.get_root().name == "A", "scene root name"

scene2.set_root(child_b)
assert scene2.get_root() == child_b, "scene root changed to B"

print("PASS: scene.set_root / get_root")

# ===== scene.remove clears root =====
scene2.remove(child_b)
assert scene2.get_root() == nil, "root cleared on remove"

print("PASS: scene.remove clears root")

# ===== Deep hierarchy traversal =====
var deep = scene("deep")
var top = node("top")
var mid = node("mid")
var bot = node("bot")
var sub = node("sub")

top.add_child(mid)
mid.add_child(bot)
bot.add_child(sub)

deep.set_root(top)

var all_nodes = deep.get_all_nodes()
var names = []
for n in all_nodes {
    names.append(n.name)
}

var has_top = false
var has_mid = false
var has_bot = false
var has_sub = false
for name in names {
    if name == "top" { has_top = true }
    if name == "mid" { has_mid = true }
    if name == "bot" { has_bot = true }
    if name == "sub" { has_sub = true }
}
assert has_top, "top in all_nodes"
assert has_mid, "mid in all_nodes"
assert has_bot, "bot in all_nodes"
assert has_sub, "sub in all_nodes"

print("PASS: deep hierarchy traversal")

# ===== node() factory defaults =====
var n = node("factory_test")
assert n.name == "factory_test", "node factory name"
assert n.position.x == 0, "node default position x"
assert n.position.y == 0, "node default position y"
assert n.position.z == 0, "node default position z"
assert n.scale.x == 1, "node default scale x"
assert n.scale.y == 1, "node default scale y"
assert n.scale.z == 1, "node default scale z"

print("PASS: node() factory defaults")

# ===== add_child returns nil (void method) =====
var chain_root = node("chain_root")
var chain_child = node("chain_child")
var result = chain_root.add_child(chain_child)
assert result == nil, "add_child returns nil"
assert len(chain_root.get_children()) == 1

print("PASS: add_child void return")

# ===== Repeated remove_child =====
var dup = node("dup")
var dup_child = node("dup_child")
dup.add_child(dup_child)
assert dup.remove_child(dup_child) == true, "first remove succeeds"
assert dup.remove_child(dup_child) == false, "second remove returns false"

print("PASS: repeated remove_child")

# ===== Scene with hierarchy rendering =====
var render_scene = scene("render_hierarchy")
var cam = camera("main_cam")
render_scene.set_camera(cam)

var parent_mesh = mesh_cube(1)
parent_mesh.position = vec3(5, 0, 0)
var child_mesh = mesh_cube(0.5)
child_mesh.position = vec3(2, 0, 0)
parent_mesh.add_child(child_mesh)
render_scene.add(parent_mesh)

var render_result = render_scene.render()
assert render_result != nil, "hierarchy render works"

print("PASS: hierarchy scene render")

print("\nAll v2.0.9 scene tree tests passed!")
