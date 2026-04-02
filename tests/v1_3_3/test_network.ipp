# Test v1.3.3 - Networking Libraries

print("=== Testing v1.3.3 Networking Libraries ===")

# ====== HTTP Tests ======
print("\n--- HTTP Tests ---")

# Test HTTP GET (using a public test API)
var result = http_get("https://httpbin.org/get")
print("GET status:", result["status"])

# Test HTTP POST
var post_result = http_post("https://httpbin.org/post", "test=data")
print("POST status:", post_result["status"])

# Test HTTP PUT
var put_result = http_put("https://httpbin.org/put", "test=data")
print("PUT status:", put_result["status"])

# Test HTTP DELETE
var delete_result = http_delete("https://httpbin.org/delete")
print("DELETE status:", delete_result["status"])

# Test generic HTTP request
var generic = http_request("https://httpbin.org/get", "GET")
print("Generic request status:", generic["status"])

# ====== URL Encode/Decode Tests ======
print("\n--- URL Encode/Decode Tests ---")

var encoded = url_encode("hello world")
print("Encoded:", encoded)

var decoded = url_decode(encoded)
print("Decoded:", decoded)

var query_encoded = url_query_build({"name": "John", "age": "30"})
print("Query encoded:", query_encoded)

var query_decoded = url_query_parse("name=John&age=30")
print("Query decoded:", query_decoded)

# ====== SMTP Tests ======
print("\n--- SMTP Tests ---")

# Test SMTP client creation (not actual connection - just verify API exists)
print("smtp_connect function exists:", type(smtp_connect))
print("smtp_disconnect function exists:", type(smtp_disconnect))
print("smtp_send function exists:", type(smtp_send))

# ====== FTP Tests ======
print("\n--- FTP Tests ---")

# Test FTP client creation (not actual connection - just verify API exists)
print("ftp_connect function exists:", type(ftp_connect))
print("ftp_disconnect function exists:", type(ftp_disconnect))
print("ftp_list function exists:", type(ftp_list))
print("ftp_get function exists:", type(ftp_get))
print("ftp_put function exists:", type(ftp_put))

print("\n=== v1.3.3 Networking tests complete! ===")
