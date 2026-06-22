# Benchmark: Prime counting
def is_prime(n):
    if n < 2: return False
    if n % 2 == 0: return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0: return False
        i += 2
    return True

count = 0
for n in range(2, 100001):
    if is_prime(n): count += 1
print(count)
