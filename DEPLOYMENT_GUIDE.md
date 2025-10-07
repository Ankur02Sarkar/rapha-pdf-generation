# AWS Lambda Deployment Guide for RaphaCure PDF Generation API

This guide provides step-by-step instructions for deploying your FastAPI PDF generation service to AWS Lambda using the AWS CLI.

## 📋 Prerequisites

### 1. AWS CLI Setup
```bash
# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Configure AWS CLI with your credentials
aws configure
```

### 2. Required Tools
- Python 3.9+
- Docker (for building Lambda layers)
- AWS CLI v2
- jq (for JSON processing)

### 3. AWS Permissions
Ensure your AWS user/role has the following permissions:
- `lambda:*`
- `iam:CreateRole`
- `iam:AttachRolePolicy`
- `iam:PassRole`
- `apigateway:*`
- `logs:*`

## 🚀 Deployment Steps

### Step 1: Prepare Environment Configuration

1. **Update Environment Files**
   
   Edit `.env.production` with your specific values:
   ```bash
   # Application Settings
   APP_NAME=rapha-pdf-api
   ENVIRONMENT=production
   DEBUG=false
   
   # Update with your domain or leave as default
   ALLOWED_HOSTS=["*"]
   
   # Add your secret key
   SECRET_KEY=your-super-secret-key-here
   ```

2. **Update Deployment Configuration**
   
   Edit `deploy-config.json` to match your AWS setup:
   ```json
   {
     "production": {
       "function_name": "rapha-pdf-api-prod",
       "region": "ap-south-1",
       "runtime": "python3.9",
       "timeout": 30,
       "memory_size": 1024
     }
   }
   ```

### Step 2: Build Lambda Layers (Optional but Recommended)

Lambda layers help reduce deployment package size and improve cold start times:

```bash
# Build and deploy Lambda layers for WeasyPrint dependencies
./create-lambda-layer.sh production

# This will create:
# - rapha-pdf-python-deps-prod (Python dependencies)
# - rapha-pdf-system-libs-prod (System libraries)
# - rapha-pdf-fonts-prod (Fonts)
```

### Step 3: Deploy the Application

```bash
# Deploy to production
./deploy.sh production

# Or deploy to staging
./deploy.sh staging
```

The deployment script will:
1. ✅ Check prerequisites
2. ✅ Create IAM roles and policies
3. ✅ Package the application
4. ✅ Deploy Lambda function
5. ✅ Set up API Gateway
6. ✅ Configure permissions

### Step 4: Test the Deployment

After deployment, you'll receive an API Gateway URL. Test it using:

```bash
# Replace with your actual API Gateway URL
python test-lambda-deployment.py https://your-api-id.execute-api.ap-south-1.amazonaws.com/prod
```

## 📁 Project Structure After Deployment

```
rapha-pdf-generation/
├── app/                          # Original FastAPI application
├── lambda_handler.py             # Lambda entry point with Mangum
├── requirements-lambda.txt       # Lambda-optimized dependencies
├── deploy.sh                     # Main deployment script
├── create-lambda-layer.sh        # Lambda layer creation script
├── test-lambda-deployment.py     # Deployment testing script
├── .env.production               # Production environment variables
├── .env.staging                  # Staging environment variables
├── deploy-config.json            # Deployment configuration
└── DEPLOYMENT_GUIDE.md           # This guide
```

## 🔧 Configuration Files Explained

### `lambda_handler.py`
- **Purpose**: AWS Lambda entry point using Mangum adapter
- **Key Features**: 
  - Handles API Gateway integration
  - Manages CORS and MIME types
  - Optimized for Lambda environment

### `requirements-lambda.txt`
- **Purpose**: Lambda-optimized dependencies
- **Optimizations**:
  - Removed development dependencies
  - Optimized WeasyPrint for Lambda
  - Reduced package size

### `deploy.sh`
- **Purpose**: Automated deployment script
- **Features**:
  - Environment validation
  - IAM role creation
  - Lambda function deployment
  - API Gateway setup
  - Error handling and rollback

