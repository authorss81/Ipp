# Comprehensive test for Ipp v0.1.1

# Test 1: Variables
var x = 10
let y = 20
print("Test 1 - Variables:")
print(x)
print(y)

# Test 2: Arithmetic
print("Test 2 - Arithmetic:")
print(5 + 3)
print(10 - 4)
print(6 * 7)
print(20 / 4)
print(17 % 5)
print(2 ^ 8)

# Test 3: Comparison
print("Test 3 - Comparison:")
print(5 > 3)
print(5 == 5)
print(5 != 3)

# Test 4: Lists
print("Test 4 - Lists:")
var nums = [1, 2, 3, 4, 5]
print(len(nums))
print(nums[0])
print(nums[4])

# Test 5: Dicts
print("Test 5 - Dictionaries:")
var person = {"name": "Bob", "age": 30}
print(person["name"])
print(keys(person))
print(values(person))

# Test 6: Control Flow
print("Test 6 - Control Flow:")
if x > 5 {
    print("x is big")
}

for i in 0..5 {
    print(i)
}

# Test 7: Functions
print("Test 7 - Functions:")
func add(a, b) {
    return a + b
}
print(add(5, 3))

# Test 8: Closures
print("Test 8 - Closures:")
func make_counter() {
    var count = 0
    func increment() {
        count = count + 1
        return count
    }
    return increment
}
var counter = make_counter()
print(counter())
print(counter())

# Test 9: Classes
print("Test 9 - Classes:")
class Dog {
    func init(name) {
        self.name = name
    }
    
    func bark() {
        return self.name + " says Woof!"
    }
}
var dog = Dog("Rex")
print(dog.bark())

# Test 10: Math functions
print("Test 10 - Math functions:")
print(abs(-5))
print(min(1, 2, 3))
print(max(1, 2, 3))
print(sum(1, 2, 3))
print(sqrt(16))
print(pow(2, 3))
print(sin(0))
print(cos(0))

print("=== All tests passed! ===")
