FROM apache/airflow:latest

ADD requirements.txt /requirements.txt

RUN pip install --no-cache-dir -U pip setuptools wheel
RUN pip install --no-cache-dir -r /requirements.txt