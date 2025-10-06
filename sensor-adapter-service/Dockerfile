FROM python:3.11-slim

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code
COPY .env .

ENV PYTHONPATH=/code

EXPOSE ${APP_PORT}

CMD uvicorn app.main:app --host ${APP_HOST} --port ${APP_PORT}