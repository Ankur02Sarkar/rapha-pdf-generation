#!/bin/bash

# FastAPI to AWS Lambda Deployment Script
# This script follows the deployment process outlined in the Searce blog post
# https://blog.searce.com/fastapi-container-app-deployment-using-aws-lambda-and-api-gateway-6721904531d0

set -e  # Exit on any error

# Configuration - Update these values for your AWS environment
AWS_REGION="ap-south-1"  # Change to your preferred region
ECR_REPOSITORY_NAME="rapha-pdf-generation"
LAMBDA_FUNCTION_NAME="rapha-pdf-generation-lambda"
AWS_ACCOUNT_ID=""  # Will be auto-detected if not set

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if AWS CLI is configured
check_aws_cli() {
    print_status "Checking AWS CLI configuration..."
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "AWS CLI is configured"
}

# Function to get AWS Account ID
get_account_id() {
    if [ -z "$AWS_ACCOUNT_ID" ]; then
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        print_status "Auto-detected AWS Account ID: $AWS_ACCOUNT_ID"
    fi
}

# Function to create ECR repository if it doesn't exist
create_ecr_repository() {
    print_status "Checking if ECR repository exists..."
    
    if aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION &> /dev/null; then
        print_success "ECR repository '$ECR_REPOSITORY_NAME' already exists"
    else
        print_status "Creating ECR repository '$ECR_REPOSITORY_NAME'..."
        aws ecr create-repository \
            --repository-name $ECR_REPOSITORY_NAME \
            --region $AWS_REGION \
            --image-scanning-configuration scanOnPush=true
        print_success "ECR repository created successfully"
    fi
}

# Function to authenticate Docker with ECR
authenticate_docker() {
    print_status "Authenticating Docker with ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    print_success "Docker authenticated with ECR"
}

# Function to build Docker image
build_docker_image() {
    print_status "Building Docker image for AWS Lambda (linux/amd64)..."
    docker build --platform linux/amd64 -t $ECR_REPOSITORY_NAME .
    print_success "Docker image built successfully"
}

# Function to tag and push image to ECR
push_to_ecr() {
    ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME"
    
    print_status "Tagging image for ECR..."
    docker tag $ECR_REPOSITORY_NAME:latest $ECR_URI:latest
    
    print_status "Pushing image to ECR..."
    docker push $ECR_URI:latest
    print_success "Image pushed to ECR successfully"
    
    echo "ECR Image URI: $ECR_URI:latest"
}

# Function to create or update Lambda function
deploy_lambda() {
    ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:latest"
    
    print_status "Checking if Lambda function exists..."
    
    if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION &> /dev/null; then
        print_status "Updating existing Lambda function..."
        aws lambda update-function-code \
            --function-name $LAMBDA_FUNCTION_NAME \
            --image-uri $ECR_URI \
            --region $AWS_REGION
        print_success "Lambda function updated successfully"
    else
        print_status "Creating new Lambda function..."
        
        # Create execution role if it doesn't exist
        ROLE_NAME="lambda-execution-role-$ECR_REPOSITORY_NAME"
        ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text 2>/dev/null || echo "")
        
        if [ -z "$ROLE_ARN" ]; then
            print_status "Creating Lambda execution role..."
            
            # Create trust policy
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
            
            aws iam create-role \
                --role-name $ROLE_NAME \
                --assume-role-policy-document file://trust-policy.json
            
            aws iam attach-role-policy \
                --role-name $ROLE_NAME \
                --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
            
            # Wait for role to be available
            sleep 10
            
            ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
            rm trust-policy.json
            print_success "Lambda execution role created"
        fi
        
        aws lambda create-function \
            --function-name $LAMBDA_FUNCTION_NAME \
            --package-type Image \
            --code ImageUri=$ECR_URI \
            --role $ROLE_ARN \
            --timeout 30 \
            --memory-size 512 \
            --region $AWS_REGION
        
        print_success "Lambda function created successfully"
    fi
}

# Function to create API Gateway (optional)
create_api_gateway() {
    print_status "Creating API Gateway integration..."
    print_warning "API Gateway creation is complex and typically done through AWS Console or CloudFormation."
    print_warning "Please create API Gateway manually or use the provided CloudFormation template."
    
    # Get Lambda function ARN for reference
    LAMBDA_ARN=$(aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION --query 'Configuration.FunctionArn' --output text)
    echo "Lambda Function ARN: $LAMBDA_ARN"
    
    print_status "You can also create a Lambda Function URL for quick testing:"
    echo "aws lambda create-function-url-config --function-name $LAMBDA_FUNCTION_NAME --auth-type NONE --cors '{\"AllowCredentials\": false, \"AllowHeaders\": [\"*\"], \"AllowMethods\": [\"*\"], \"AllowOrigins\": [\"*\"]}'"
}

# Main deployment function
main() {
    print_status "Starting FastAPI to AWS Lambda deployment..."
    
    check_aws_cli
    get_account_id
    create_ecr_repository
    authenticate_docker
    build_docker_image
    push_to_ecr
    deploy_lambda
    create_api_gateway
    
    print_success "Deployment completed successfully!"
    print_status "Next steps:"
    echo "1. Test your Lambda function in the AWS Console"
    echo "2. Create API Gateway integration"
    echo "3. Set up custom domain (optional)"
    echo "4. Configure monitoring and logging"
}

# Run main function
main "$@"