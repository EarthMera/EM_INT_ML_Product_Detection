import boto3
import os
import logging
from synthetic_image_generation.pipeline_entry import (
    run_colmap2nerf,
    run_train_nerf,
    run_generate_synthetic_transforms,
    run_render_synthetic_images,
    upload_synthetic_images_to_s3
)
from db import update_product
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS clients
s3_client = boto3.client("s3", region_name=AWS_REGION)

def run_nerf_pipeline(product_id, video_s3_path):
    """
    Run the NeRF pipeline steps locally within the current task.
    """
    try:
        logger.info(f"Starting local NeRF pipeline for product ID: {product_id}")
        
        # Step 1: Run COLMAP to generate poses
        logger.info("Running COLMAP...")
        run_colmap2nerf(product_id, video_s3_path)
        
        # Step 2: Train NeRF model
        logger.info("Training NeRF model...")
        run_train_nerf(product_id)
        
        # Step 3: Generate synthetic transforms
        logger.info("Generating synthetic transforms...")
        run_generate_synthetic_transforms(product_id)
        
        # Step 4: Render synthetic images
        logger.info("Rendering synthetic images...")
        run_render_synthetic_images(product_id)

        # Step 5: Upload synthetic images to S3
        logger.info("Uploading synthetic images to S3...")
        upload_synthetic_images_to_s3(product_id)
        
        # Update the product status to completed
        update_product(product_id, status="completed")
        logger.info(f"Pipeline completed successfully for product ID: {product_id}")
    
    except Exception as e:
        logger.error(f"Failed to run NeRF pipeline: {e}")
        update_product(product_id, status="failed")
        raise

def get_synthetic_images(product_id):
    """Retrieve synthetic images from S3."""
    prefix = f"processed/{product_id}/synthetic_images/"
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
    if "Contents" not in response:
        return []
    return [f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{item['Key']}" for item in response["Contents"]]
