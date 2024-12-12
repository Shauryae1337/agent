import time
from datetime import datetime
import os

LOG_FILE = "mqtt_logs.txt"

def monitor_requests(ip_address):
    print(f"Monitoring requests for IP: {ip_address}")
    
    try:
        with open(LOG_FILE, "r") as log_file:
            # Move to the end of the file to start monitoring new entries
            log_file.seek(0, os.SEEK_END)
            
            request_count = 0
            start_time = datetime.now()
            
            while True:
                line = log_file.readline()
                
                if not line:  # No new line, wait for updates
                    time.sleep(0.1)
                    continue
                
                # Parse the log line
                try:
                    timestamp, source, dest, payload = map(str.strip, line.split(",", 3))
                except ValueError:
                    continue  # Skip malformed lines
                
                # Check if the destination matches the input IP address
                if dest == ip_address:
                    request_count += 1
                
                # Calculate time elapsed
                elapsed_time = (datetime.now() - start_time).total_seconds()
                
                if elapsed_time >= 1:  # Every second, report the count
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Requests per second: {request_count}")
                    request_count = 0
                    start_time = datetime.now()
    except FileNotFoundError:
        print(f"Log file '{LOG_FILE}' not found. Ensure the MQTT packet capturer is running.")
    except KeyboardInterrupt:
        print("\nStopping monitoring.")

if __name__ == "__main__":
    ip_address = input("Enter the IP address to monitor: ").strip()
    monitor_requests(ip_address)

