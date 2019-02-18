FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY ./app /apps
WORKDIR /apps
RUN pip install -r requirements.txt
RUN python migrate.py db init;python migrate.py db migrate;python migrate.py db upgrade

ENTRYPOINT ["python"]
CMD ["run.py"]