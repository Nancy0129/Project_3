 FROM python:3.7-slim

RUN mkdir /viz
COPY . /viz
WORKDIR /viz

RUN pip install -r requirements.txt

ENTRYPOINT ["python","app.py","--port","5101","--host=0.0.0.0"]
