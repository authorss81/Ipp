# Test v1.1.1 - Bug Fixes

print("=== Testing v1.1.1 Bug Fixes ===")

# ====== Dict String Key Assignment ======
print("\n--- Dict String Key Assignment ---")

var d = {}
d["name"] = "Alice"
d["age"] = 30
d["city"] = "NYC"
print("Dict size: " + str(len(d)))
print("Name: " + str(d["name"]))
print("Age: " + str(d["age"]))
print("City: " + str(d["city"]))

# ====== List Index Assignment ======
print("\n--- List Index Assignment ---")

var nums = [1, 2, 3, 4, 5]
print("Original: " + str(nums))

nums[0] = 10
nums[2] = nums[2] + 100
print("After update: " + str(nums))

# ====== Nested Dict ======
print("\n--- Nested Dict ---")

var nested = {}
nested["user"] = {}
nested["user"]["name"] = "Bob"
nested["user"]["score"] = 100
print("User: " + str(nested["user"]["name"]))
print("Score: " + str(nested["user"]["score"]))

# ====== Dict Iteration ======
print("\n--- Dict Iteration ---")

# Direct dict iteration not yet supported
# Testing that dict works with known keys
var data = {"a": 1, "b": 2, "c": 3}
var sum_vals = data["a"] + data["b"] + data["c"]
print("Sum of dict values: " + str(sum_vals))

# ====== List of Dicts ======
print("\n--- List of Dicts ---")

var people = []
people.append({"name": "Alice", "age": 25})
people.append({"name": "Bob", "age": 30})
people[0]["age"] = 26
print("First person: " + str(people[0]["name"]) + ", age " + str(people[0]["age"]))
print("Second person: " + str(people[1]["name"]) + ", age " + str(people[1]["age"]))

# ====== Update Existing Keys ======
print("\n--- Update Existing Keys ---")

var counter = {}
counter["clicks"] = 0
counter["clicks"] = counter["clicks"] + 1
counter["clicks"] = counter["clicks"] + 1
print("Click count: " + str(counter["clicks"]))

# ====== Dict with Numeric Keys ======
print("\n--- Dict with Numeric Keys ---")

var matrix = {}
matrix[0] = [1, 2, 3]
matrix[1] = [4, 5, 6]
print("Row 0: " + str(matrix[0]))
print("Row 1: " + str(matrix[1]))

print("\nv1.1.1 tests complete!")
