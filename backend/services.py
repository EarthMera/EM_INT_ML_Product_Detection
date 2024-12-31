import boto3

s3_client = boto3.client("s3")
ecs_client = boto3.client("ecs")

BUCKET_NAME = "product-videos-bucket"
ECS_CLUSTER_NAME = "nerf-cluster"
ECS_TASK_DEFINITION = "nerf-pipeline-task"

def upload_video_to_s3(product_name, file):
    """Upload a video to S3."""
    s3_key = f"products/{product_name}/{file.filename}"
    s3_client.upload_fileobj(file.file, BUCKET_NAME, s3_key)
    return f"s3://{BUCKET_NAME}/{s3_key}"

def trigger_nerf_pipeline_task(product_name, video_s3_path):
    """Trigger ECS task to run the NeRF pipeline."""
    response = ecs_client.run_task(
        cluster=ECS_CLUSTER_NAME,
        taskDefinition=ECS_TASK_DEFINITION,
        launchType="FARGATE",
        overrides={
            "containerOverrides": [
                {
                    "name": "nerf-container",
                    "command": [
                        "python",
                        "synthetic_image_generation/pipeline_entry.py",
                        "--product_name",
                        product_name,
                        "--video_s3_path",
                        video_s3_path
                    ]
                }
            ]
        },
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": ["subnet-xxxxxx"], # need to replace with subnet once i get access
                "assignPublicIp": "ENABLED"
            }
        }
    )
    return response["tasks"][0]["taskArn"]

def check_task_status(task_arn):
    """Check the status of an ECS task."""
    response = ecs_client.describe_tasks(cluster=ECS_CLUSTER_NAME, tasks=[task_arn])
    task = response["tasks"][0]
    return task["lastStatus"]
