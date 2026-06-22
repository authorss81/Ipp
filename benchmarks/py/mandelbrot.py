# Benchmark: Mandelbrot set
def mandelbrot(x, y):
    cr = y - 0.5
    ci = x
    zr = 0.0
    zi = 0.0
    n = 0
    while n < 100:
        zr2 = zr * zr
        zi2 = zi * zi
        if zr2 + zi2 > 4.0: return n
        zi = 2.0 * zr * zi + ci
        zr = zr2 - zi2 + cr
        n += 1
    return 0

total = 0
y = -1.0
while y <= 1.0:
    x = -1.5
    while x <= 0.5:
        total += mandelbrot(x, y)
        x += 0.05
    y += 0.05
print(total)
