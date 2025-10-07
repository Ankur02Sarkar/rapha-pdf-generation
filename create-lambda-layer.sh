#!/bin/bash

# Lambda Layer Creation Script for WeasyPrint Dependencies
# This script creates Lambda layers for system libraries required by WeasyPrint
# Author: Principal Backend Architect

set -e

# Configuration
LAYER_NAME="weasyprint-dependencies"
REGION="ap-south-1"
PYTHON_VERSION="3.11"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create Python dependencies layer
create_python_layer() {
    log_info "Creating Python dependencies layer..."
    
    # Create layer directory structure
    rm -rf layer-python
    mkdir -p layer-python/python/lib/python${PYTHON_VERSION}/site-packages
    
    # Install Python dependencies to layer
    pip3 install -r requirements-lambda.txt -t layer-python/python/lib/python${PYTHON_VERSION}/site-packages/
    
    # Create layer zip
    cd layer-python
    zip -r ../python-dependencies-layer.zip . -x "*.pyc" "*/__pycache__/*"
    cd ..
    
    # Publish layer
    PYTHON_LAYER_ARN=$(aws lambda publish-layer-version \
        --layer-name "${LAYER_NAME}-python" \
        --description "Python dependencies for WeasyPrint PDF generation" \
        --zip-file fileb://python-dependencies-layer.zip \
        --compatible-runtimes python${PYTHON_VERSION} \
        --query 'LayerVersionArn' --output text)
    
    log_success "Python layer created: $PYTHON_LAYER_ARN"
    echo "PYTHON_LAYER_ARN=$PYTHON_LAYER_ARN" >> layer-arns.env
}

# Create system libraries layer (requires Docker)
create_system_layer() {
    log_info "Creating system libraries layer..."
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        log_warning "Docker not found. Skipping system libraries layer."
        log_warning "WeasyPrint may not work properly without system dependencies."
        return
    fi
    
    # Create Dockerfile for building system dependencies
    cat > Dockerfile.layer << 'EOF'
FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies
RUN yum update -y && \
    yum install -y \
    cairo-devel \
    pango-devel \
    gdk-pixbuf2-devel \
    libffi-devel \
    shared-mime-info \
    && yum clean all

# Create layer structure
RUN mkdir -p /opt/lib /opt/bin

# Copy system libraries
RUN cp -r /usr/lib64/libcairo* /opt/lib/ && \
    cp -r /usr/lib64/libpango* /opt/lib/ && \
    cp -r /usr/lib64/libgdk* /opt/lib/ && \
    cp -r /usr/lib64/libffi* /opt/lib/ && \
    cp -r /usr/lib64/libpixman* /opt/lib/ && \
    cp -r /usr/lib64/libfontconfig* /opt/lib/ && \
    cp -r /usr/lib64/libfreetype* /opt/lib/ && \
    cp -r /usr/lib64/libharfbuzz* /opt/lib/ && \
    cp -r /usr/lib64/libglib* /opt/lib/ && \
    cp -r /usr/lib64/libgobject* /opt/lib/ && \
    cp -r /usr/lib64/libgio* /opt/lib/

# Copy font configuration
RUN cp -r /etc/fonts /opt/ && \
    cp -r /usr/share/fonts /opt/

CMD ["echo", "Layer built successfully"]
EOF

    # Build Docker image
    docker build -f Dockerfile.layer -t lambda-layer-builder .
    
    # Extract layer files
    rm -rf layer-system
    mkdir layer-system
    docker run --rm -v $(pwd)/layer-system:/output lambda-layer-builder sh -c "cp -r /opt/* /output/"
    
    # Create layer zip
    cd layer-system
    zip -r ../system-dependencies-layer.zip . -x "*.pyc" "*/__pycache__/*"
    cd ..
    
    # Publish layer
    SYSTEM_LAYER_ARN=$(aws lambda publish-layer-version \
        --layer-name "${LAYER_NAME}-system" \
        --description "System libraries for WeasyPrint PDF generation" \
        --zip-file fileb://system-dependencies-layer.zip \
        --compatible-runtimes python${PYTHON_VERSION} \
        --query 'LayerVersionArn' --output text)
    
    log_success "System layer created: $SYSTEM_LAYER_ARN"
    echo "SYSTEM_LAYER_ARN=$SYSTEM_LAYER_ARN" >> layer-arns.env
    
    # Clean up Docker resources
    docker rmi lambda-layer-builder 2>/dev/null || true
    rm -f Dockerfile.layer
}

# Create fonts layer
create_fonts_layer() {
    log_info "Creating fonts layer..."
    
    # Create fonts directory
    rm -rf layer-fonts
    mkdir -p layer-fonts/fonts
    
    # Download common fonts (you can add more fonts here)
    cat > layer-fonts/fonts/README.txt << 'EOF'
This directory contains fonts for PDF generation.
Add your custom fonts here if needed.

Common fonts are included in the system layer.
EOF

    # Create layer zip
    cd layer-fonts
    zip -r ../fonts-layer.zip . -x "*.pyc" "*/__pycache__/*"
    cd ..
    
    # Publish layer
    FONTS_LAYER_ARN=$(aws lambda publish-layer-version \
        --layer-name "${LAYER_NAME}-fonts" \
        --description "Fonts for WeasyPrint PDF generation" \
        --zip-file fileb://fonts-layer.zip \
        --compatible-runtimes python${PYTHON_VERSION} \
        --query 'LayerVersionArn' --output text)
    
    log_success "Fonts layer created: $FONTS_LAYER_ARN"
    echo "FONTS_LAYER_ARN=$FONTS_LAYER_ARN" >> layer-arns.env
}

# Update Lambda function with layers
update_lambda_with_layers() {
    log_info "Updating Lambda function with layers..."
    
    if [ ! -f layer-arns.env ]; then
        log_error "Layer ARNs file not found. Please create layers first."
        return 1
    fi
    
    source layer-arns.env
    
    LAYERS=""
    if [ ! -z "$PYTHON_LAYER_ARN" ]; then
        LAYERS="$PYTHON_LAYER_ARN"
    fi
    if [ ! -z "$SYSTEM_LAYER_ARN" ]; then
        LAYERS="$LAYERS,$SYSTEM_LAYER_ARN"
    fi
    if [ ! -z "$FONTS_LAYER_ARN" ]; then
        LAYERS="$LAYERS,$FONTS_LAYER_ARN"
    fi
    
    # Remove leading comma if present
    LAYERS=$(echo $LAYERS | sed 's/^,//')
    
    if [ ! -z "$LAYERS" ]; then
        aws lambda update-function-configuration \
            --function-name rapha-pdf-generation \
            --layers $LAYERS
        log_success "Lambda function updated with layers"
    else
        log_warning "No layers to attach"
    fi
}

# Clean up temporary files
cleanup() {
    log_info "Cleaning up temporary files..."
    rm -rf layer-python layer-system layer-fonts
    rm -f python-dependencies-layer.zip system-dependencies-layer.zip fonts-layer.zip
    log_success "Cleanup completed"
}

# Main function
main() {
    log_info "Creating Lambda layers for WeasyPrint dependencies..."
    
    # Initialize layer ARNs file
    rm -f layer-arns.env
    touch layer-arns.env
    
    create_python_layer
    create_system_layer
    create_fonts_layer
    
    log_success "All layers created successfully!"
    log_info "Layer ARNs saved to layer-arns.env"
    
    # Ask if user wants to update Lambda function
    read -p "Do you want to update the Lambda function with these layers? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        update_lambda_with_layers
    fi
    
    cleanup
}

# Run main function
main "$@"