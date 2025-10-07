# Use the official AWS Lambda Python 3.11 base image
FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies for WeasyPrint
RUN yum update -y && \
    yum install -y \
        gcc \
        gcc-c++ \
        make \
        cairo-devel \
        pango-devel \
        gdk-pixbuf2-devel \
        libffi-devel \
        fontconfig-devel \
        freetype-devel \
        harfbuzz-devel \
        fribidi-devel \
        dejavu-sans-fonts \
        dejavu-serif-fonts \
        dejavu-sans-mono-fonts && \
    yum clean all

# Copy system libraries for WeasyPrint
COPY lib/ ${LAMBDA_TASK_ROOT}/lib/

# Set environment variables for WeasyPrint
ENV FONTCONFIG_FILE=/etc/fonts/fonts.conf
ENV LD_LIBRARY_PATH=${LAMBDA_TASK_ROOT}/lib:${LD_LIBRARY_PATH}

# Copy requirements and install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ ${LAMBDA_TASK_ROOT}/app/

# Set the CMD to your handler
CMD ["app.handler.lambda_handler"]