from fastapi import FastAPI, HTTPException
import httpx
import pika
import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# RabbitMQ connection parameters
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-service.default.svc.cluster.local")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_QUEUE = "name_meanings"

def publish_to_queue(name: str, meaning: str):
    try:
        logger.info(f"Attempting to connect to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
        credentials = pika.PlainCredentials('guest', 'guest')
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
        logger.info(f"Connected to RabbitMQ successfully")
        
        channel.queue_declare(queue=RABBITMQ_QUEUE)
        
        message = json.dumps({"name": name, "meaning": meaning})
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=message
        )
        connection.close()
        logger.info(f"Message published successfully")
        return True
    except Exception as e:
        logger.error(f"Error publishing to queue: {str(e)}")
        return False

@app.get("/")
def read_root():
    return {"status": "healthy"}

@app.post("/lookup/{name}")
async def lookup_name(name: str):
    try:
        # Simulated name meaning lookup
        meaning = f"This is a simulated meaning for the name {name}"
        
        # Publish to RabbitMQ
        if publish_to_queue(name, meaning):
            return {
                "status": "success",
                "message": "Name meaning published to queue",
                "name": name,
                "meaning": meaning
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to publish to queue")
            
    except Exception as e:
        logger.error(f"Error in lookup_name: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
