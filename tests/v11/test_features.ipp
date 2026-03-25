# Test v0.11.0 - Standard Library Expansion

print("=== Testing v0.11.0 Standard Library ===")

# ====== DateTime Tests ======
print("\n--- DateTime Tests ---")

var now = datetime()
print(now)
print(now.year())
print(now.month())
print(now.day())
print(now.hour())
print(now.minute())
print(now.second())

var formatted = now.format("%Y-%m-%d %H:%M:%S")
print(formatted)

var future = now.add_days(10)
print(future)

# ====== Path Tests ======
print("\n--- Path Tests ---")

var p = path("/home/user/file.txt")
print(p)
print(path_dirname("/home/user/file.txt"))
print(path_basename("/home/user/file.txt"))
print(path_join("folder", "subfolder", "file.txt"))
print(path_exists("tests/v11/test_features.ipp"))

# ====== Hash Tests ======
print("\n--- Hash Tests ---")

var md5_hash = md5("hello")
print(md5_hash)

var sha256_hash = sha256("hello")
print(sha256_hash)

var sha1_hash = sha1("hello")
print(sha1_hash)

var sha512_hash = sha512("hello")
print(sha512_hash)

var h = hash("test")
print(h)

# ====== Base64 Tests ======
print("\n--- Base64 Tests ---")

var encoded = base64_encode("Hello, World!")
print(encoded)

var decoded = base64_decode(encoded)
print(decoded)

# ====== CSV Tests ======
print("\n--- CSV Tests ---")

var csv_data = "name,age,city\nAlice,25,NYC\nBob,30,LA"
var parsed = csv_parse(csv_data)
print(parsed)
print(len(parsed))

# ====== OS Tests ======
print("\n--- OS Tests ---")

var platform = os_platform()
print(platform)

var cwd = os_cwd()
print(cwd)

# ====== Complex Number Tests ======
print("\n--- Complex Number Tests ---")

var c1 = complex(3, 4)
print(c1)

var c2 = complex(1, 2)
print(c2)

var c3 = c1 + c2
print(c3)

var c4 = c1 - c2
print(c4)

var c5 = c1 * c2
print(c5)

var c6 = c1 / c2
print(c6)

var abs_c1 = abs(c1)
print(abs_c1)

var conj = c1.conjugate()
print(conj)

print("\nv0.11.0 tests complete!")

# ====== v0.11.2 Additional Libraries ======
print("\n=== Testing v0.11.2 Additional Libraries ===")

# ====== XML Tests ======
print("\n--- XML Tests ---")

var xml_str = "<root><item name='test'>value</item></root>"
var xml_parsed = xml_parse(xml_str)
print(xml_parsed)

# ====== UUID Tests ======
print("\n--- UUID Tests ---")

var uuid1_val = uuid4()
print(uuid1_val)

var uuid_nil_val = uuid_nil()
print(uuid_nil_val)

# ====== URL Tests ======
print("\n--- URL Tests ---")

var url = "https://example.com/path?query=value#fragment"
var parsed_url = url_parse(url)
print(parsed_url["scheme"])
print(parsed_url["netloc"])
print(parsed_url["path"])

var encoded = url_encode("hello world")
print(encoded)

var decoded = url_decode(encoded)
print(decoded)

# ====== Collections Tests ======
print("\n--- Collections Tests ---")

var dq = deque([1, 2, 3])
print(dq)
dq.push_back(4)
print(dq)
print(dq.front())
print(dq.back())
print(dq.len())

# ====== Logging Tests ======
print("\n--- Logging Tests ---")

var logger = log("test", "INFO")
logger.info("Test log message")

print("\nv0.11.2 tests complete!")
