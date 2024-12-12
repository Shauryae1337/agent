import re

# Path to your log file
log_file_path = 'new.logs'

# Lists to keep track of connections and disconnections
connections = {}
disconnections = set()

def parse_log_file(log_file_path):
    # Regular expressions for matching log entries
    connection_pattern = re.compile(r"(\d+): New connection from (\S+):(\d+)")
    connack_pattern = re.compile(r"(\d+): Sending CONNACK to (\S+) \((\d+), (\d+)\)")
    disconnect_pattern = re.compile(r"(\d+): Client (\S+) disconnected")

    # Open the log file for reading
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            # Match new connections
            connection_match = connection_pattern.search(line)
            if connection_match:
                timestamp, ip, port = connection_match.groups()
                connections[ip] = None  # Save the IP and prepare to link with a unique ID

            # Match CONNACK messages
            connack_match = connack_pattern.search(line)
            if connack_match:
                timestamp, unique_id, return_code_1, return_code_2 = connack_match.groups()
                for ip in connections:
                    # Link IP to the unique ID after successful CONNACK
                    connections[ip] = unique_id

            # Match disconnections
            disconnect_match = disconnect_pattern.search(line)
            if disconnect_match:
                timestamp, unique_id = disconnect_match.groups()
                disconnections.add(unique_id)

    # Return the list of currently connected IPs (excluding disconnected ones)
    currently_connected_ips = [ip for ip, unique_id in connections.items() if unique_id and unique_id not in disconnections]
    
    return currently_connected_ips

# Get the currently connected IPs
connected_ips = parse_log_file(log_file_path)

# Filter out '127.0.0.1' from the list of connected IPs
connected_ips = [ip for ip in connected_ips if ip != '127.0.0.1']

# Save the connected IPs to a file
with open('connections.txt', 'w') as output_file:
    if connected_ips:
        for ip in connected_ips:
            output_file.write(f"{ip}\n")
    else:
        output_file.write("No IPs currently connected.\n")

print("Output saved to 'connections.txt'.")

