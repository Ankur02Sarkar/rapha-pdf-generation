# FastAPI to AWS Lambda Deployment Guide

This guide follows the deployment process outlined in the [Searce blog post](https://blog.searce.com/fastapi-container-app-deployment-using-aws-lambda-and-api-gateway-6721904531d0) for deploying a containerized FastAPI application to AWS Lambda with API Gateway.

## Architecture Overview

```
Internet → API Gateway → AWS Lambda (FastAPI + Mangum) → Your Application
```

## Prerequisites

Before starting the deployment, ensure you have:

1. **AWS CLI installed and configured**
   ```bash
   aws configure
   ```

2. **Docker installed and running**
   ```bash
   docker --version
   ```

3. **AWS Account with appropriate permissions**
   - ECR repository creation
   - Lambda function creation and management
   - IAM role creation
   - API Gateway creation

## Quick Deployment

### Option 1: Automated Deployment Script

Run the automated deployment script:

```bash
./deploy.sh
```

This script will:
- Create ECR repository
- Build and push Docker image
- Create/update Lambda function
- Set up IAM roles

### Option 2: Manual Step-by-Step Deployment

#### Step 1: Create ECR Repository

```bash
aws ecr create-repository \
    --repository-name rapha-pdf-generation \
    --region ap-south-1 \
    --image-scanning-configuration scanOnPush=true
```

#### Step 2: Authenticate Docker with ECR

```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <YOUR_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com
```

#### Step 3: Build Docker Image

```bash
docker build -t rapha-pdf-generation .
```

#### Step 4: Tag and Push Image

```bash
# Replace <YOUR_ACCOUNT_ID> with your actual AWS account ID
docker tag rapha-pdf-generation:latest <YOUR_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/rapha-pdf-generation:latest
docker push <YOUR_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/rapha-pdf-generation:latest
```

#### Step 5: Create Lambda Function

```bash
# Create execution role first
aws iam create-role \
    --role-name lambda-execution-role-rapha-pdf \
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
    }'

# Attach basic execution policy
aws iam attach-role-policy \
    --role-name lambda-execution-role-rapha-pdf \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create Lambda function
aws lambda create-function \
    --function-name rapha-pdf-generation-lambda \
    --package-type Image \
    --code ImageUri=<YOUR_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/rapha-pdf-generation:latest \
    --role arn:aws:iam::<YOUR_ACCOUNT_ID>:role/lambda-execution-role-rapha-pdf \
    --timeout 30 \
    --memory-size 512 \
    --region ap-south-1
```

## API Gateway Integration

### Option 1: CloudFormation Template

Deploy the API Gateway using the provided CloudFormation template:

```bash
aws cloudformation deploy \
    --template-file api-gateway-template.yaml \
    --stack-name rapha-pdf-api-gateway \
    --parameter-overrides LambdaFunctionName=rapha-pdf-generation-lambda \
    --capabilities CAPABILITY_IAM \
    --region ap-south-1
```

### Option 2: Lambda Function URL (Quick Testing)

For quick testing, create a Lambda Function URL:

```bash
aws lambda create-function-url-config \
    --function-name rapha-pdf-generation-lambda \
    --auth-type NONE \
    --cors '{
        "AllowCredentials": false,
        "AllowHeaders": ["*"],
        "AllowMethods": ["*"],
        "AllowOrigins": ["*"]
    }'
```

## Testing Your Deployment

### Test Lambda Function Directly

```bash
aws lambda invoke \
    --function-name rapha-pdf-generation-lambda \
    --payload '{
        "httpMethod": "GET",
        "path": "/health",
        "headers": {},
        "queryStringParameters": null,
        "body": null
    }' \
    response.json

cat response.json
```

### Test via API Gateway

Once API Gateway is deployed, test your endpoints:

```bash
# Get the API Gateway URL from CloudFormation outputs
API_URL=$(aws cloudformation describe-stacks \
    --stack-name rapha-pdf-api-gateway \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
    --output text)

# Test health endpoint
curl $API_URL/health

# Test your PDF endpoints
curl -X POST $API_URL/api/v1/pdf/generate \
    -H "Content-Type: application/json" \
    -d '{"your": "data"}'
```

## Configuration

### Environment Variables

Set environment variables for your Lambda function:

```bash
aws lambda update-function-configuration \
    --function-name rapha-pdf-generation-lambda \
    --environment Variables='{
        "ENVIRONMENT": "production",
        "LOG_LEVEL": "INFO"
    }'
```

### Memory and Timeout Settings

Adjust based on your application needs:

```bash
aws lambda update-function-configuration \
    --function-name rapha-pdf-generation-lambda \
    --memory-size 1024 \
    --timeout 60
```

## Monitoring and Logging

### CloudWatch Logs

Your Lambda function logs are automatically sent to CloudWatch:

```bash
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/rapha-pdf-generation-lambda
```

### View Recent Logs

```bash
aws logs tail /aws/lambda/rapha-pdf-generation-lambda --follow
```

## Troubleshooting

### Common Issues

1. **"Not Found" errors**: Check API Gateway proxy integration and Mangum configuration
2. **Timeout errors**: Increase Lambda timeout and memory
3. **Import errors**: Ensure all dependencies are in requirements.txt
4. **Permission errors**: Verify IAM roles and policies

### Debug Lambda Function

Enable detailed logging in your Lambda function:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Locally

Test your FastAPI app locally before deployment:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Cost Optimization

1. **Right-size memory allocation**: Start with 512MB and adjust based on usage
2. **Set appropriate timeout**: Don't set unnecessarily high timeouts
3. **Use provisioned concurrency** only if needed for consistent performance
4. **Monitor CloudWatch metrics** for optimization opportunities

## Security Best Practices

1. **Use API Keys**: Enable API key requirement in API Gateway
2. **Enable CORS properly**: Configure CORS settings based on your needs
3. **Use VPC**: Deploy Lambda in VPC if accessing private resources
4. **Environment variables**: Use AWS Systems Manager Parameter Store for sensitive data

## Updating Your Application

To update your deployed application:

```bash
# Rebuild and push new image
docker build -t rapha-pdf-generation .
docker tag rapha-pdf-generation:latest <YOUR_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/rapha-pdf-generation:latest
docker push <YOUR_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/rapha-pdf-generation:latest

# Update Lambda function
aws lambda update-function-code \
    --function-name rapha-pdf-generation-lambda \
    --image-uri <YOUR_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/rapha-pdf-generation:latest
```

## Additional Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Mangum Documentation](https://mangum.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Original Blog Post](https://blog.searce.com/fastapi-container-app-deployment-using-aws-lambda-and-api-gateway-6721904531d0)