FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
RUN ln -s /usr/bin/python3 /usr/bin/python
COPY ./app /apps
WORKDIR /apps
RUN pip3 install -r requirements.txt
RUN python migrate.py db init;python migrate.py db migrate;python migrate.py db upgrade

ENTRYPOINT ["python"]
CMD ["run.py"]
