FROM python:3.12-alpine

RUN mkdir "RestAPI"

WORKDIR /RestAPI

COPY req.txt /RestAPI

RUN pip install -r req.txt

COPY . /RestAPI

CMD gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:10000