FROM apache/airflow:2.3.2

RUN pip install --no-cache-dir beautifulsoup4==4.10.0
RUN pip install pafy==0.5.5
RUN pip install moviepy==1.0.3
RUN pip install youtube_dl==2020.12.31
RUN pip install markdown2