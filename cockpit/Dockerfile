FROM python:3.12-slim

RUN mkdir /opt/cockpit
ADD requirements.txt /opt/cockpit

WORKDIR /opt/cockpit
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

WORKDIR /opt
VOLUME /opt/cockpit
CMD exec uvicorn --host 0.0.0.0 cockpit.server:fastapi_app --port 8000 --log-config cockpit/uvicorn-logging.yml --reload
EXPOSE 8000
