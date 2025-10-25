FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app
USER app

CMD ["sh", "-c", "python3 -m http.server ${PORT} & exec python3 bot_main.py"]
