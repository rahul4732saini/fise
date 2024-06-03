FROM python:3.10-slim AS base

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential

WORKDIR /fise

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

COPY ./fise ./fise

CMD ["python", "./fise/main.py"]