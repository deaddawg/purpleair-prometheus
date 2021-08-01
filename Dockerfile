FROM python:3.8

WORKDIR /code
COPY requirements.txt .

RUN pip install -r requirements.txt

ENV SENSORS=""
ENV EXTRA_OPTS=""
ENV PORT="7884"

COPY src/ .
CMD python purple-prom.py -p $PORT -s $SENSORS $EXTRA_OPTS
