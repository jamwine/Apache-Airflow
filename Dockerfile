FROM apache/airflow:2.3.4-python3.10

USER root
RUN apt-get update && apt-get install -y git
WORKDIR /app/

USER airflow
# Install requirements
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -U pip setuptools wheel
RUN pip install -r /requirements.txt

# Copy script for health check
COPY ./health_check.py ./health_check.py