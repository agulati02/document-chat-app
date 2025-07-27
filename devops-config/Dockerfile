FROM ubuntu:22.04

# Install Python, pip, and curl
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY src/main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]