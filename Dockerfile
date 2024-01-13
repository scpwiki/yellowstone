FROM python:3.11-alpine

COPY ./ /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "-m", "yellowstone", "/app/config.toml"]
