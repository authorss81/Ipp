# Benchmark: Mandelbrot set
func mandelbrot(x, y) {
    var cr = y - 0.5
    var ci = x
    var zi = 0.0
    var zr = 0.0
    var n = 0
    while n < 100 {
        var zr2 = zr * zr
        var zi2 = zi * zi
        if zr2 + zi2 > 4.0 { return n }
        zi = 2.0 * zr * zi + ci
        zr = zr2 - zi2 + cr
        n = n + 1
    }
    return 0
}
var total = 0
var y = -1.0
while y <= 1.0 {
    var x = -1.5
    while x <= 0.5 {
        total = total + mandelbrot(x, y)
        x = x + 0.05
    }
    y = y + 0.05
}
print(total)
