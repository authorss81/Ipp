# Test v1.5.25: Static methods on classes
# Bug: Static methods were inaccessible on class

class Math {
    static func square(x) {
        return x * x
    }
    
    static func add(a, b) {
        return a + b
    }
    
    static func multiply(a, b, c) {
        return a * b * c
    }
}

# Test static method calls
assert Math.square(5) == 25
assert Math.add(3, 4) == 7
assert Math.multiply(2, 3, 4) == 24

# Test static and instance methods mixed
class Calculator {
    static func max(a, b) {
        if a > b { return a }
        return b
    }
    
    func init() {
        self.value = 0
    }
    
    func add(n) {
        self.value = self.value + n
        return self.value
    }
}

assert Calculator.max(10, 20) == 20
assert Calculator.max(5, 3) == 5

var calc = Calculator()
assert calc.add(5) == 5
assert calc.add(3) == 8

print("v1.5.25: Static methods tests PASSED")