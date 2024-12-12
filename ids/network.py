from scapy.all import sniff, IP, TCP
import os
from datetime import datetime

LOG_FILE = "mqtt_logs.txt"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
PORT = 1833

def packet_handler(packet):
    if IP in packet and TCP in packet and packet[TCP].dport == PORT:
        log_packet(packet)

def log_packet(packet):
    # Extracting required information
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source = packet[IP].src
    dest = packet[IP].dst
    payload = bytes(packet[TCP].payload).decode(errors="replace")  # Decode with error handling

    # Format the log entry
    log_entry = f"{timestamp}, {source}, {dest}, {payload}\n"
    
    # Write to file
    with open(LOG_FILE, "a") as file:
        file.write(log_entry)
    manage_file_size()

def manage_file_size():
    if os.path.getsize(LOG_FILE) > MAX_FILE_SIZE:
        with open(LOG_FILE, "r+") as file:
            lines = file.readlines()
            file.seek(0)
            file.writelines(lines[len(lines)//2:])  # Keep the latter half
            file.truncate()

if __name__ == "__main__":
    print("Starting MQTT packet capturer...")
    sniff(prn=packet_handler, filter=f"tcp port {PORT}", store=0)

