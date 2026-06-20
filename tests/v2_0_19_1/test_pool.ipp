import { ObjectPool } from "ipp-pool"

var counter = 0
var factory = func() { counter = counter + 1; return {"id": counter} }
var last_reset = nil
var resetter = func(obj) { last_reset = obj }

# Basic acquire/release
var pool = ObjectPool(factory, resetter, 2)
assert pool.size() == 2, "pool pre-filled"
assert pool.active_count() == 0, "no active yet"

var a = pool.acquire()
assert a.id == 2, "first from pool"
assert pool.size() == 1, "one left"
assert pool.active_count() == 1, "one active"

var b = pool.acquire()
assert b.id == 1, "second from pool"
assert pool.size() == 0, "empty pool"
assert pool.active_count() == 2, "two active"

# Acquire creates new when empty
var c = pool.acquire()
assert c.id == 3, "new object created"
assert pool.active_count() == 3, "three active"

# Release returns to pool
var r1 = pool.release(a)
assert r1 == true, "release succeeded"
assert pool.size() == 1, "one available"
assert pool.active_count() == 2, "two active"
assert last_reset == a, "resetter called on release"

# Re-acquire from pool
var d = pool.acquire()
assert d.id == 2, "re-acquired released object"
assert pool.size() == 0, "pool empty again"

# Release non-active object returns false
var fake = {"id": 99}
assert pool.release(fake) == false, "release non-active returns false"

# max_size
var limited = ObjectPool(factory, nil, 0, 2)
var x1 = limited.acquire()
var x2 = limited.acquire()
assert limited.acquire() == nil, "max size enforced"

# resize
var resizable = ObjectPool(factory, nil, 0)
assert resizable.size() == 0, "resize start empty"
resizable.resize(3)
assert resizable.size() == 3, "resize creates objects"

# clear
var clear_pool = ObjectPool(factory, nil, 2)
var ca = clear_pool.acquire()
assert clear_pool.active_count() == 1, "clear test active"
clear_pool.clear()
assert clear_pool.size() == 0, "clear empties available"
assert clear_pool.active_count() == 0, "clear empties active"

# release_all
var all_pool = ObjectPool(factory, nil, 2)
var ra1 = all_pool.acquire()
var ra2 = all_pool.acquire()
assert all_pool.active_count() == 2, "release_all active count"
all_pool.release_all()
assert all_pool.active_count() == 0, "release_all clears active"
assert all_pool.size() == 2, "release_all returns active to available"

# capacity
assert all_pool.capacity() == 2, "capacity total"
var capped = ObjectPool(factory, nil, 3, 10)
assert capped.capacity() == 10, "capacity respects max"

# Default factory (no factory = empty dict)
var default_pool = ObjectPool(nil, nil, 0, nil)
var default_obj = default_pool.acquire()
assert default_obj != nil, "default factory creates object"
assert len(keys(default_obj)) == 0, "default factory creates empty dict"

print("All pool tests passed!")
