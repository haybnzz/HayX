import socket
import json
import threading

class Peer:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.is_connected = False
        self.socket = None
        self.listener_thread = None

    def connect(self):
        """Establish connection to peer."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.address, self.port))
            self.is_connected = True
            self.listener_thread = threading.Thread(target=self.listen)
            self.listener_thread.daemon = True
            self.listener_thread.start()
            print(f"Connected to peer {self.address}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to peer {self.address}:{self.port} -> {e}")
            self.is_connected = False

    def listen(self):
        """Listen for incoming data from peer."""
        try:
            while self.is_connected:
                data = self.socket.recv(4096)
                if data:
                    message = json.loads(data.decode())
                    print(f"Message from {self.address}:{self.port} -> {message}")
                else:
                    break
        except Exception as e:
            print(f"Error receiving data from peer {self.address}:{self.port} -> {e}")
        finally:
            self.disconnect()

    def send(self, message):
        """Send a JSON message to the peer."""
        if not self.is_connected:
            return False
        try:
            self.socket.send(json.dumps(message).encode())
            return True
        except Exception as e:
            print(f"Error sending message to {self.address}:{self.port} -> {e}")
            return False

    def disconnect(self):
        """Close connection to peer."""
        if self.socket:
            self.socket.close()
        self.is_connected = False
        print(f"Disconnected from peer {self.address}:{self.port}")
