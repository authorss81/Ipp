// Benchmark: Fibonacci (recursive)
function fib(n) {
    if (n < 2) return n;
    return fib(n - 1) + fib(n - 2);
}
let total = 0;
for (let i = 0; i < 5; i++) {
    total += fib(28);
}
console.log(total);
