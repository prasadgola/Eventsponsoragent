FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./chat_with_human/requirements.txt
RUN pip install --no-cache-dir -r ./chat_with_human/requirements.txt


COPY . ./chat_with_human/

EXPOSE 8000

CMD ["python", "chat_with_human/main.py"]