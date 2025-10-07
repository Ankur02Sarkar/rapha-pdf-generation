# Use the official AWS Lambda Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.11

# Install minimal system dependencies for ReportLab
RUN yum update -y && \
    yum install -y \
        gcc \
        gcc-c++ \
        make \
        freetype-devel \
        libjpeg-devel \
        zlib-devel && \
    yum clean all

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}" -U --no-cache-dir

# Copy application code
COPY ./app ${LAMBDA_TASK_ROOT}/app
COPY main.py ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD [ "main.handler" ]