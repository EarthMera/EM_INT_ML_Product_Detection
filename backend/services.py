import boto3
import os
import logging
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS clients
ecs_client = boto3.client("ecs", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)

def trigger_nerf_pipeline_task(product_id, video_s3_path):
    """Trigger an ECS task for the NeRF pipeline."""
    cluster_name = os.getenv("ECS_CLUSTER_NAME")
    task_definition = os.getenv("ECS_TASK_DEFINITION")
    logger.info(f"Triggering ECS task for product ID: {product_id}")
    
    response = ecs_client.run_task(
        cluster=cluster_name,
        launchType="EC2",
        taskDefinition=task_definition,
        overrides={
            "containerOverrides": [
                {
                    "name": "nerf-backend",
                    "command": [
                        "python", 
                        "synthetic_image_generation/pipeline_entry.py",
                        "--product_id", str(product_id),
                        "--video_s3_path", video_s3_path
                    ],
                    "environment": [
                        {"name": "PRODUCT_ID", "value": str(product_id)},
                        {"name": "VIDEO_S3_PATH", "value": video_s3_path}
                    ]
                }
            ]
        },
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": os.getenv("ECS_SUBNETS").split(","),
                "securityGroups": os.getenv("ECS_SECURITY_GROUPS").split(","),
                "assignPublicIp": "ENABLED"
            }
        }
    )
    return response["tasks"][0]["taskArn"]

def check_task_status(task_arn):
    """Check the status of an ECS task."""
    cluster_name = os.getenv("ECS_CLUSTER_NAME")
    logger.info(f"Checking status for task: {task_arn}")
    response = ecs_client.describe_tasks(cluster=cluster_name, tasks=[task_arn])
    return response["tasks"][0]["lastStatus"]

def get_synthetic_images(product_id):
    """Retrieve synthetic images from S3."""
    prefix = f"processed/{product_id}/synthetic_images/"
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
    if "Contents" not in response:
        return []
    return [f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{item['Key']}" for item in response["Contents"]]
