FROM python:3.7
MAINTAINER Kevin McKenzie "kjtmckenzie@gmail.com"
COPY . /main
WORKDIR /main
RUN pip install -r requirements.txt
ENV GOOGLE_APPLICATION_CREDENTIALS kjtmckenzie-home-fs-e95cb6b832bf.json
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app

