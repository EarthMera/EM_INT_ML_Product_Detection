#!/bin/bash

# Ensure required environment variables are set
if [ -z "$AWS_REGION" ] || [ -z "$ECR_REPOSITORY" ]; then
  echo "AWS_REGION and ECR_REPOSITORY must be set as environment variables."
  exit 1
fi

# Authenticate Docker with AWS ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$ECR_REPOSITORY"

# Build the Docker image
docker build -t nerf-backend .

# Tag and push the image
docker tag nerf-backend:latest "$ECR_REPOSITORY:latest"
docker push "$ECR_REPOSITORY:latest"

# Update ECS service to use the new image
CLUSTER_NAME=$(aws ecs list-clusters --query "clusterArns[0]" --output text)
SERVICE_NAME=$(aws ecs list-services --cluster $CLUSTER_NAME --query "serviceArns[0]" --output text)
aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment

echo "Deployment complete."
