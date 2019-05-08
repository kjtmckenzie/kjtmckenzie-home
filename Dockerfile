FROM python:3.7
LABEL maintainer="kjtmckenzie@gmail.com"
COPY . /main
WORKDIR /main
RUN pip install -r requirements.txt
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app

