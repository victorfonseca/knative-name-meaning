import pika
import json
import os
import time
import logging
import signal
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "name_meanings")

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        logger.info(f"Received message: {json.dumps(message, indent=2)}")
        logger.info(f"Processing message for name: {message.get('name')}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Message acknowledged successfully")
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
    )
    return connection

def signal_handler(signal, frame):
    logger.info("Signal received, shutting down gracefully...")
    sys.exit(0)

def main():
    logger.info("Consumer starting up...")

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    retry_delay = 5

    while True:
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
            channel.basic_qos(prefetch_count=1)

            logger.info(f"Connected to RabbitMQ host: {RABBITMQ_HOST}, queue: {RABBITMQ_QUEUE}")
            logger.info("Waiting for messages...")

            channel.basic_consume(
                queue=RABBITMQ_QUEUE,
                on_message_callback=callback
            )

            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Connection error: {str(e)}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)  # Exponential backoff with a maximum delay
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)

if __name__ == '__main__':
    main()

