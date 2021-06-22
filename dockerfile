FROM python:3.8.9-buster
WORKDIR /app/

RUN pip install boto3 && \
    pip install ring_doorbell

COPY . .
CMD [ "python", "./init.py" ]