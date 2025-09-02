# Builder stage
FROM python:3.8-slim AS builder
WORKDIR /app
COPY src/ src/
COPY setup.py .
COPY requirements.txt .
RUN pip install -r requirements.txt && pip install .

# Final stage
FROM python:3.8-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt && pip install .

RUN apt-get update && apt-get install -y curl && \
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

RUN useradd -m myuser
USER myuser

CMD ["openkrait", "--help"]
