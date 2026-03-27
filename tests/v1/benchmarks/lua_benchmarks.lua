-- ============================================
-- Lua Benchmark Comparison for Ipp
-- ============================================
-- Run with: lua benchmarks/lua_benchmarks.lua
-- ============================================

local clock = os.clock

print("=" .. string.rep("=", 58))
print("LUA BENCHMARKS (for comparison)")
print("=" .. string.rep("=", 58))

-- --------------------------------------------
-- Benchmark 1: Integer Arithmetic
-- --------------------------------------------
print("\n--- Benchmark 1: Integer Arithmetic ---")

local function bench_integer_add(n)
    local sum = 0
    for i = 0, n - 1 do
        sum = sum + i
    end
    return sum
end

local function bench_integer_mul(n)
    local product = 1
    for i = 1, n do
        product = product * i
    end
    return product
end

local function bench_integer_mod(n)
    local result = 0
    for i = 0, n - 1 do
        result = result + (i % 7)
    end
    return result
end

local iterations = 100000

local start = clock()
local result = bench_integer_add(iterations)
local elapsed = clock() - start
print("Integer Add: " .. result .. " in " .. string.format("%.4f", elapsed) .. "s")

start = clock()
result = bench_integer_mul(100)
elapsed = clock() - start
print("Integer Mul (100!): " .. result .. " in " .. string.format("%.4f", elapsed) .. "s")

start = clock()
result = bench_integer_mod(iterations)
elapsed = clock() - start
print("Integer Mod: " .. result .. " in " .. string.format("%.4f", elapsed) .. "s")

-- --------------------------------------------
-- Benchmark 2: Floating Point Math
-- --------------------------------------------
print("\n--- Benchmark 2: Floating Point Math ---")

local function bench_float_trig(n)
    local sum = 0.0
    for i = 0, n - 1 do
        sum = sum + math.sin(i)
    end
    return sum
end

local function bench_float_sqrt(n)
    local sum = 0.0
    for i = 1, n do
        sum = sum + math.sqrt(i)
    end
    return sum
end

local iterations = 50000

start = clock()
result = bench_float_trig(iterations)
elapsed = clock() - start
print("Float Trig (sin): " .. string.format("%.4f", result) .. " in " .. string.format("%.4f", elapsed) .. "s")

start = clock()
result = bench_float_sqrt(iterations)
elapsed = clock() - start
print("Float Sqrt: " .. string.format("%.4f", result) .. " in " .. string.format("%.4f", elapsed) .. "s")

-- --------------------------------------------
-- Benchmark 3: String Operations
-- --------------------------------------------
print("\n--- Benchmark 3: String Operations ---")

local function bench_string_concat(n)
    local s = ""
    for i = 0, n - 1 do
        s = s .. "x"
    end
    return #s
end

local function bench_string_split(s, n)
    local count = 0
    for i = 1, n do
        local parts = {}
        for part in string.gmatch(s, "[^,]+") do
            table.insert(parts, part)
        end
        count = count + #parts
    end
    return count
end

local iterations = 10000

start = clock()
result = bench_string_concat(iterations)
elapsed = clock() - start
print("String Concat: " .. result .. " in " .. string.format("%.4f", elapsed) .. "s")

local test_string = "a,b,c,d,e,f,g,h,i,j"
start = clock()
result = bench_string_split(test_string, iterations)
elapsed = clock() - start
print("String Split: " .. result .. " in " .. string.format("%.4f", elapsed) .. "s")

-- --------------------------------------------
-- Benchmark 4: Function Calls
-- --------------------------------------------
print("\n--- Benchmark 4: Function Calls ---")

local function bench_recursive_fib(n)
    if n <= 1 then
        return n
    end
    return bench_recursive_fib(n - 1) + bench_recursive_fib(n - 2)
end

local function bench_iterative_fib(n)
    if n <= 1 then
        return n
    end
    local a, b = 0, 1
    for i = 2, n do
        a, b = b, a + b
    end
    return b
end

local function bench_higher_order(n, f)
    local result = 0
    for i = 0, n - 1 do
        result = result + f(i)
    end
    return result
end

local function simple_add(n)
    return n + 1
end

local iterations = 25

start = clock()
result = bench_recursive_fib(iterations)
elapsed = clock() - start
print("Recursive Fibonacci(25): " .. result .. " in " .. string.format("%.4f", elapsed) .. "s")

start = clock()
result = bench_iterative_fib(10000)
elapsed = clock() - start
print("Iterative Fibonacci(10000): " .. result .. " in " .. string.format("%.4f", elapsed) .. "s")

start = clock()
result = bench_higher_order(100000, simple_add)
elapsed = clock() - start
print("Higher-Order Function: " .. result .. " in " .. string.format("%.4f", elapsed) .. "s")

