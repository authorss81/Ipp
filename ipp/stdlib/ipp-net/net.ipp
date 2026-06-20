# ipp-net: HTTP client/server, WebSocket, FTP, SMTP
# v2.0.19.3 — bundled stdlib package
# Wraps Python builtins in clean Ipp API

# ── HTTP Client ──

export class HTTPClient {
    func init(base_url="") {
        self._base = base_url
        self._headers = {}
    }

    func set_header(name, value) {
        self._headers[name] = value
        return self
    }

    func set_headers(headers) {
        self._headers = headers
        return self
    }

    func _url(path) {
        if self._base == "" { return path }
        return self._base + path
    }

    func get(path, headers=nil) {
        return http_get(self._url(path), headers ?? self._headers)
    }

    func post(path, data=nil, headers=nil) {
        return http_post(self._url(path), data, headers ?? self._headers)
    }

    func put(path, data=nil, headers=nil) {
        return http_put(self._url(path), data, headers ?? self._headers)
    }

    func delete(path, headers=nil) {
        return http_delete(self._url(path), headers ?? self._headers)
    }

    func request(method, path, data=nil, headers=nil) {
        return http_request(self._url(path), method, data, headers ?? self._headers)
    }
}

# ── HTTP Response parser (simple) ──

export func parse_json_response(raw) {
    return json_parse(raw)
}

# ── HTTP Server ──

export func serve(handler, host="localhost", port=8080) {
    return http_serve(handler, host, port)
}

# ── WebSocket ──

export class WebSocket {
    func init(url) {
        self._url = url
        self._ws = nil
        self._connected = false
    }

    func connect() {
        if self._connected { return self }
        self._ws = websocket_connect(self._url)
        self._connected = true
        return self
    }

    func send(message) {
        if not self._connected { return false }
        websocket_send(self._ws, message)
        return true
    }

    func receive(timeout=nil) {
        if not self._connected { return nil }
        return websocket_receive(self._ws, timeout)
    }

    func close() {
        if not self._connected { return self }
        websocket_close(self._ws)
        self._connected = false
        return self
    }

    func is_connected() { return self._connected }
}

# ── FTP Client ──

export class FTPClient {
    func init(host, user, password="", port=21) {
        self._host = host
        self._user = user
        self._password = password
        self._port = port
        self._client = nil
        self._connected = false
    }

    func connect() {
        if self._connected { return self }
        self._client = ftp_connect(self._host, self._user, self._password, self._port)
        self._connected = true
        return self
    }

    func list(path=".") {
        if not self._connected { return [] }
        return ftp_list(self._client, path)
    }

    func download(remote_path, local_path) {
        if not self._connected { return false }
        ftp_get(self._client, remote_path, local_path)
        return true
    }

    func upload(local_path, remote_path) {
        if not self._connected { return false }
        ftp_put(self._client, local_path, remote_path)
        return true
    }

    func disconnect() {
        if not self._connected { return self }
        ftp_disconnect(self._client)
        self._connected = false
        return self
    }

    func is_connected() { return self._connected }
}

# ── SMTP Client ──

export class SMTPClient {
    func init(server, port=587, use_tls=true, username=nil, password=nil) {
        self._server = server
        self._port = port
        self._use_tls = use_tls
        self._username = username
        self._password = password
        self._client = nil
        self._connected = false
    }

    func connect() {
        if self._connected { return self }
        self._client = smtp_connect(self._server, self._port, self._use_tls, self._username, self._password)
        self._connected = true
        return self
    }

    func send(from_addr, to_addrs, subject, body) {
        if not self._connected { return false }
        smtp_send(self._client, from_addr, to_addrs, subject, body)
        return true
    }

    func disconnect() {
        if not self._connected { return self }
        smtp_disconnect(self._client)
        self._connected = false
        return self
    }

    func is_connected() { return self._connected }
}
