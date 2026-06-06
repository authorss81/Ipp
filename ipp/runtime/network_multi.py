"""
ipp/runtime/network_multi.py
v2.4.0 — Network Multiplayer Support

Provides:
  network_connect(address)  - connect to a game server (TCP)
  network_send(data)        - send string data to server
  network_receive()         - non-blocking receive, returns nil if nothing
  network_disconnect()      - close connection
  network_host(port)        - host a game server
  network_accept()          - accept incoming connection (non-blocking)
"""

import sys
import socket
import threading

# Client state
_client_sock = None

# Server state
_server_sock = None
_server_thread = None
_server_running = False
_server_clients = []
_server_lock = threading.Lock()

# Receive buffer
_recv_buffer = ""
_recv_lock = threading.Lock()
_recv_thread = None
_recv_running = False


def _recv_worker(sock):
    global _recv_buffer
    try:
        sock.settimeout(1.0)
        while _recv_running:
            try:
                data, _ = sock.recvfrom(4096) if sock.type == socket.SOCK_DGRAM else (sock.recv(4096), None)
                if data:
                    with _recv_lock:
                        _recv_buffer += data.decode('utf-8', errors='replace')
            except socket.timeout:
                continue
            except (ConnectionResetError, BrokenPipeError, OSError):
                break
    except Exception:
        pass


def _cleanup_socket(sock):
    try:
        sock.close()
    except Exception:
        pass


def ipp_network_connect(address: str) -> str:
    """Connect to a game server at address (e.g. 'localhost:9000')."""
    global _client_sock, _recv_running, _recv_thread
    ipp_network_disconnect()
    try:
        host, port = address.rsplit(":", 1)
        port = int(port)
    except Exception:
        return f"[network error: invalid address '{address}', use host:port]"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((host, port))
        sock.setblocking(False)
        _client_sock = sock
        _recv_running = True
        _recv_thread = threading.Thread(target=_recv_worker, args=(sock,), daemon=True)
        _recv_thread.start()
        return f"[connected to {address}]"
    except Exception as e:
        _cleanup_socket(sock)
        return f"[network error: {e}]"


def ipp_network_send(data: str) -> str:
    """Send string data to the connected server."""
    global _client_sock
    if _client_sock is None:
        return "[network error: not connected]"
    try:
        _client_sock.sendall(str(data).encode('utf-8'))
        return "[data sent]"
    except Exception as e:
        ipp_network_disconnect()
        return f"[network error: {e}]"


def ipp_network_receive():
    """Receive string data (non-blocking). Returns nil if nothing available."""
    global _recv_buffer
    with _recv_lock:
        if _recv_buffer:
            data = _recv_buffer
            _recv_buffer = ""
            return data
    return None


def ipp_network_disconnect() -> str:
    """Disconnect from server."""
    global _client_sock, _recv_running, _recv_thread
    _recv_running = False
    if _client_sock:
        _cleanup_socket(_client_sock)
        _client_sock = None
    return "[disconnected]"


def ipp_network_host(port=9000) -> str:
    """Host a game server on the given port."""
    global _server_sock, _server_running
    ipp_network_stop_host()
    try:
        _server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _server_sock.bind(("0.0.0.0", int(port)))
        _server_sock.listen(5)
        _server_sock.setblocking(False)
        _server_running = True
        return f"[hosting on port {port}]"
    except Exception as e:
        _cleanup_socket(_server_sock)
        _server_sock = None
        return f"[network error: {e}]"


def ipp_network_accept():
    """Accept an incoming connection (non-blocking). Returns nil if none."""
    global _server_sock
    if not _server_sock:
        return None
    try:
        client, addr = _server_sock.accept()
        client.setblocking(False)
        with _server_lock:
            _server_clients.append(client)
        return f"[client connected from {addr[0]}:{addr[1]}]"
    except BlockingIOError:
        return None
    except Exception as e:
        return f"[network error: {e}]"


def ipp_network_broadcast(data: str) -> str:
    """Send data to all connected clients."""
    data_bytes = str(data).encode('utf-8')
    with _server_lock:
        alive = []
        for c in _server_clients:
            try:
                c.sendall(data_bytes)
                alive.append(c)
            except Exception:
                _cleanup_socket(c)
        _server_clients = alive
    return "[broadcast sent]"


def ipp_network_stop_host() -> str:
    """Stop hosting the game server."""
    global _server_sock, _server_running, _server_clients
    _server_running = False
    with _server_lock:
        for c in _server_clients:
            _cleanup_socket(c)
        _server_clients = []
    if _server_sock:
        _cleanup_socket(_server_sock)
        _server_sock = None
    return "[host stopped]"


def ipp_network_client_count() -> int:
    """Return number of connected clients."""
    with _server_lock:
        return len(_server_clients)
