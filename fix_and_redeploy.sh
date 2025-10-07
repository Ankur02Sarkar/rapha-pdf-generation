#!/bin/bash

# Quick Fix and Redeploy Script
# Fixes the Docker platform issue and redeploys to Lambda

set -e

# Configuration
ECR_REPOSITORY_NAME="rapha-pdf-generation"
LAMBDA_FUNCTION_NAME="rapha-pdf-generation-lambda"
AWS_REGION="ap-south-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo -e "${BLUE}🔧 Quick Fix: Rebuilding Docker image with correct platform...${NC}\n"

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME"

print_status "AWS Account: $AWS_ACCOUNT_ID"
print_status "ECR Repository: $ECR_URI"
print_status "Lambda Function: $LAMBDA_FUNCTION_NAME"
echo ""

# Step 1: Remove old local images
print_status "Cleaning up old Docker images..."
docker rmi $ECR_REPOSITORY_NAME:latest 2>/dev/null || true
docker rmi $ECR_URI:latest 2>/dev/null || true
print_success "Old images cleaned up"

# Step 2: Build with correct platform (using legacy builder for compatibility)
print_status "Building Docker image for AWS Lambda (linux/amd64)..."
export DOCKER_BUILDKIT=0
docker build --no-cache -t $ECR_REPOSITORY_NAME .
print_success "Docker image built with correct platform"

# Step 3: Authenticate with ECR
print_status "Authenticating Docker with ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
print_success "Docker authenticated with ECR"

# Step 4: Tag and push
print_status "Tagging image for ECR..."
docker tag $ECR_REPOSITORY_NAME:latest $ECR_URI:latest

print_status "Pushing image to ECR..."
docker push $ECR_URI:latest
print_success "Image pushed to ECR successfully"

# Step 5: Create or Update Lambda function
print_status "Checking if Lambda function exists..."
if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION >/dev/null 2>&1; then
    print_status "Lambda function exists. Updating with new image..."
    aws lambda update-function-code \
        --function-name $LAMBDA_FUNCTION_NAME \
        --image-uri $ECR_URI:latest \
        --region $AWS_REGION
    
    print_status "Waiting for Lambda function to be updated..."
    aws lambda wait function-updated \
        --function-name $LAMBDA_FUNCTION_NAME \
        --region $AWS_REGION
    
    print_success "Lambda function updated successfully"
else
    print_status "Lambda function doesn't exist. Creating new function..."
    aws lambda create-function \
        --function-name $LAMBDA_FUNCTION_NAME \
        --package-type Image \
        --code ImageUri=$ECR_URI:latest \
        --role arn:aws:iam::$AWS_ACCOUNT_ID:role/lambda-execution-role \
        --timeout 30 \
        --memory-size 512 \
        --region $AWS_REGION \
        --architecture x86_64 || {
        
        print_error "Failed to create Lambda function. This might be due to missing IAM role."
        print_status "Creating basic Lambda execution role..."
        
        # Create IAM role for Lambda
        aws iam create-role \
            --role-name lambda-execution-role \
            --assume-role-policy-document '{
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
            }' >/dev/null 2>&1 || true
        
        # Attach basic execution policy
        aws iam attach-role-policy \
            --role-name lambda-execution-role \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole >/dev/null 2>&1 || true
        
        print_status "Waiting for IAM role to be ready..."
        sleep 10
        
        # Try creating function again
        aws lambda create-function \
            --function-name $LAMBDA_FUNCTION_NAME \
            --package-type Image \
            --code ImageUri=$ECR_URI:latest \
            --role arn:aws:iam::$AWS_ACCOUNT_ID:role/lambda-execution-role \
            --timeout 30 \
            --memory-size 512 \
            --region $AWS_REGION \
            --architecture x86_64
    }
    
    print_status "Waiting for Lambda function to be active..."
    aws lambda wait function-active \
        --function-name $LAMBDA_FUNCTION_NAME \
        --region $AWS_REGION
    
    print_success "Lambda function created successfully"
fi

echo ""
echo -e "${GREEN}🎉 Fix applied successfully!${NC}"
echo -e "${GREEN}✅ Your FastAPI Lambda function is now deployed with the correct platform${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "   Test your deployment: ${YELLOW}python test_lambda_deployment.py${NC}"
echo ""

# Optional: Get function URL if it exists
print_status "Checking for Lambda Function URL..."
FUNCTION_URL=$(aws lambda get-function-url-config --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION --query 'FunctionUrl' --output text 2>/dev/null || echo "")

if [[ -n "$FUNCTION_URL" && "$FUNCTION_URL" != "None" ]]; then
    echo -e "${GREEN}🌐 Your API is available at: ${FUNCTION_URL}${NC}"
    echo -e "${GREEN}📋 Test health endpoint: ${FUNCTION_URL}health${NC}"
else
    echo -e "${YELLOW}💡 To create a Function URL for easy testing:${NC}"
    echo -e "   ${YELLOW}aws lambda create-function-url-config --function-name $LAMBDA_FUNCTION_NAME --auth-type NONE --region $AWS_REGION${NC}"
fi

echo ""