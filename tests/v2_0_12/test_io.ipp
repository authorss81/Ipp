# v2.0.12 — ipp-io Package: File I/O, JSON, Environment, CLI Args
import { write_file, read_file, file_exists, delete_file, json_parse, json_stringify, get_env } from "ipp-io"

print("=== ipp-io Package v2.0.12 ===")

# File write + read roundtrip
var test_file = "test_ipp_io.txt"
write_file(test_file, "hello ipp")
var ok = file_exists(test_file)
assert ok == true
var content = read_file(test_file)
assert content == "hello ipp"
delete_file(test_file)
assert file_exists(test_file) == false
print("PASS: file write/read/delete")

# JSON roundtrip
var data = {"name": "Alice", "score": 100, "items": ["sword", "shield"]}
var text = json_stringify(data)
var back = json_parse(text)
assert back["name"] == "Alice"
assert back["score"] == 100
assert back["items"][0] == "sword"
print("PASS: JSON roundtrip")

# Pretty JSON
var pretty = json_stringify({"x": 1, "y": 2}, indent=2)
# No easy way to assert contains in Ipp, just verify it parses back
var back2 = json_parse(pretty)
assert back2["x"] == 1
assert back2["y"] == 2
print("PASS: JSON pretty print")

# Environment variable (HOME on Linux/macOS, USERPROFILE on Windows)
var home = get_env("USERPROFILE", get_env("HOME", "no-home"))
assert home != nil
assert home != ""
print("PASS: get_env")

# get_args should return a list
var args = get_args()
assert type(args) == "list"
print("PASS: get_args returns list")

print("\nAll v2.0.12 ipp-io tests passed!")
