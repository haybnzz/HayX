from hayx.web.app import app, socketio
from config import Config

if __name__ == "__main__":
    print(f"🚀 Starting HayX Web Server on http://localhost:{Config.WEB_PORT}")
    socketio.run(app, host="0.0.0.0", port=Config.WEB_PORT, debug=False)
