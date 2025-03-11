FROM python:3.12-alpine3.21

WORKDIR /app

COPY setup.py .
COPY common/ common/
COPY consumer/ consumer/

RUN pip install . --no-cache-dir -r consumer/requirements.txt

ENTRYPOINT [ "python3", "-m", "consumer.main" ]
