FROM python:3.11-slim

WORKDIR /app

# Copy the HTML file and the combined server
COPY index.html .
COPY combined_server.py .

# Expose the port that Cloud Run will use
EXPOSE 8080

# The ADK_SERVER_URL will be set as environment variable during deployment
# This will point to the deployed backend container URL
ENV ADK_SERVER_URL=""

# Run the combined server
CMD ["python", "combined_server.py"]