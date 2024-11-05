import pika
import json
import os
import time
import sys

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"Processing message: {json.dumps(message, indent=2)}")
        sys.stdout.flush()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Message acknowledged successfully")
        sys.stdout.flush()
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        sys.stdout.flush()

def main():
    print("Consumer starting up...")
    sys.stdout.flush()
    
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq',
                    port=5672,
                    credentials=pika.PlainCredentials('guest', 'guest'),
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
            
            channel = connection.channel()
            channel.queue_declare(queue='name_meanings')
            channel.basic_qos(prefetch_count=1)
            
            print("Connected to RabbitMQ, waiting for messages...")
            sys.stdout.flush()
            
            channel.basic_consume(
                queue='name_meanings',
                on_message_callback=callback
            )
            
            channel.start_consuming()
            
        except Exception as e:
            print(f"Connection error: {str(e)}")
            sys.stdout.flush()
            time.sleep(5)

if __name__ == '__main__':
    main()
