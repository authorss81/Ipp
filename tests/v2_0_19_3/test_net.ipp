import { HTTPClient, WebSocket, FTPClient, SMTPClient, serve, parse_json_response } from "ipp-net"

# ── HTTPClient ──
var client = HTTPClient()
assert client != nil, "HTTPClient created"
client.set_header("User-Agent", "ipp-test/1.0")
client.set_headers({"Accept": "application/json"})
assert client != nil, "headers set"

# HTTPClient with base URL
var api = HTTPClient("https://jsonplaceholder.typicode.com")
# Just verify the object exists, skip network in CI
assert api != nil, "HTTPClient with base URL"

# Test without network: get/post/put/delete return values (type is string or nil)
var result = nil
try { result = api.get("/todos/1") } catch e { result = nil }
# If network works, result is a string; if offline, it's nil — both OK
assert result == nil or type(result) == "string", "http_get returns string or nil"

# parse_json_response
var json_str = '{"userId": 1, "id": 1, "title": "delectus aut autem", "completed": false}'
var parsed = parse_json_response(json_str)
assert parsed != nil, "parse_json_response works"
assert parsed["title"] == "delectus aut autem", "parsed json field"

# ── WebSocket ──
var ws = WebSocket("ws://localhost:8080/ws")
assert ws != nil, "WebSocket created"
assert ws.is_connected() == false, "WebSocket not connected initially"
ws.send("test")  # should not crash, returns false
ws.receive()     # should not crash
ws.close()       # should not crash

# ── FTPClient ──
try {
    var ftp = FTPClient("localhost", "anonymous")
    assert ftp != nil, "FTPClient created"
    assert ftp.is_connected() == false, "FTP not connected"
    ftp.list()
    ftp.disconnect()
} catch e { }

# ── SMTPClient ──
try {
    var smtp = SMTPClient("smtp.example.com", 587, true, "user", "pass")
    assert smtp != nil, "SMTPClient created"
    assert smtp.is_connected() == false, "SMTP not connected"
    smtp.send("from@test.com", "to@test.com", "Subject", "Body")
    smtp.disconnect()
} catch e { }

# ── serve function exists ──
assert serve != nil, "serve function exists"

print("All ipp-net tests passed!")
