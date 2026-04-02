# Test Collections and Set

print("Testing Set type:")
var s = set([1, 2, 3, 2, 1])
print("set([1,2,3,2,1]):", s)

s.add(4)
print("after add(4):", s)

s.remove(2)
print("after remove(2):", s)

print("contains(3):", s.contains(3))
print("contains(2):", s.contains(2))

print("size:", len(s))

print("\nTesting List operations:")
var lst = [1, 2, 3]
print("list:", lst)

lst.append(4)
print("after append(4):", lst)

lst.push(5)
print("after push(5):", lst)

var popped = lst.pop()
print("pop():", popped, "list:", lst)

print("contains(2):", lst.contains(2))
print("index_of(3):", lst.index_of(3))

print("\nTesting Dict operations:")
var d = {"a": 1, "b": 2}
print("dict:", d)

d["c"] = 3
print("after d['c'] = 3:", d)

print("has_key('b'):", has_key(d, "b"))
print("has_key('x'):", has_key(d, "x"))

print("keys:", keys(d))
print("values:", values(d))
print("items:", items(d))

print("\nCollections tests completed!")