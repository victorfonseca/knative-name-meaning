FROM python:3.9-slim

WORKDIR /app

# Install dependencies first to leverage Docker's caching mechanism
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main code into the container
COPY src/ .

CMD ["python", "main.py"]
