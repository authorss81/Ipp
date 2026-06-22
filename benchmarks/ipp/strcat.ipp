# Benchmark: String concatenation
var s = ""
for i in 1..5000 {
    s = s + "hello world "
}
print(len(s))