### Environment Files
- **`.env.production`**: Production-specific settings
- **`.env.staging`**: Staging-specific settings
- **Key Settings**: Timeouts, memory limits, security configurations

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. WeasyPrint Dependencies
**Problem**: WeasyPrint fails to load fonts or libraries
**Solution**: 
```bash
# Rebuild Lambda layers with system dependencies
./create-lambda-layer.sh production --force
```

#### 2. Timeout Issues
**Problem**: Lambda function times out during PDF generation
**Solution**: 
- Increase timeout in `deploy-config.json`
- Optimize PDF generation settings in `.env.production`

#### 3. Memory Issues
**Problem**: Lambda runs out of memory
**Solution**:
- Increase memory size in `deploy-config.json`
- Monitor CloudWatch logs for memory usage

#### 4. API Gateway Issues
**Problem**: CORS or routing issues
**Solution**:
- Check `lambda_handler.py` CORS configuration
- Verify API Gateway integration settings

### Debugging Commands

```bash
# Check Lambda function logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/rapha-pdf-api"

# Get recent logs
aws logs filter-log-events --log-group-name "/aws/lambda/rapha-pdf-api-prod" --start-time $(date -d '1 hour ago' +%s)000

# Test Lambda function directly
aws lambda invoke --function-name rapha-pdf-api-prod --payload '{}' response.json

# Check API Gateway
aws apigateway get-rest-apis
```

## 📊 Performance Optimization

### Lambda Configuration
- **Memory**: Start with 1024MB, adjust based on usage
- **Timeout**: 30 seconds for PDF generation
- **Provisioned Concurrency**: Consider for production workloads

### PDF Generation Optimization
- **Template Caching**: Templates are cached in memory
- **Font Optimization**: Only essential fonts included
- **Image Optimization**: Compress images in templates

### Monitoring
- **CloudWatch Metrics**: Monitor duration, errors, throttles
- **X-Ray Tracing**: Enable for detailed performance analysis
- **Custom Metrics**: Track PDF generation times

## 🔒 Security Best Practices

### Environment Variables
- Store sensitive data in AWS Systems Manager Parameter Store
- Use AWS Secrets Manager for API keys
- Never commit secrets to version control

### IAM Policies
- Follow principle of least privilege
- Use resource-specific permissions
- Regular audit of permissions

### API Security
- Implement API key authentication
- Use AWS WAF for additional protection
- Monitor for unusual traffic patterns

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy to AWS Lambda
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-south-1
      - name: Deploy to Lambda
        run: ./deploy.sh production
```

## 📈 Scaling Considerations

### Auto Scaling
- Lambda automatically scales based on demand
- Configure reserved concurrency if needed
- Monitor throttling metrics

### Cost Optimization
- Use Lambda layers to reduce deployment size
- Optimize memory allocation based on actual usage
- Consider Provisioned Concurrency for consistent performance

### Multi-Region Deployment
- Deploy to multiple regions for global availability
- Use Route 53 for traffic routing
- Implement cross-region monitoring

## 📞 Support and Maintenance

### Regular Maintenance Tasks
1. **Weekly**: Review CloudWatch logs and metrics
2. **Monthly**: Update dependencies and security patches
3. **Quarterly**: Review and optimize Lambda configuration

### Monitoring Alerts
Set up CloudWatch alarms for:
- High error rates
- Increased latency
- Memory usage spikes
- Throttling events

### Backup and Recovery
- Lambda functions are automatically backed up
- Store deployment artifacts in S3
- Document rollback procedures

---

## 🎯 Quick Start Checklist

- [ ] AWS CLI configured with proper permissions
- [ ] Environment files updated with your values
- [ ] Docker installed (for Lambda layers)
- [ ] Run `./create-lambda-layer.sh production`
- [ ] Run `./deploy.sh production`
- [ ] Test with `python test-lambda-deployment.py <API_URL>`
- [ ] Set up monitoring and alerts
- [ ] Document your specific configuration

**Need Help?** Check the troubleshooting section or review the CloudWatch logs for detailed error information.