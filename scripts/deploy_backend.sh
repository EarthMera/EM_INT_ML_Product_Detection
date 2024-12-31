#!/bin/bash

# Define variables
ECR_REPO="<your_ecr_repo>"  # need to replace
DOCKER_IMAGE_TAG="latest"

# Build and push Docker image
echo "Building Docker image..."
docker build -t nerf-backend .

echo "Tagging Docker image..."
docker tag nerf-backend:latest $ECR_REPO:$DOCKER_IMAGE_TAG

echo "Pushing Docker image to ECR..."
docker push $ECR_REPO:$DOCKER_IMAGE_TAG

# Update ECS service to use the new image
echo "Updating ECS service..."
aws ecs update-service --cluster nerf-cluster --service nerf-backend-service --force-new-deployment

echo "Deployment complete!"
