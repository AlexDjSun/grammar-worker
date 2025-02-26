import pika
import json

mq_host = "localhost"  # Change if your RabbitMQ is running elsewhere
mq_queue = "grammar.et"  # Adjust this based on your queue setup

connection = pika.BlockingConnection(pika.ConnectionParameters(host=mq_host))
channel = connection.channel()

request_data = {
    "text": "Loodan, et meil kõik kätte sai."  # Sample incorrect sentence
}

channel.basic_publish(
    exchange="grammar",
    routing_key=mq_queue,
    body=json.dumps(request_data),
    properties=pika.BasicProperties(reply_to="response_queue")
)

print("Sent test request!")
connection.close()

