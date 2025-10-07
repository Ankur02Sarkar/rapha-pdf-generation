#!/bin/bash

# Pre-deployment Prerequisites Check
# Verifies that all required tools and services are ready for Lambda deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Checking deployment prerequisites...${NC}\n"

# Check 1: AWS CLI
echo -e "${YELLOW}1. Checking AWS CLI...${NC}"
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version 2>&1)
    echo -e "   ✅ AWS CLI installed: ${AWS_VERSION}"
    
    # Check AWS credentials
    if aws sts get-caller-identity &> /dev/null; then
        AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
        AWS_REGION=$(aws configure get region)
        echo -e "   ✅ AWS credentials configured"
        echo -e "   📋 Account: ${AWS_ACCOUNT}"
        echo -e "   🌍 Region: ${AWS_REGION}"
    else
        echo -e "   ❌ AWS credentials not configured"
        echo -e "   💡 Run: aws configure"
        exit 1
    fi
else
    echo -e "   ❌ AWS CLI not installed"
    echo -e "   💡 Run: brew install awscli"
    exit 1
fi

echo ""

# Check 2: Docker
echo -e "${YELLOW}2. Checking Docker...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "   ✅ Docker installed: ${DOCKER_VERSION}"
    
    # Check if Docker daemon is running
    if docker info &> /dev/null; then
        echo -e "   ✅ Docker daemon is running"
    else
        echo -e "   ❌ Docker daemon is not running"
        echo -e "   💡 Start Docker Desktop application"
        exit 1
    fi
else
    echo -e "   ❌ Docker not installed"
    echo -e "   💡 Install Docker Desktop from https://docker.com"
    exit 1
fi

echo ""

# Check 3: Required files
echo -e "${YELLOW}3. Checking required files...${NC}"
REQUIRED_FILES=("main.py" "requirements.txt" "Dockerfile" "deploy.sh" "app/handler.py")

for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "   ✅ ${file} exists"
    else
        echo -e "   ❌ ${file} missing"
        exit 1
    fi
done

echo ""

# Check 4: Python dependencies
echo -e "${YELLOW}4. Checking Python dependencies...${NC}"
if [[ -f "requirements.txt" ]]; then
    if grep -q "mangum" requirements.txt; then
        echo -e "   ✅ Mangum dependency found"
    else
        echo -e "   ❌ Mangum dependency missing"
        exit 1
    fi
    
    if grep -q "fastapi" requirements.txt; then
        echo -e "   ✅ FastAPI dependency found"
    else
        echo -e "   ❌ FastAPI dependency missing"
        exit 1
    fi
fi

echo ""

# Check 5: ECR permissions (optional check)
echo -e "${YELLOW}5. Checking ECR permissions...${NC}"
if aws ecr describe-repositories --region $(aws configure get region) &> /dev/null; then
    echo -e "   ✅ ECR access verified"
elif aws ecr create-repository --repository-name test-permissions --region $(aws configure get region) &> /dev/null; then
    aws ecr delete-repository --repository-name test-permissions --region $(aws configure get region) --force &> /dev/null
    echo -e "   ✅ ECR permissions verified"
else
    echo -e "   ⚠️  ECR permissions may be limited"
    echo -e "   💡 Ensure your AWS user has ECR permissions"
fi

echo ""
echo -e "${GREEN}🎉 All prerequisites check passed!${NC}"
echo -e "${GREEN}✅ Ready to deploy to AWS Lambda${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "   1. Run: ${YELLOW}./deploy.sh${NC}"
echo -e "   2. Test: ${YELLOW}python test_lambda_deployment.py${NC}"
echo ""