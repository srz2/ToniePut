FROM python:3.13.0-slim-bullseye
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Manually install ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg
COPY src/ /app
ENV PORT=8000
EXPOSE 8000
CMD ["gunicorn", "--certfile", "/app/certs/cert.pem", "--keyfile", "/app/certs/key.pem", "-b", "0.0.0.0", "main:app"]
