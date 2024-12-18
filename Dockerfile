FROM python:3.9-slim

RUN apt-get update

ENV PYTHONBUFFERED=True
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install "psycopg[binary]"

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", "0.0.0.0:8080", "app:app", "--timeout=2", "--log-level=debug", "--access-logfile=-", "--error-logfile=-"]