from fastapi import FastAPI, HTTPException
import pika
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Use environment variables provided by ConfigMap and Secret
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")

def publish_to_queue(name: str, meaning: str):
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=5
            )
        )
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        message = json.dumps({"name": name, "meaning": meaning})
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        connection.close()
        logger.info(f"Successfully published message to queue: {message}")
        return True
    except Exception as e:
        logger.error(f"Error publishing to queue: {str(e)}")
        return False

@app.get("/")
def read_root():
    return {"status": "healthy"}

@app.post("/lookup/{name}")
async def lookup_name(name: str):
    meaning = f"This is a simulated meaning for the name {name}"
    if publish_to_queue(name, meaning):
        return {
            "status": "success",
            "message": "Name meaning processed and published",
            "name": name,
            "meaning": meaning
        }
    raise HTTPException(status_code=500, detail="Failed to publish message to queue")
