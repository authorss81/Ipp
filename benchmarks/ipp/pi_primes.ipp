# Benchmark: Prime counting (sieve)
func is_prime(n) {
    if n < 2 { return false }
    if n % 2 == 0 { return n == 2 }
    var i = 3
    while i * i <= n {
        if n % i == 0 { return false }
        i = i + 2
    }
    return true
}
var count = 0
for n in 2..100000 {
    if is_prime(n) { count = count + 1 }
}
print(count)
