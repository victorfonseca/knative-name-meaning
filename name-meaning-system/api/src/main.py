from fastapi import FastAPI, HTTPException
import pika
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_QUEUE = "name_meanings"

def publish_to_queue(name: str, meaning: str):
    try:
        credentials = pika.PlainCredentials('guest', 'guest')
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=5
            )
        )
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE)
        
        message = json.dumps({"name": name, "meaning": meaning})
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=message
        )
        connection.close()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
