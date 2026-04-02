"""
HTTP module for Ipp language - HTTP client and server support
"""
import urllib.request
import urllib.parse
import urllib.error
import json as _json


class HttpResponse:
    """HTTP response wrapper for Ipp"""
    def __init__(self, status_code, headers, body, url=None):
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self.url = url
    
    def __repr__(self):
        return f"<HttpResponse {self.status_code}>"
    
    def json(self):
        """Parse response body as JSON"""
        try:
            return _json.loads(self.body)
        except _json.JSONDecodeError:
            raise RuntimeError("Failed to parse response as JSON")
    
    def text(self):
        """Return response body as string"""
        return self.body


def http_get(url, headers=None):
    """Make an HTTP GET request"""
    try:
        req = urllib.request.Request(url)
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)
        
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            resp_headers = dict(response.headers)
            return HttpResponse(response.status, resp_headers, body, url)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        return HttpResponse(e.code, dict(e.headers), body, url)
    except Exception as e:
        raise RuntimeError(f"HTTP GET failed: {e}")


def http_post(url, data=None, headers=None, json_data=None):
    """Make an HTTP POST request"""
    try:
        req = urllib.request.Request(url, method='POST')
        
        if json_data is not None:
            req.add_header('Content-Type', 'application/json')
            data = _json.dumps(json_data).encode('utf-8')
        elif data is not None:
            if isinstance(data, dict):
                data = urllib.parse.urlencode(data).encode('utf-8')
            elif isinstance(data, str):
                data = data.encode('utf-8')
        
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)
        
        req.data = data
        
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            resp_headers = dict(response.headers)
            return HttpResponse(response.status, resp_headers, body, url)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        return HttpResponse(e.code, dict(e.headers), body, url)
    except Exception as e:
        raise RuntimeError(f"HTTP POST failed: {e}")


def http_put(url, data=None, headers=None, json_data=None):
    """Make an HTTP PUT request"""
    try:
        req = urllib.request.Request(url, method='PUT')
        
        if json_data is not None:
            req.add_header('Content-Type', 'application/json')
            data = _json.dumps(json_data).encode('utf-8')
        elif data is not None:
            if isinstance(data, dict):
                data = urllib.parse.urlencode(data).encode('utf-8')
            elif isinstance(data, str):
                data = data.encode('utf-8')
        
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)
        
        req.data = data
        
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            resp_headers = dict(response.headers)
            return HttpResponse(response.status, resp_headers, body, url)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        return HttpResponse(e.code, dict(e.headers), body, url)
    except Exception as e:
        raise RuntimeError(f"HTTP PUT failed: {e}")


def http_delete(url, headers=None):
    """Make an HTTP DELETE request"""
    try:
        req = urllib.request.Request(url, method='DELETE')
        
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)
        
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            resp_headers = dict(response.headers)
            return HttpResponse(response.status, resp_headers, body, url)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        return HttpResponse(e.code, dict(e.headers), body, url)
    except Exception as e:
        raise RuntimeError(f"HTTP DELETE failed: {e}")


def http_request(url, method='GET', data=None, headers=None, json_data=None):
    """Make a generic HTTP request"""
    method = method.upper()
    if method == 'GET':
        return http_get(url, headers)
    elif method == 'POST':
        return http_post(url, data, headers, json_data)
    elif method == 'PUT':
        return http_put(url, data, headers, json_data)
    elif method == 'DELETE':
        return http_delete(url, headers)
    else:
        raise RuntimeError(f"Unsupported HTTP method: {method}")


def url_encode(data):
    """URL encode a dictionary of parameters"""
    if isinstance(data, dict):
        return urllib.parse.urlencode(data)
    raise RuntimeError("url_encode expects a dictionary")


def url_decode(query_string):
    """URL decode a query string into a dictionary"""
    if isinstance(query_string, str):
        return dict(urllib.parse.parse_qsl(query_string))
    raise RuntimeError("url_decode expects a string")


def url_join(base, path):
    """Join a base URL with a path"""
    return urllib.parse.urljoin(base, path)


def url_parse(url):
    """Parse a URL into its components"""
    parsed = urllib.parse.urlparse(url)
    return {
        'scheme': parsed.scheme,
        'netloc': parsed.netloc,
        'path': parsed.path,
        'params': parsed.params,
        'query': parsed.query,
        'fragment': parsed.fragment
    }
