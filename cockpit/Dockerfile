FROM python:3.12

RUN apt update -y && apt upgrade -y
RUN apt install -y v4l-utils i2c-tools

COPY pilesos /app/pilesos
ADD requirements.txt /app

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

CMD exec uvicorn --host 0.0.0.0 pilesos.cockpit.server:fastapi_app --port 8000 --log-config pilesos/cockpit/uvicorn-logging.yml --reload
EXPOSE 8000
