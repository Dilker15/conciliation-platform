FROM public.ecr.aws/lambda/python:3.13

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY shared_layer/ ${LAMBDA_TASK_ROOT}/shared_layer/

COPY src/ ${LAMBDA_TASK_ROOT}/

CMD ["lambda_function.lambda_handler"]