"""
WebSocket module for Ipp language - WebSocket client support
"""
import asyncio
import json as _json
import threading
import time

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False


class WebSocketClient:
    """WebSocket client wrapper for Ipp"""
    
    def __init__(self, url):
        self.url = url
        self._ws = None
        self._loop = None
        self._thread = None
        self._connected = False
        self._messages = []
        self._closed = False
        self._error = None
    
    def connect(self):
        """Connect to the WebSocket server"""
        if not HAS_WEBSOCKETS:
            raise RuntimeError("websockets library not installed. Install with: pip install websockets")
        
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        future = asyncio.run_coroutine_threadsafe(self._connect(), self._loop)
        try:
            future.result(timeout=10)
        except Exception as e:
            raise RuntimeError(f"WebSocket connection failed: {e}")
        
        self._connected = True
        return True
    
    def _run_loop(self):
        """Run the asyncio event loop in a separate thread"""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
    
    async def _connect(self):
        """Internal async connect method"""
        self._ws = await websockets.connect(self.url)
        self._start_reader()
    
    def _start_reader(self):
        """Start reading messages in the background"""
        asyncio.run_coroutine_threadsafe(self._read_loop(), self._loop)
    
    async def _read_loop(self):
        """Continuously read messages from the WebSocket"""
        try:
            while not self._closed:
                message = await self._ws.recv()
                self._messages.append(message)
        except websockets.exceptions.ConnectionClosed:
            self._connected = False
        except Exception as e:
            self._error = str(e)
    
    def send(self, message):
        """Send a message to the WebSocket server"""
        if not self._connected:
            raise RuntimeError("WebSocket not connected")
        
        if isinstance(message, dict):
            message = _json.dumps(message)
        
        future = asyncio.run_coroutine_threadsafe(self._ws.send(message), self._loop)
        try:
            future.result(timeout=5)
        except Exception as e:
            raise RuntimeError(f"Failed to send message: {e}")
        
        return True
    
    def receive(self, timeout=5):
        """Receive a message from the WebSocket server"""
        if not self._connected:
            raise RuntimeError("WebSocket not connected")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._messages:
                return self._messages.pop(0)
            time.sleep(0.1)
        
        return None
    
    def receive_json(self, timeout=5):
        """Receive a JSON message from the WebSocket server"""
        message = self.receive(timeout)
        if message is None:
            return None
        try:
            return _json.loads(message)
        except _json.JSONDecodeError:
            raise RuntimeError("Failed to parse message as JSON")
    
    def is_connected(self):
        """Check if the WebSocket is connected"""
        return self._connected
    
    def close(self):
        """Close the WebSocket connection"""
        if self._connected and self._ws:
            self._closed = True
            future = asyncio.run_coroutine_threadsafe(self._ws.close(), self._loop)
            try:
                future.result(timeout=5)
            except Exception:
                pass
            self._connected = False
    
    def __repr__(self):
        return f"<WebSocketClient url={self.url} connected={self._connected}>"


def websocket_connect(url):
    """Create and connect a WebSocket client"""
    client = WebSocketClient(url)
    client.connect()
    return client


def websocket_send(client, message):
    """Send a message via WebSocket"""
    if not isinstance(client, WebSocketClient):
        raise RuntimeError("First argument must be a WebSocketClient")
    return client.send(message)


def websocket_receive(client, timeout=5):
    """Receive a message via WebSocket"""
    if not isinstance(client, WebSocketClient):
        raise RuntimeError("First argument must be a WebSocketClient")
    return client.receive(timeout)


def websocket_close(client):
    """Close a WebSocket connection"""
    if not isinstance(client, WebSocketClient):
        raise RuntimeError("First argument must be a WebSocketClient")
    client.close()
    return True
