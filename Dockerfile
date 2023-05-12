FROM python:3.10-slim

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY TelegramBot.py .

ENV BOT_TOKEN="enter-your-bot-token-here"

CMD ["python", "TelegramBot.py"]