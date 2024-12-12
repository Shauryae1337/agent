import time
import subprocess
from flask import Flask, render_template, request, jsonify
import threading
import os

app = Flask(__name__)

# Hardcoded IP of server from which logs and rate will be fetched
log_server_ip = '54.209.251.197'

# File paths for output files
malformed_requests_file = 'malformed_requests.txt'
flood_data_file = 'flood_data.txt'
connections_file = 'connections.txt'
rate_file = 'rate.txt'
new_logs_file = 'new.logs'

# Background task to periodically fetch logs and run components
def background_task():
    while True:
        # Step 1: Fetch new logs
        subprocess.run(["curl", f"http://{log_server_ip}:80/logs", "-o", new_logs_file])
        
        # Step 2: Run each component
        subprocess.run(["python3", "malform.py"])
        subprocess.run(["python3", "floodec.py"])
        subprocess.run(["python3", "log_analyzer.py"])

        # Wait for 5 seconds before running the cycle again
        time.sleep(5)

# Start the background task in a separate thread
def start_background_task():
    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/rate', methods=['POST'])
def get_rate():
    ip = request.form['ip']
    subprocess.run(["curl", f"http://{log_server_ip}:80/rate?ip={ip}", "-o", rate_file])

    with open(rate_file, 'r') as file:
        rate_data = file.read()
    
    return jsonify({'rate_data': rate_data})

@app.route('/malformed_requests')
def malformed_requests():
    with open(malformed_requests_file, 'r') as file:
        data = file.readlines()
    
    malformed_data = [line.strip() for line in data if int(line.split(',')[2].strip()) > 0]
    return jsonify({'malformed_requests': malformed_data})

@app.route('/flood_data', methods=['POST'])
def flood_data():
    limit_topics_sec = int(request.form['limit_topics_sec'])
    limit_num_topics = int(request.form['limit_num_topics'])

    with open(flood_data_file, 'r') as file:
        data = file.readlines()

    filtered_data = []
    for line in data:
        ip, client_id, total_topics, topics_per_sec = line.split(",")
        topics_per_sec = float(topics_per_sec.split(":")[1].strip())
        total_topics = int(total_topics.split(":")[1].strip())

        if topics_per_sec > limit_topics_sec or total_topics > limit_num_topics:
            filtered_data.append(line.strip())

    return jsonify({'flood_data': filtered_data})

@app.route('/active_connections')
def active_connections():
    with open(connections_file, 'r') as file:
        data = file.readlines()
    
    if not data or data[0].strip() == "No IPs currently connected.":
        return jsonify({'connections': "No active connections"})
    
    return jsonify({'connections': data})

if __name__ == '__main__':
    # Start the background task
    start_background_task()
    app.run(debug=True, host='0.0.0.0', port=8000)

