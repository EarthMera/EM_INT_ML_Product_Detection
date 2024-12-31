#!/bin/bash

# Define variables
BUCKET_NAME="product-videos-bucket"
ECS_CLUSTER_NAME="nerf-cluster"
ECS_TASK_ROLE_NAME="nerf-task-role"
ECS_EXECUTION_ROLE_NAME="nerf-execution-role"
LOG_GROUP_NAME="/ecs/nerf-pipeline-task"
REGION="us-east-1" 

echo "Setting up AWS resources for the project..."

# Step 1: Create S3 bucket
echo "Creating S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION
aws s3api put-bucket-versioning --bucket $BUCKET_NAME --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket $BUCKET_NAME \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# Step 2: Create IAM roles
echo "Creating IAM roles for ECS..."

# Create ECS Task Role
aws iam create-role --role-name $ECS_TASK_ROLE_NAME \
  --assume-role-policy-document file://ecs-task-role-trust-policy.json

aws iam attach-role-policy --role-name $ECS_TASK_ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Create ECS Execution Role
aws iam create-role --role-name $ECS_EXECUTION_ROLE_NAME \
  --assume-role-policy-document file://ecs-execution-role-trust-policy.json

aws iam attach-role-policy --role-name $ECS_EXECUTION_ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Step 3: Create CloudWatch Logs group
echo "Creating CloudWatch log group..."
aws logs create-log-group --log-group-name $LOG_GROUP_NAME || true

# Step 4: Create ECS cluster
echo "Creating ECS cluster..."
aws ecs create-cluster --cluster-name $ECS_CLUSTER_NAME

echo "AWS setup complete!"
