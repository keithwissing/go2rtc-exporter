import requests
from prometheus_client import start_http_server, Gauge
import json
import time

# Get go2rtc path from argument
import sys
go2rtc_path = sys.argv[1]

from flask import Flask
from prometheus_client import generate_latest, Counter
app = Flask(__name__)
request_counter = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])

# Initialize Prometheus metrics
recv_bytes_gauge = Gauge("go2rtc_stream_recv_bytes", "Received bytes by producers", ["camera", "user_agent", "ip_address", "media_type", "connection_type"])
send_bytes_gauge = Gauge("go2rtc_stream_sent_bytes", "Sent bytes to consumers", ["camera", "user_agent", "ip_address", "media_type", "connection_type"])
num_consumers_gauge = Gauge("go2rtc_stream_num_consumers", "Number of consumers", ["camera"])
num_producers_gauge = Gauge("go2rtc_stream_num_producers", "Number of producers", ["camera"])

# Function to parse the JSON and update Prometheus metrics
def update_metrics(json_data):
    if json_data:
        for camera, data in json_data.items():
            num_consumers = len(data["consumers"]) if data["consumers"] else 0
            num_producers = len(data["producers"]) if data["producers"] else 0
            num_consumers_gauge.labels(camera).set(num_consumers)
            num_producers_gauge.labels(camera).set(num_producers)
            if data["producers"]:
                for producer in data["producers"]:
                    if "recv" in producer:
                        recv_bytes_gauge.labels(
                            camera=camera,
                            user_agent=producer.get("user_agent", ""),
                            ip_address=producer.get("remote_addr", ""),
                            media_type=producer.get("medias", ["Unknown"])[0],
                            connection_type=producer.get("type", ""),
                        ).set(producer["recv"])
            if data["consumers"]:
                for consumer in data["consumers"]:
                    if "send" in consumer:
                        send_bytes_gauge.labels(
                            camera=camera,
                            user_agent=consumer.get("user_agent", ""),
                            ip_address=consumer.get("remote_addr", ""),
                            media_type=consumer.get("medias", ["Unknown"])[0],
                            connection_type=consumer.get("type", ""),
                        ).set(consumer["send"])

# Function to fetch data from API
def fetch_data_from_api():
    try:
        response = requests.get(go2rtc_path)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch data from API. Status code:", response.status_code)
            return None
    except Exception as e:
        print("Error fetching data from API:", e)
        return None

# if __name__ == '__main__':
#     # Start the Prometheus server on port 8000
#     start_http_server(8000)

#     while True:
#         # Fetch data from API
#         api_data = fetch_data_from_api()
#         # Update Prometheus metrics
#         update_metrics(api_data)
#         # Sleep for 30 seconds
#         time.sleep(30)

@app.route('/metrics')
def metrics():
    # Increment the counter for the metrics endpoint
    request_counter.labels('GET', '/metrics').inc()
    # Fetch data from API
    api_data = fetch_data_from_api()
    # Update Prometheus metrics
    update_metrics(api_data)
    # Return the metrics
    return generate_latest()

if __name__ == '__main__':
    # Start the Flask app on port 1985
    app.run(port=1985, host="0.0.0.0")