#!/bin/bash

# AWS Lambda Deployment Script for RaphaCure PDF Generation API
# This script automates the complete deployment process to AWS Lambda
# Author: Principal Backend Architect

set -e  # Exit on any error

# Configuration
FUNCTION_NAME="rapha-pdf-generation"
REGION="ap-south-1"  # Change to your preferred region
RUNTIME="python3.11"
TIMEOUT=30
MEMORY_SIZE=1024
ROLE_NAME="lambda-execution-role-${FUNCTION_NAME}"
POLICY_NAME="lambda-policy-${FUNCTION_NAME}"
API_NAME="rapha-pdf-api"
STAGE_NAME="prod"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create IAM role and policies
create_iam_resources() {
    log_info "Creating IAM role and policies..."
    
    # Trust policy for Lambda
    cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

    # Create IAM role
    if aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
        log_warning "IAM role $ROLE_NAME already exists"
    else
        aws iam create-role \
            --role-name $ROLE_NAME \
            --assume-role-policy-document file://trust-policy.json
        log_success "Created IAM role: $ROLE_NAME"
    fi
    
    # Attach basic Lambda execution policy
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
    # Custom policy for additional permissions
    cat > lambda-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
EOF

    # Create and attach custom policy
    if aws iam get-policy --policy-arn "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/$POLICY_NAME" &> /dev/null; then
        log_warning "Policy $POLICY_NAME already exists"
    else
        aws iam create-policy \
            --policy-name $POLICY_NAME \
            --policy-document file://lambda-policy.json
        
        aws iam attach-role-policy \
            --role-name $ROLE_NAME \
            --policy-arn "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/$POLICY_NAME"
        log_success "Created and attached custom policy"
    fi
    
    # Clean up temporary files
    rm -f trust-policy.json lambda-policy.json
    
    # Wait for role to be available
    log_info "Waiting for IAM role to be available..."
    sleep 10
}

# Package the application
package_application() {
    log_info "Packaging application for Lambda..."
    
    # Create deployment package directory
    rm -rf lambda-package
    mkdir lambda-package
    
    # Copy application files
    cp -r app/ lambda-package/
    cp lambda_handler.py lambda-package/
    cp main.py lambda-package/
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    pip3 install -r requirements-lambda.txt -t lambda-package/
    
    # Create deployment zip
    cd lambda-package
    zip -r ../lambda-deployment.zip . -x "*.pyc" "*/__pycache__/*"
    cd ..
    
    log_success "Application packaged successfully"
}

# Deploy Lambda function
deploy_lambda() {
    log_info "Deploying Lambda function..."
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
    
    # Check if function exists
    if aws lambda get-function --function-name $FUNCTION_NAME &> /dev/null; then
        log_info "Updating existing Lambda function..."
        aws lambda update-function-code \
            --function-name $FUNCTION_NAME \
            --zip-file fileb://lambda-deployment.zip
        
        aws lambda update-function-configuration \
            --function-name $FUNCTION_NAME \
            --timeout $TIMEOUT \
            --memory-size $MEMORY_SIZE \
            --environment Variables="{ENVIRONMENT=production,AWS_LAMBDA_FUNCTION_NAME=$FUNCTION_NAME}"
    else
        log_info "Creating new Lambda function..."
        aws lambda create-function \
            --function-name $FUNCTION_NAME \
            --runtime $RUNTIME \
            --role $ROLE_ARN \
            --handler lambda_handler.lambda_handler \
            --zip-file fileb://lambda-deployment.zip \
            --timeout $TIMEOUT \
            --memory-size $MEMORY_SIZE \
            --environment Variables="{ENVIRONMENT=production,AWS_LAMBDA_FUNCTION_NAME=$FUNCTION_NAME}"
    fi
    
    log_success "Lambda function deployed successfully"
}

# Create API Gateway
create_api_gateway() {
    log_info "Creating API Gateway..."
    
    # Create REST API
    API_ID=$(aws apigateway create-rest-api \
        --name $API_NAME \
        --description "API Gateway for RaphaCure PDF Generation" \
        --query 'id' --output text 2>/dev/null || \
        aws apigateway get-rest-apis \
        --query "items[?name=='$API_NAME'].id" --output text)
    
    if [ -z "$API_ID" ]; then
        log_error "Failed to create or find API Gateway"
        exit 1
    fi
    
    log_info "API Gateway ID: $API_ID"
    
    # Get root resource ID
    ROOT_RESOURCE_ID=$(aws apigateway get-resources \
        --rest-api-id $API_ID \
        --query 'items[?path==`/`].id' --output text)
    
    # Create proxy resource
    PROXY_RESOURCE_ID=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $ROOT_RESOURCE_ID \
        --path-part '{proxy+}' \
        --query 'id' --output text 2>/dev/null || \
        aws apigateway get-resources \
        --rest-api-id $API_ID \
        --query 'items[?pathPart==`{proxy+}`].id' --output text)
    
    # Create ANY method for proxy
    aws apigateway put-method \
        --rest-api-id $API_ID \
        --resource-id $PROXY_RESOURCE_ID \
        --http-method ANY \
        --authorization-type NONE 2>/dev/null || true
    
    # Set up Lambda integration
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    LAMBDA_URI="arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${FUNCTION_NAME}/invocations"
    
    aws apigateway put-integration \
        --rest-api-id $API_ID \
        --resource-id $PROXY_RESOURCE_ID \
        --http-method ANY \
        --type AWS_PROXY \
        --integration-http-method POST \
        --uri $LAMBDA_URI 2>/dev/null || true
    
    # Add Lambda permission for API Gateway
    aws lambda add-permission \
        --function-name $FUNCTION_NAME \
        --statement-id api-gateway-invoke \
        --action lambda:InvokeFunction \
        --principal apigateway.amazonaws.com \
        --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*/*" 2>/dev/null || true
    
    # Deploy API
    aws apigateway create-deployment \
        --rest-api-id $API_ID \
        --stage-name $STAGE_NAME
    
    # Get API endpoint
    API_ENDPOINT="https://${API_ID}.execute-api.${REGION}.amazonaws.com/${STAGE_NAME}"
    
    log_success "API Gateway created successfully"
    log_success "API Endpoint: $API_ENDPOINT"
}

# Clean up temporary files
cleanup() {
    log_info "Cleaning up temporary files..."
    rm -rf lambda-package
    rm -f lambda-deployment.zip
    log_success "Cleanup completed"
}

# Main deployment process
main() {
    log_info "Starting AWS Lambda deployment for $FUNCTION_NAME"
    
    check_prerequisites
    create_iam_resources
    package_application
    deploy_lambda
    create_api_gateway
    cleanup
    
    log_success "Deployment completed successfully!"
    log_info "Your API is available at: https://${API_ID}.execute-api.${REGION}.amazonaws.com/${STAGE_NAME}"
    log_info "Test endpoints:"
    log_info "  - Health: GET https://${API_ID}.execute-api.${REGION}.amazonaws.com/${STAGE_NAME}/api/v1/health"
    log_info "  - PDF Health: GET https://${API_ID}.execute-api.${REGION}.amazonaws.com/${STAGE_NAME}/api/v1/pdf/health"
    log_info "  - Generate Prescription: POST https://${API_ID}.execute-api.${REGION}.amazonaws.com/${STAGE_NAME}/api/v1/pdf/prescription"
}

# Run main function
main "$@"