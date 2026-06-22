// Benchmark: Prime counting
function isPrime(n) {
    if (n < 2) return false;
    if (n % 2 === 0) return n === 2;
    let i = 3;
    while (i * i <= n) {
        if (n % i === 0) return false;
        i += 2;
    }
    return true;
}
let count = 0;
for (let n = 2; n <= 100000; n++) {
    if (isPrime(n)) count++;
}
console.log(count);
