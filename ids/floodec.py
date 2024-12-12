import re
from collections import defaultdict
from datetime import datetime

def parse_mqtt_log(file_path):
    ip_id_pairs = []
    publish_count = defaultdict(int)
    connection_times = {}
    topic_publish_times = defaultdict(list)

    # Regex patterns
    connection_pattern = re.compile(r"(\d+): New connection from (\d+\.\d+\.\d+\.\d+):(\d+) on port (\d+).")
    client_pattern = re.compile(r"(\d+): New client connected from (\d+\.\d+\.\d+\.\d+):\d+ as (\S+)")
    publish_pattern = re.compile(r"(\d+): Received PUBLISH from (\S+) \((\S+), (\S+), (\S+), (\S+), '(\S+)',")
    disconnect_pattern = re.compile(r"(\d+): Received DISCONNECT from (\S+)")

    # Open output file
    with open("flood_data.txt", "w") as output_file:
        with open(file_path, 'r') as file:
            for line in file:
                # Parse new connection
                match = connection_pattern.search(line)
                if match:
                    timestamp, ip, _, _ = match.groups()
                    ip_id_pairs.append((ip, None))
                    continue

                # Parse client connection
                match = client_pattern.search(line)
                if match:
                    timestamp, ip, client_id = match.groups()
                    ip_id_pairs[-1] = (ip, client_id)  # Update the most recent entry with client ID
                    connection_times[client_id] = int(timestamp)  # Record connection time
                    continue

                # Parse PUBLISH events
                match = publish_pattern.search(line)
                if match:
                    timestamp, client_id, _, _, _, _, topic = match.groups()
                    timestamp = int(timestamp)
                    publish_count[(client_id, topic)] += 1
                    topic_publish_times[client_id].append(timestamp)
                    continue

                # Parse DISCONNECT events
                match = disconnect_pattern.search(line)
                if match:
                    timestamp, client_id = match.groups()
                    timestamp = int(timestamp)
                    if client_id in connection_times:
                        connection_duration = timestamp - connection_times[client_id]
                        # Calculate topics per second
                        total_topics = len([key for key in publish_count.keys() if key[0] == client_id])
                        if connection_duration > 0:
                            topics_per_second = total_topics / connection_duration
                        else:
                            topics_per_second = 0
                        output = (f"IP: {ip_id_pairs[-1][0]}, ID: {client_id}, Topics Published: {total_topics}, "
                                  f"Topics/Second: {topics_per_second:.2f}\n")
                        output_file.write(output)
                        # Clean up for next client
                        del connection_times[client_id]

if __name__ == "__main__":
    log_file_path = 'new.logs'
    parse_mqtt_log(log_file_path)
