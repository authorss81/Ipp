# Test Standard Library - Data Formats

# Test JSON
var json_str = '{"name": "Alice", "age": 30}'
var parsed = json_parse(json_str)
print("JSON parse:", parsed)

var obj = {"name": "Bob", "items": [1, 2, 3]}
var json_out = json_stringify(obj)
print("JSON stringify:", json_out)

# Test XML (if available)
try {
    var xml_str = '<root><item>test</item></root>'
    var xml_parsed = xml_parse(xml_str)
    print("XML parse:", xml_parsed)
} catch e {
    print("XML not available:", e)
}

# Test TOML (if available)
try {
    var toml_str = '[section]\nkey = "value"'
    var toml_parsed = toml_parse(toml_str)
    print("TOML parse:", toml_parsed)
} catch e {
    print("TOML not available:", e)
}

# Test YAML (if available)
try {
    var yaml_str = 'name: Alice\nage: 30'
    var yaml_parsed = yaml_parse(yaml_str)
    print("YAML parse:", yaml_parsed)
} catch e {
    print("YAML not available:", e)
}

# Test file operations
try {
    write_file("test_temp.txt", "Hello, World!")
    var content = read_file("test_temp.txt")
    print("File read:", content)
    
    var exists = file_exists("test_temp.txt")
    print("File exists:", exists)
    
    delete_file("test_temp.txt")
    print("File deleted")
} catch e {
    print("File operations error:", e)
}

# Test sprintf/printf
var formatted = sprintf("Name: %s, Age: %d", "Alice", 30)
print("Sprintf:", formatted)

print("\nStandard library tests completed!")