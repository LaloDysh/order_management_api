FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 1995

CMD ["gunicorn", "--bind", "0.0.0.0:1995", "run:app"]