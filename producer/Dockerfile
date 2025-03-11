FROM python:3.12-alpine3.21

WORKDIR /app

COPY setup.py .
COPY common/ common/
COPY producer/ producer/

RUN pip install . --no-cache-dir -r producer/requirements.txt

ENTRYPOINT [ "python3", "-m", "producer.main" ]
