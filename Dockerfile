FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY chat_with_human ./chat_with_human
COPY config ./config

# Create secrets directory (will be mounted as volume)
RUN mkdir -p /secrets

EXPOSE 8000

CMD ["adk", "api_server", "--host", "0.0.0.0", "--port", "8000"]