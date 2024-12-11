from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import threading
import subprocess

app = Flask(__name__)

# Hardcoded authentication key
AUTH_KEY = "your_hardcoded_key"

# Lock for thread-safe operations on the banned_ips dictionary
lock = threading.Lock()

@app.route('/ban', methods=['POST'])
def ban_ip():
    ip = request.args.get('ip')
    key = request.args.get('key')
    time = request.args.get('time', type=int)

    # Check if the key is correct
    if key != AUTH_KEY:
        return jsonify({"error": "Invalid authentication key."}), 403

    # Validate input
    if not ip or not time:
        return jsonify({"error": "IP and time parameters are required."}), 400

    # Ban the IP using UFW
    try:
        subprocess.run(["ufw", "deny", "from", ip], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Failed to ban IP {ip}: {e}"}), 500

    # Schedule unbanning the IP
    def unban():
        with lock:
            try:
                subprocess.run(["ufw", "delete", "deny", "from", ip], check=True)
            except subprocess.CalledProcessError:
                pass

    threading.Timer(time, unban).start()

    return jsonify({"message": f"IP {ip} banned for {time} seconds."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)
