# v2.4.0 network multiplayer builtins
# Test basic API exists and error handling works

# network_connect with invalid address should return error
var err = network_connect("invalid")
print(err)

# network_send without connection should return error
var err2 = network_send("hello")
print(err2)

# network_receive without connection should return nil
var recv = network_receive()
print("recv=nil:", recv == nil)
assert recv == nil

# network_disconnect without connection should not crash
var disc = network_disconnect()
print(disc)

# Test hosting
var host = network_host(9999)
print(host)

var client_count = network_client_count()
print("clients:", client_count)
assert client_count == 0

var accept = network_accept()
print("accept=nil:", accept == nil)
assert accept == nil

var stop = network_stop_host()
print(stop)

print("All v2.4.0 network tests passed")
