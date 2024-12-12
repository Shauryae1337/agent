import re
import csv

# Load malicious patterns from a single CSV file
def load_malicious_patterns(csv_file):
    malicious_patterns = {}

    try:
        with open(csv_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:
                    category = row[0].strip()
                    patterns = [pattern.strip() for pattern in row[1:] if pattern.strip()]
                    malicious_patterns[category] = patterns
    except FileNotFoundError:
        print(f"Error: {csv_file} not found.")
        return {}

    return malicious_patterns

# Define a function to check for potential malicious payloads
def find_malicious_categories(payload, malicious_patterns):
    matching_categories = []

    for category, patterns in malicious_patterns.items():
        for pattern in patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                matching_categories.append(category)
                break  # Avoid duplicate matches for the same category

    return matching_categories

# Parse the log file
def parse_mosquitto_logs(log_file, malicious_patterns):
    connections = {}
    results = []

    with open(log_file, 'r') as file:
        lines = file.readlines()

    for line in lines:
        # Check for new client connections
        if 'New client connected from' in line:
            ip_match = re.search(r'from ([\d\.]+):\d+', line)
            id_match = re.search(r'as (\S+)', line)

            if ip_match and id_match:
                ip = ip_match.group(1)
                unique_id = id_match.group(1)
                connections[unique_id] = {'ip': ip, 'malformed_count': 0, 'categories': set()}

        # Check for PUBLISH messages
        elif 'Received PUBLISH from' in line:
            id_match = re.search(r'from (\S+)', line)
            topic_match = re.search(r"'(.*?)'", line)

            if id_match and topic_match:
                unique_id = id_match.group(1)
                topic = topic_match.group(1)

                if unique_id in connections:
                    categories = find_malicious_categories(topic, malicious_patterns)
                    if categories:
                        connections[unique_id]['malformed_count'] += 1
                        connections[unique_id]['categories'].update(categories)

    # Convert connections dict to a list of results
    for unique_id, data in connections.items():
        categories_str = ', '.join(data['categories']) if data['categories'] else 'None'
        results.append(f"{data['ip']}, {unique_id}, {data['malformed_count']}, {categories_str}")

    return results

# Example usage
if __name__ == "__main__":
    log_file = "new.logs"  # Replace with the path to your log file
    csv_file = "malicious_patterns.csv"  # Replace with the path to your patterns CSV
    malicious_patterns = load_malicious_patterns(csv_file)

    if malicious_patterns:
        results = parse_mosquitto_logs(log_file, malicious_patterns)

        # Write the results to a text file
        output_file = "malformed_requests.txt"
        with open(output_file, 'w') as file:
            for result in results:
                file.write(result + '\n')

        print(f"Results saved to {output_file}")

