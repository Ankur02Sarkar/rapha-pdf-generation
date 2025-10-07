#!/bin/bash

# AWS Lambda CloudWatch Monitoring Setup Script
# This script sets up comprehensive monitoring and alerting for the RaphaCure PDF API

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/deploy-config.json"

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get configuration value
get_config() {
    local env="$1"
    local key="$2"
    jq -r ".${env}.${key}" "$CONFIG_FILE"
}

# Function to create CloudWatch dashboard
create_dashboard() {
    local env="$1"
    local function_name="$2"
    local region="$3"
    
    log_info "Creating CloudWatch dashboard for $function_name..."
    
    local dashboard_name="RaphaPDF-${env^}"
    local dashboard_body=$(cat <<EOF
{
    "widgets": [
        {
            "type": "metric",
            "x": 0,
            "y": 0,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/Lambda", "Invocations", "FunctionName", "$function_name" ],
                    [ ".", "Errors", ".", "." ],
                    [ ".", "Throttles", ".", "." ],
                    [ ".", "Duration", ".", "." ],
                    [ ".", "ConcurrentExecutions", ".", "." ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "$region",
                "title": "Lambda Function Metrics",
                "period": 300,
                "stat": "Sum"
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 0,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/Lambda", "Duration", "FunctionName", "$function_name", { "stat": "Average" } ],
                    [ "...", { "stat": "Maximum" } ],
                    [ "...", { "stat": "Minimum" } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "$region",
                "title": "Function Duration",
                "period": 300,
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 6,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/ApiGateway", "Count", "ApiName", "rapha-pdf-api-$env" ],
                    [ ".", "4XXError", ".", "." ],
                    [ ".", "5XXError", ".", "." ],
                    [ ".", "Latency", ".", "." ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "$region",
                "title": "API Gateway Metrics",
                "period": 300
            }
        },
        {
            "type": "log",
            "x": 12,
            "y": 6,
            "width": 12,
            "height": 6,
            "properties": {
                "query": "SOURCE '/aws/lambda/$function_name'\n| fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 20",
                "region": "$region",
                "title": "Recent Errors",
                "view": "table"
            }
        }
    ]
}
EOF
)
    
    aws cloudwatch put-dashboard \
        --dashboard-name "$dashboard_name" \
        --dashboard-body "$dashboard_body" \
        --region "$region"
    
    log_success "Dashboard '$dashboard_name' created successfully"
}

# Function to create CloudWatch alarms
create_alarms() {
    local env="$1"
    local function_name="$2"
    local region="$3"
    local sns_topic_arn="$4"
    
    log_info "Creating CloudWatch alarms for $function_name..."
    
    # Error rate alarm
    aws cloudwatch put-metric-alarm \
        --alarm-name "RaphaPDF-${env^}-ErrorRate" \
        --alarm-description "High error rate for $function_name" \
        --metric-name "Errors" \
        --namespace "AWS/Lambda" \
        --statistic "Sum" \
        --period 300 \
        --threshold 5 \
        --comparison-operator "GreaterThanThreshold" \
        --evaluation-periods 2 \
        --alarm-actions "$sns_topic_arn" \
        --dimensions "Name=FunctionName,Value=$function_name" \
        --region "$region"
    
    # Duration alarm
    aws cloudwatch put-metric-alarm \
        --alarm-name "RaphaPDF-${env^}-HighDuration" \
        --alarm-description "High duration for $function_name" \
        --metric-name "Duration" \
        --namespace "AWS/Lambda" \
        --statistic "Average" \
        --period 300 \
        --threshold 25000 \
        --comparison-operator "GreaterThanThreshold" \
        --evaluation-periods 2 \
        --alarm-actions "$sns_topic_arn" \
        --dimensions "Name=FunctionName,Value=$function_name" \
        --region "$region"
    
    # Throttle alarm
    aws cloudwatch put-metric-alarm \
        --alarm-name "RaphaPDF-${env^}-Throttles" \
        --alarm-description "Function throttling for $function_name" \
        --metric-name "Throttles" \
        --namespace "AWS/Lambda" \
        --statistic "Sum" \
        --period 300 \
        --threshold 1 \
        --comparison-operator "GreaterThanOrEqualToThreshold" \
        --evaluation-periods 1 \
        --alarm-actions "$sns_topic_arn" \
        --dimensions "Name=FunctionName,Value=$function_name" \
        --region "$region"
    
    # API Gateway 4XX errors
    aws cloudwatch put-metric-alarm \
        --alarm-name "RaphaPDF-${env^}-API-4XXErrors" \
        --alarm-description "High 4XX error rate for API Gateway" \
        --metric-name "4XXError" \
        --namespace "AWS/ApiGateway" \
        --statistic "Sum" \
        --period 300 \
        --threshold 10 \
        --comparison-operator "GreaterThanThreshold" \
        --evaluation-periods 2 \
        --alarm-actions "$sns_topic_arn" \
        --dimensions "Name=ApiName,Value=rapha-pdf-api-$env" \
        --region "$region"
    
    # API Gateway 5XX errors
    aws cloudwatch put-metric-alarm \
        --alarm-name "RaphaPDF-${env^}-API-5XXErrors" \
        --alarm-description "High 5XX error rate for API Gateway" \
        --metric-name "5XXError" \
        --namespace "AWS/ApiGateway" \
        --statistic "Sum" \
        --period 300 \
        --threshold 3 \
        --comparison-operator "GreaterThanThreshold" \
        --evaluation-periods 1 \
        --alarm-actions "$sns_topic_arn" \
        --dimensions "Name=ApiName,Value=rapha-pdf-api-$env" \
        --region "$region"
    
    log_success "CloudWatch alarms created successfully"
}

# Function to create SNS topic for notifications
create_sns_topic() {
    local env="$1"
    local region="$2"
    local email="$3"
    
    log_info "Creating SNS topic for notifications..."
    
    local topic_name="rapha-pdf-api-alerts-$env"
    
    # Create SNS topic
    local topic_arn=$(aws sns create-topic \
        --name "$topic_name" \
        --region "$region" \
        --query 'TopicArn' \
        --output text)
    
    # Subscribe email to topic if provided
    if [[ -n "$email" ]]; then
        aws sns subscribe \
            --topic-arn "$topic_arn" \
            --protocol email \
            --notification-endpoint "$email" \
            --region "$region"
        
        log_info "Email subscription created. Please check your email and confirm the subscription."
    fi
    
    echo "$topic_arn"
}

# Function to setup log insights queries
setup_log_insights() {
    local env="$1"
    local function_name="$2"
    local region="$3"
    
    log_info "Setting up CloudWatch Insights queries..."
    
    # Create query for error analysis
    aws logs put-query-definition \
        --name "RaphaPDF-${env^}-ErrorAnalysis" \
        --log-group-names "/aws/lambda/$function_name" \
        --query-string 'fields @timestamp, @message, @requestId
| filter @message like /ERROR/
| sort @timestamp desc
| limit 50' \
        --region "$region"
    
    # Create query for performance analysis
    aws logs put-query-definition \
        --name "RaphaPDF-${env^}-PerformanceAnalysis" \
        --log-group-names "/aws/lambda/$function_name" \
        --query-string 'fields @timestamp, @duration, @billedDuration, @memorySize, @maxMemoryUsed
| filter @type = "REPORT"
| sort @timestamp desc
| limit 50' \
        --region "$region"
    
    # Create query for PDF generation metrics
    aws logs put-query-definition \
        --name "RaphaPDF-${env^}-PDFMetrics" \
        --log-group-names "/aws/lambda/$function_name" \
        --query-string 'fields @timestamp, @message
| filter @message like /PDF generation/
| parse @message "PDF generation completed in * seconds, size: * bytes"
| sort @timestamp desc
| limit 50' \
        --region "$region"
    
    log_success "CloudWatch Insights queries created successfully"
}

# Function to enable X-Ray tracing
enable_xray_tracing() {
    local function_name="$1"
    local region="$2"
    
    log_info "Enabling X-Ray tracing for $function_name..."
    
    aws lambda put-function-configuration \
        --function-name "$function_name" \
        --tracing-config Mode=Active \
        --region "$region"
    
    log_success "X-Ray tracing enabled successfully"
}

# Main function
main() {
    local env="${1:-production}"
    local email="${2:-}"
    
    log_info "Setting up monitoring for environment: $env"
    
    # Check prerequisites
    if ! command_exists aws; then
        log_error "AWS CLI is not installed"
        exit 1
    fi
    
    if ! command_exists jq; then
        log_error "jq is not installed"
        exit 1
    fi
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    
    # Get configuration
    local function_name=$(get_config "$env" "function_name")
    local region=$(get_config "$env" "region")
    
    if [[ "$function_name" == "null" ]] || [[ "$region" == "null" ]]; then
        log_error "Invalid configuration for environment: $env"
        exit 1
    fi
    
    log_info "Function: $function_name"
    log_info "Region: $region"
    
    # Create SNS topic for alerts
    local sns_topic_arn=$(create_sns_topic "$env" "$region" "$email")
    log_success "SNS topic created: $sns_topic_arn"
    
    # Create CloudWatch dashboard
    create_dashboard "$env" "$function_name" "$region"
    
    # Create CloudWatch alarms
    create_alarms "$env" "$function_name" "$region" "$sns_topic_arn"
    
    # Setup log insights queries
    setup_log_insights "$env" "$function_name" "$region"
    
    # Enable X-Ray tracing
    enable_xray_tracing "$function_name" "$region"
    
    log_success "Monitoring setup completed successfully!"
    log_info "Dashboard URL: https://$region.console.aws.amazon.com/cloudwatch/home?region=$region#dashboards:name=RaphaPDF-${env^}"
    
    if [[ -n "$email" ]]; then
        log_warning "Please check your email and confirm the SNS subscription to receive alerts"
    fi
}

# Show usage if no arguments provided
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <environment> [email]"
    echo ""
    echo "Arguments:"
    echo "  environment    Deployment environment (production, staging, development)"
    echo "  email          Email address for alert notifications (optional)"
    echo ""
    echo "Examples:"
    echo "  $0 production admin@raphacure.com"
    echo "  $0 staging"
    exit 1
fi

# Run main function
main "$@"