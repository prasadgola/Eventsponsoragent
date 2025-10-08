FROM python:3.11-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY index.html .
COPY server.py .

EXPOSE 8080

ENV ADK_SERVER_URL=""

CMD ["python", "server.py"]