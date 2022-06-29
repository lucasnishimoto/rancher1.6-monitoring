FROM python:alpine 

WORKDIR /app

RUN pip install schedule mysql-connector-python influxdb

COPY *.py /app/

CMD python3 main.py 
