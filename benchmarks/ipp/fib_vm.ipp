# Benchmark: Fibonacci (recursive) - VM
func fib(n) {
    if n < 2 { return n }
    return fib(n - 1) + fib(n - 2)
}
var total = 0
for i in 1..10 {
    total = total + fib(35)
}
print(total)
