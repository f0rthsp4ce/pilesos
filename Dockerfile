FROM python:3.12-slim

COPY pilesos /app/pilesos
ADD requirements.txt /app

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

CMD exec uvicorn --host 0.0.0.0 pilesos.cockpit.server:fastapi_app --port 8000 --log-config pilesos/cockpit/uvicorn-logging.yml --reload
EXPOSE 8000
