import paho.mqtt.client as mqtt
import requests
import argparse
import platform
from scapy.all import sniff, IP, TCP, conf
import os

# MQTT broker settings
broker_address = "127.0.0.1"  # Replace with the actual broker IP address
broker_port = 1883
topic = "#"

# Broker API settings (for Mode 2)
broker_api_url = f"http://{broker_address}:5000/logs"

# Mode 1: MQTT message listener callback
def on_message(client, userdata, msg):
    print(f"Message received on topic '{msg.topic}': {msg.payload.decode()}")

# Mode 1: Listen to MQTT messages
def mode_1_listen():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker_address, broker_port)
    client.subscribe(topic)
    print("Listening for MQTT messages...")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Stopping listener...")
        client.disconnect()

# Mode 2: Fetch broker logs using the API
def mode_2_fetch_logs():
    try:
        response = requests.get(broker_api_url)
        if response.status_code == 200:
            logs = response.json().get("logs", [])
            if logs:
                print("\n".join(logs))
            else:
                print("No logs available.")
        else:
            print(f"Error fetching logs: {response.json().get('message')}")
    except Exception as e:
        print(f"Failed to fetch logs: {e}")

# Mode 3: Scapy Packet Capture for MQTT traffic
def packet_callback(packet):
    # Check if it's a TCP packet with port 1883 (MQTT default port)
    if packet.haslayer(TCP):
        if packet[TCP].dport == 1883 or packet[TCP].sport == 1883:
            source_ip = packet[IP].src
            dest_ip = packet[IP].dst
            source_port = packet[TCP].sport
            dest_port = packet[TCP].dport
            print(f"Source IP: {source_ip}, Source Port: {source_port} --> "
                  f"Destination IP: {dest_ip}, Destination Port: {dest_port}")

# Mode 3: Capture MQTT traffic using Scapy
def mode_3_capture_mqtt():
    print("Starting packet capture... Press Ctrl+C to stop.")
    
    # Detect platform and set the correct network interface
    if platform.system() == "Windows":
        # On Windows, the interface is typically named "Ethernet" or "Wi-Fi"
        iface = "Wi-Fi"  # Change this if necessary
    else:
        # On Linux or macOS, we use the default interface or explicitly set "lo" for loopback
        iface = conf.iface  # Automatically chooses the correct interface on Linux/macOS
        
        # If on Linux, we can explicitly check for the loopback interface `lo`
        if platform.system() == "Linux":
            # Add loopback interface to the capture list if needed
            iface = "lo"  # Explicitly using loopback interface for Linux
            print(f"Capturing on loopback interface: {iface}")
    
    print(f"Using interface: {iface}")
    
    sniff(prn=packet_callback, store=0, filter="tcp", iface=iface)

# Main entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MQTT Activity Listener")
    parser.add_argument(
        "mode",
        choices=["1", "2", "3"],
        help="Mode 1: Listen to MQTT messages, Mode 2: Fetch broker logs, Mode 3: Capture MQTT traffic"
    )
    args = parser.parse_args()

    # Display a message to indicate the selected mode
    print(f"Running in Mode {args.mode}")

    if args.mode == "1":
        # Mode 1: Listen to MQTT messages
        mode_1_listen()
    elif args.mode == "2":
        # Mode 2: Fetch broker logs
        mode_2_fetch_logs()
    elif args.mode == "3":
        # Mode 3: Capture MQTT traffic using Scapy
        mode_3_capture_mqtt()

