// Benchmark: Mandelbrot set
function mandelbrot(x, y) {
    const cr = y - 0.5;
    const ci = x;
    let zr = 0.0, zi = 0.0;
    let n = 0;
    while (n < 100) {
        const zr2 = zr * zr;
        const zi2 = zi * zi;
        if (zr2 + zi2 > 4.0) return n;
        zi = 2.0 * zr * zi + ci;
        zr = zr2 - zi2 + cr;
        n++;
    }
    return 0;
}
let total = 0;
for (let y = -1.0; y <= 1.0; y += 0.05) {
    for (let x = -1.5; x <= 0.5; x += 0.05) {
        total += mandelbrot(x, y);
    }
}
console.log(total);
