import os
import subprocess
import argparse
import boto3

def run_colmap2nerf(product_id, video_s3_path):
    data_dir = f"/app/synthetic_image_generation/data/{product_id}"
    os.makedirs(data_dir, exist_ok=True)
    video_path = download_s3_file(video_s3_path, f"{data_dir}/{product_id}.mp4")
    command = [
        "python", "/app/synthetic_image_generation/instant-ngp/scripts/colmap2nerf.py",
        "--video_in", video_path, "--video_fps", "8", "--run_colmap",
        "--aabb_scale", "8", "--overwrite", "--out", data_dir
    ]
    subprocess.run(command, check=True)

def run_train_nerf(product_id):
    data_dir = f"/app/synthetic_image_generation/data/{product_id}"
    snapshot_path = f"{data_dir}/{product_id}.ingp"
    command = [
        "python", "/app/synthetic_image_generation/instant-ngp/scripts/run.py",
        data_dir, "--save_snapshot", snapshot_path, "--n_steps", "20000"
    ]
    subprocess.run(command, check=True)

def run_generate_synthetic_transforms(product_id):
    command = ["python", "scripts/generate_transforms.py", str(product_id)]
    subprocess.run(command, check=True)

def run_render_synthetic_images(product_id):
    data_dir = f"/app/synthetic_image_generation/data/{product_id}"
    snapshot_path = f"{data_dir}/{product_id}.ingp"
    transforms_path = f"{data_dir}/synthetic_transforms.json"
    output_dir = f"{data_dir}/synthetic_images"
    command = [
        "python", "/app/synthetic_image_generation/instant-ngp/scripts/run.py",
        "--load_snapshot", snapshot_path, "--screenshot_transforms", transforms_path,
        "--screenshot_dir", output_dir, "--screenshot_spp", "16"
    ]
    subprocess.run(command, check=True)

def download_s3_file(s3_path, local_path):
    bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_client = boto3.client("s3")

    # Validate and parse S3 path
    if not s3_path.startswith(f"s3://{bucket_name}/"):
        raise ValueError(f"Invalid S3 path: {s3_path}. Expected format: s3://{bucket_name}/...")

    s3_key = s3_path[len(f"s3://{bucket_name}/"):]
    if not s3_key:
        raise ValueError(f"S3 path does not include a key: {s3_path}")

    # Download file
    try:
        s3_client.download_file(bucket_name, s3_key, local_path)
        return local_path
    except Exception as e:
        raise RuntimeError(f"Failed to download file from S3: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run NeRF pipeline.")
    parser.add_argument("--product_id", required=True, type=int)
    parser.add_argument("--video_s3_path", required=True)
    args = parser.parse_args()
    run_colmap2nerf(args.product_id, args.video_s3_path)
    run_train_nerf(args.product_id)
    run_generate_synthetic_transforms(args.product_id)
    run_render_synthetic_images(args.product_id)
