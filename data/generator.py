import json
import time
import random
from faker import Faker
from kafka import KafkaProducer

fake = Faker()

# Configure the Kafka Producer
# We use localhost:9092 because we exposed this port in docker-compose.yml
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    api_version=(3, 7, 0)
)

TOPIC_NAME = 'network-traffic'

def generate_netflow_log():
    """Generates a highly realistic simulated NetFlow log with overlapping features."""
    is_attack = random.random() < 0.05 
    
    # Common ports that BOTH normal users and attackers use
    common_ports = [80, 443, 22, 21, 8080]
    
    if is_attack:
        # Attackers target common ports and send large bursts of data
        dest_port = random.choice(common_ports)
        bytes_sent = random.randint(3000, 15000) 
    else:
        # Normal users use common ports half the time, and random ports the other half
        dest_port = random.choice(common_ports) if random.random() < 0.5 else random.randint(1024, 65535)
        # Normal users usually send smaller packets, but occasionally download larger files
        bytes_sent = random.randint(64, 6000)

    log = {
        "timestamp": time.time(),
        "source_ip": fake.ipv4(),
        "dest_ip": "10.0.0.50" if is_attack else fake.ipv4(),
        "source_port": random.randint(1024, 65535),
        "dest_port": dest_port,
        "bytes": bytes_sent,
        "is_attack": int(is_attack)
    }
    return log

print(f"Starting simulated NetFlow generator. Sending to topic: {TOPIC_NAME}...")

try:
    while True:
        log_data = generate_netflow_log()
        producer.send(TOPIC_NAME, value=log_data)
        
        # Print every 100th message to the console so you can see it working
        if random.random() < 0.01:
            print(f"Sent: {log_data}")
            
        # Sleep briefly to simulate high throughput without crashing your PC
        # We can increase this later to hit your 800-1200 msg/sec goal
        time.sleep(0.01) 
        
except KeyboardInterrupt:
    print("\nStopping data generator...")
finally:
    producer.flush()
    producer.close()
