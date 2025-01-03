#!/bin/bash

# AWS CLI configurations
AWS_REGION="us-east-1"
S3_BUCKET_NAME="nerf-pipeline-bucket"
ECR_REPOSITORY="827432256119.dkr.ecr.$AWS_REGION.amazonaws.com/nerf-backend"

# Create S3 bucket
aws s3api create-bucket --bucket $S3_BUCKET_NAME --region $AWS_REGION

# Create ECR repository
aws ecr create-repository --repository-name nerf-backend --region $AWS_REGION

# Set up ECS roles and policies
aws iam create-role --role-name ECSExecutionRole --assume-role-policy-document file://ecs-execution-role-trust-policy.json
aws iam attach-role-policy --role-name ECSExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

aws iam create-role --role-name ECSTaskRole --assume-role-policy-document file://ecs-task-role-trust-policy.json
aws iam attach-role-policy --role-name ECSTaskRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam attach-role-policy --role-name ECSTaskRole --policy-arn arn:aws:iam::aws:policy/AmazonRDSFullAccess

# Output setup details
echo "AWS setup complete."
