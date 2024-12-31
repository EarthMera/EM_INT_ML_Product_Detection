import os
import subprocess
import argparse
import json
import boto3

def run_colmap2nerf(product_name, video_s3_path):
    """Run colmap2nerf.py to extract frames and generate transforms.json."""
    data_dir = f"synthetic_image_generation/data/{product_name}"
    os.makedirs(data_dir, exist_ok=True)
    
    video_path = download_s3_file(video_s3_path, f"{data_dir}/{product_name}.mp4")
    
    print("Running colmap2nerf.py...")
    command = [
        "python", "synthetic_image_generation/instant-ngp/scripts/colmap2nerf.py",
        "--video_in", video_path,
        "--video_fps", "8",
        "--run_colmap",
        "--aabb_scale", "8",
        "--overwrite",
        "--output", data_dir
    ]
    subprocess.run(command, check=True)

def run_train_nerf(product_name):
    """Train the NeRF model using run.py and save the snapshot."""
    print("Training NeRF model...")
    data_dir = f"synthetic_image_generation/data/{product_name}"
    snapshot_path = f"{data_dir}/{product_name}.ingp"
    
    command = [
        "python", "synthetic_image_generation/instant-ngp/scripts/run.py",
        "--scene", data_dir,
        "--save_snapshot", snapshot_path,
        "--n_steps", "20000"
    ]
    subprocess.run(command, check=True)

def run_generate_synthetic_transforms(product_name):
    """Generate synthetic transforms.json for rendering."""
    print("Generating synthetic transforms...")
    command = [
        "python", "scripts/generate_transforms.py",
        product_name
    ]
    subprocess.run(command, check=True)

def run_render_synthetic_images(product_name):
    """Render synthetic images using the trained NeRF model and synthetic transforms."""
    print("Rendering synthetic images...")
    data_dir = f"synthetic_image_generation/data/{product_name}"
    snapshot_path = f"{data_dir}/{product_name}.ingp"
    transforms_path = f"{data_dir}/synthetic_transforms.json"
    output_dir = f"{data_dir}/synthetic_images"

    command = [
        "python", "synthetic_image_generation/instant-ngp/scripts/run.py",
        "--load_snapshot", snapshot_path,
        "--screenshot_transforms", transforms_path,
        "--screenshot_dir", output_dir,
        "--screenshot_spp", "16"
    ]
    subprocess.run(command, check=True)

def download_s3_file(s3_path, local_path):
    """Download a file from S3 to a local path."""
    print(f"Downloading {s3_path} to {local_path}...")
    bucket_name = os.getenv("S3_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("S3_BUCKET_NAME environment variable not set.")
    
    s3_client = boto3.client("s3")
    s3_key = s3_path.split(f"s3://{bucket_name}/")[1]
    s3_client.download_file(bucket_name, s3_key, local_path)
    return local_path

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run NeRF pipeline.")
    parser.add_argument("--product_name", required=True, help="The product name.")
    parser.add_argument("--video_s3_path", required=True, help="The S3 path to the input video.")
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command-line arguments or read environment variables
    args = parse_args()
    product_name = args.product_name
    video_s3_path = args.video_s3_path

    print(f"Starting pipeline for product: {product_name}")
    
    # Step 1: Run colmap2nerf.py
    run_colmap2nerf(product_name, video_s3_path)
    
    # Step 2: Train NeRF model
    run_train_nerf(product_name)
    
    # Step 3: Generate synthetic transforms
    run_generate_synthetic_transforms(product_name)
    
    # Step 4: Render synthetic images
    run_render_synthetic_images(product_name)
    
    print(f"Pipeline completed for product: {product_name}")
