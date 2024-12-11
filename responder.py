from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import threading

app = Flask(__name__)

# Hardcoded authentication key
AUTH_KEY = "your_hardcoded_key"

# Dictionary to store banned IPs and their ban expiration times
banned_ips = {}

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

    # Calculate the ban expiration time
    ban_until = datetime.now() + timedelta(seconds=time)

    # Add the IP to the banned list
    with lock:
        banned_ips[ip] = ban_until

    return jsonify({"message": f"IP {ip} banned for {time} seconds."}), 200

@app.before_request
def check_ban():
    ip = request.remote_addr

    # Check if the IP is banned
    with lock:
        if ip in banned_ips:
            if datetime.now() < banned_ips[ip]:
                return jsonify({"error": "Your IP is banned."}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)

