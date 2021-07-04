FROM amazon/aws-lambda-python
WORKDIR /app/

COPY src/init.py ${LAMBDA_TASK_ROOT}

RUN pip install boto3 && \
    pip install ring_doorbell

CMD [ "init.lambda_handler" ]