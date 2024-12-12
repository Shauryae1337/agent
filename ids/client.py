import paho.mqtt.client as mqtt
import time

# Define the MQTT settings
broker_address = "54.209.251.197"
broker_port = 1833
topic = "test/topic"
message = "Hello MQTT!"

# Create a new MQTT client instance
client = mqtt.Client()

# Connect to the broker
client.connect(broker_address, broker_port)

# Send messages in a loop
try:
    while True:
        # Publish a message
        client.publish(topic, message)
        print(f"Message '{message}' sent to topic '{topic}'")
        
        # Wait for 2 seconds before sending the next message
        time.sleep(2)
except KeyboardInterrupt:
    print("Stopped sending messages.")

# Disconnect from the broker
client.disconnect()
print("Disconnected from the broker.")

