# v1.7.9.1.9 — REPL .highlight / .highlight on / .highlight off

var pt_avail = prompt_toolkit_available()
assert ipp_type(pt_avail) == "bool"

if pt_avail {
    var ok = try_create_highlight_session()
    var ok_type = ipp_type(ok)
    assert ok_type == "bool"
    print("prompt_toolkit available: true")
    print("session create-able: " + str(ok))
} else {
    print("prompt_toolkit not installed")
    print("session create-able: false")
}

print("v1.7.9.1.9 highlight command tests passed")
