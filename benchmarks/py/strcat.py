# Benchmark: String concatenation
s = ""
for i in range(5000):
    s += "hello world "
print(len(s))
