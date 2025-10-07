# Use the official AWS Lambda Python base image for x86_64
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.10

# Install system dependencies for WeasyPrint with specific versions
RUN yum update -y && \
    yum install -y \
        cairo \
        cairo-devel \
        pango \
        pango-devel \
        gdk-pixbuf2 \
        gdk-pixbuf2-devel \
        libffi \
        libffi-devel \
        shared-mime-info \
        fontconfig \
        fontconfig-devel \
        freetype \
        freetype-devel \
        harfbuzz \
        harfbuzz-devel \
        fribidi \
        fribidi-devel \
        dejavu-sans-fonts \
        dejavu-serif-fonts \
        dejavu-sans-mono-fonts && \
    yum clean all

# Set environment variables for proper library loading
ENV LD_LIBRARY_PATH=/var/lang/lib:/lib64:/usr/lib64:/var/runtime:/var/runtime/lib:/var/task:/var/task/lib:/opt/lib
ENV FONTCONFIG_PATH=/etc/fonts
ENV FONTCONFIG_FILE=/etc/fonts/fonts.conf

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