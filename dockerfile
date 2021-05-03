FROM python:3.8.9-buster
WORKDIR /app/

ADD src/init.py ./
CMD [ "python", "./init.py" ]