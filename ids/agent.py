from flask import Flask, Response, request
from scapy.all import sniff, IP, TCP
import threading
import os
from datetime import datetime, timedelta
import string
import time

app = Flask(__name__)

# Paths and constants
MOSQUITTO_LOG_PATH = "/var/log/mosquitto/mosquitto.log"
NETLOG_FILE = "mqtt_logs.txt"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
PORT = 1833

# Store logs in-memory for faster access in the rate calculation
log_entries = []

def packet_handler(packet):
    if IP in packet and TCP in packet and packet[TCP].dport == PORT:
        log_packet(packet)

def log_packet(packet):
    # Extracting required information
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source = packet[IP].src
    dest = packet[IP].dst
    payload = bytes(packet[TCP].payload).decode(errors="replace")  # Decode with error handling

    # Remove non-ASCII characters from payload
    payload = ''.join(char for char in payload if char in string.printable)

    # Format the log entry
    log_entry = {"timestamp": timestamp, "source": source, "dest": dest, "payload": payload}

    # Add to in-memory log
    log_entries.append(log_entry)

    # Manage file size and log to the file
    manage_file_size()

def manage_file_size():
    if os.path.getsize(NETLOG_FILE) > MAX_FILE_SIZE:
        with open(NETLOG_FILE, "r+") as file:
            lines = file.readlines()
            file.seek(0)
            file.writelines(lines[len(lines)//2:])  # Keep the latter half
            file.truncate()

def start_sniffer():
    print("Starting MQTT packet capturer...")
    sniff(prn=packet_handler, filter=f"tcp port {PORT}", store=0)

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        if os.path.exists(MOSQUITTO_LOG_PATH):
            with open(MOSQUITTO_LOG_PATH, 'r') as log_file:
                logs = log_file.read()  # Read entire content of the log file
            return Response(logs, mimetype='text/plain')  # Return as plain text
        else:
            return Response("Log file not found.", status=404, mimetype='text/plain')
    except Exception as e:
        return Response(f"Error: {str(e)}", status=500, mimetype='text/plain')

@app.route('/netlog', methods=['GET'])
def get_netlog():
    try:
        if os.path.exists(NETLOG_FILE):
            with open(NETLOG_FILE, 'r') as log_file:
                logs = log_file.read()  # Read entire content of the network log file
            return Response(logs, mimetype='text/plain')  # Return as plain text
        else:
            return Response("Network log file not found.", status=404, mimetype='text/plain')
    except Exception as e:
        return Response(f"Error: {str(e)}", status=500, mimetype='text/plain')

@app.route('/rate', methods=['GET'])
def get_request_rate():
    ip_address = request.args.get('ip')
    if not ip_address:
        return Response("Missing 'ip' parameter.", status=400, mimetype='text/plain')

    try:
        # Get current time and calculate the time window (last 5 seconds)
        end_time = datetime.now()
        start_time = end_time - timedelta(seconds=5)

        # Count the requests in the last 5 seconds for the specific IP
        request_count = sum(
            1 for entry in log_entries
            if start_time <= datetime.strptime(entry['timestamp'], "%Y-%m-%d %H:%M:%S") <= end_time
            and entry['source'] == ip_address
        )

        # Calculate the rate (requests per second over the last 5 seconds)
        rate = request_count / 5  # Requests per second
        return Response(f"Requests per second for IP {ip_address}: {rate:.2f}", mimetype='text/plain')

    except Exception as e:
        return Response(f"Error: {str(e)}", status=500, mimetype='text/plain')

if __name__ == '__main__':
    # Start the packet sniffer in a separate thread
    sniffer_thread = threading.Thread(target=start_sniffer, daemon=True)
    sniffer_thread.start()

    # Start the Flask app
    app.run(host='0.0.0.0', port=5000)  # Accessible from the network

