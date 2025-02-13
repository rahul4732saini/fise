FROM python:3.13.2-slim AS base

RUN apt-get update && apt-get install -y build-essential \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /home/fise

RUN python -m pip install --no-cache-dir --upgrade pip

COPY requirements/requirements.txt /tmp
COPY requirements/requirements-extra.txt /tmp

RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements-extra.txt

COPY ./fise .

CMD ["python", "./main.py"]