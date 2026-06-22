// Benchmark: String concatenation
let s = "";
for (let i = 0; i < 5000; i++) {
    s += "hello world ";
}
console.log(s.length);
