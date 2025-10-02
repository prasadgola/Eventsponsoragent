FROM python:3.11-slim

WORKDIR /app

COPY index.html .
COPY server.py .

EXPOSE 8080

ENV ADK_SERVER_URL=""

CMD ["python", "server.py"]