-- --------------------------------------------
-- Benchmark 5: Table Operations
-- --------------------------------------------
print("\n--- Benchmark 5: Table Operations ---")

local function bench_table_append(n)
    local tbl = {}
    for i = 0, n - 1 do
        table.insert(tbl, i)
    end
    return #tbl
end

local function bench_table_iterate(tbl)
    local sum = 0
    for _, v in ipairs(tbl) do
        sum = sum + v
    end
    return sum
end

local function bench_table_comprehension(n)
    local tbl = {}
    for i = 0, n - 1 do
        tbl[i + 1] = i * 2
    end
    return #tbl
end

local iterations = 50000

start = clock()
result = bench_table_append(iterations)
elapsed = clock() - start
print("Table Append: " .. result .. " in " .. string.format("%.4f", elapsed) .. "s")

local test_table = bench_table_append(iterations)
start = clock()
result = bench_table_iterate(test_table)
elapsed = clock() - start
print("Table Iterate: " .. result .. " in " .. string.format("%.4f", elapsed) .. "s")

start = clock()
result = bench_table_comprehension(iterations)
elapsed = clock() - start
print("Table Comprehension: " .. result .. " in " .. string.format("%.4f", elapsed) .. "s")

-- --------------------------------------------
-- Benchmark 6: Vector Operations
-- --------------------------------------------
print("\n--- Benchmark 6: Vector Operations ---")

local Vec2 = {}
Vec2.__index = Vec2
function Vec2.new(x, y)
    return setmetatable({x = x or 0, y = y or 0}, Vec2)
end

local function bench_vec2_operations(n)
    local sum = Vec2.new(0, 0)
    for i = 0, n - 1 do
        local v = Vec2.new(i, i + 1)
        sum.x = sum.x + v.x
        sum.y = sum.y + v.y
    end
    return sum
end

local function bench_vec2_distance(n)
    local total = 0.0
    for i = 0, n - 1 do
        local a = Vec2.new(i, i)
        local b = Vec2.new(i + 1, i + 1)
        local dx = b.x - a.x
        local dy = b.y - a.y
        total = total + math.sqrt(dx * dx + dy * dy)
    end
    return total
end

local iterations = 100000

start = clock()
result = bench_vec2_operations(iterations)
elapsed = clock() - start
print("Vec2 Operations: (" .. string.format("%.2f", result.x) .. ", " .. string.format("%.2f", result.y) .. ") in " .. string.format("%.4f", elapsed) .. "s")

start = clock()
result = bench_vec2_distance(iterations)
elapsed = clock() - start
print("Vec2 Distance: " .. string.format("%.4f", result) .. " in " .. string.format("%.4f", elapsed) .. "s")

-- --------------------------------------------
-- Benchmark 7: Physics
-- --------------------------------------------
print("\n--- Benchmark 7: Physics ---")

local function bench_physics(particles, iterations)
    local positions = {}
    local velocities = {}
    
    for i = 0, particles - 1 do
        positions[i + 1] = Vec2.new(i, i)
        velocities[i + 1] = Vec2.new(1.0, 1.0)
    end
    
    for t = 0, iterations - 1 do
        for i = 0, particles - 1 do
            positions[i + 1].x = positions[i + 1].x + velocities[i + 1].x * 0.016
            positions[i + 1].y = positions[i + 1].y + velocities[i + 1].y * 0.016
        end
    end
    return particles
end

local particles = 1000
local iterations = 1000

start = clock()
result = bench_physics(particles, iterations)
elapsed = clock() - start
print("Physics (1000 particles, 1000 iters): " .. result .. " in " .. string.format("%.4f", elapsed) .. "s")

-- --------------------------------------------
-- Benchmark 8: Particles
-- --------------------------------------------
print("\n--- Benchmark 8: Particle System ---")

local function bench_particles(count, lifetime)
    local particles = {}
    
    for i = 0, count - 1 do
        particles[i + 1] = {
            x = i,
            y = i,
            vx = 1.0,
            vy = 2.0,
            life = lifetime
        }
    end
    
    local total_life = 0
    for frame = 0, 99 do
        for _, p in ipairs(particles) do
            p.x = p.x + p.vx
            p.y = p.y + p.vy
            p.life = p.life - 1
            if p.life > 0 then
                total_life = total_life + p.life
            end
        end
    end
    
    return total_life
end

local count = 5000
local lifetime = 100

start = clock()
result = bench_particles(count, lifetime)
elapsed = clock() - start
print("Particles (5000, 100 frames): " .. result .. " in " .. string.format("%.4f", elapsed) .. "s")

print("\n" .. "=" .. string.rep("=", 58))
print("BENCHMARKS COMPLETE")
print("=" .. string.rep("=", 58))
