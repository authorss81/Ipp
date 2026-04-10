# Test v1.5.14 - Critical Bug Fixes

print("=== Testing v1.5.14 Critical Bug Fixes ===")

# Test 1: append() function
print("\n--- Test 1: append() function ---")
var lst = [1, 2, 3]
append(lst, 4)
print("append(lst, 4): " + str(lst))

# Test 2: pop() function
print("\n--- Test 2: pop() function ---")
var lst2 = [1, 2, 3, 4]
var popped = pop(lst2)
print("pop(lst2): " + str(popped))
print("After pop: " + str(lst2))

# Test 3: insert() function
print("\n--- Test 3: insert() function ---")
var lst3 = [1, 2, 3]
insert(lst3, 1, 99)
print("insert(lst3, 1, 99): " + str(lst3))

# Test 4: remove() function
print("\n--- Test 4: remove() function ---")
var lst4 = [1, 2, 3, 2, 4]
remove(lst4, 2)
print("remove(lst4, 2): " + str(lst4))

# Test 5: clear() function
print("\n--- Test 5: clear() function ---")
var lst5 = [1, 2, 3]
clear(lst5)
print("clear(lst5): " + str(lst5))

print("\n=== v1.5.14 Tests Complete ===")
print("New in v1.5.14:")
print("  append(lst, item) - Add item to end")
print("  pop(lst, index)   - Remove and return item")
print("  insert(lst, i, x) - Insert at index")
print("  remove(lst, x)    - Remove first occurrence")
print("  clear(lst)        - Remove all items")
print("Also fixed:")
print("  - VM global_env AttributeError")