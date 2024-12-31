from fastapi import FastAPI, HTTPException, UploadFile
from db import initialize_db, add_product, get_products, get_product_by_name, update_product, delete_product
from services import upload_video_to_s3, trigger_nerf_pipeline_task, check_task_status

app = FastAPI()

# Initialize the database
initialize_db()

@app.post("/products")
def create_product(name: str, description: str):
    """Create a new product."""
    try:
        product_id = add_product(name, description)
        return {"id": product_id, "name": name, "description": description}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating product: {str(e)}")

@app.get("/products")
def list_products():
    """List all products."""
    return get_products()

@app.get("/products/{product_name}")
def retrieve_product(product_name: str):
    """Retrieve a product by name."""
    product = get_product_by_name(product_name)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product

@app.delete("/products/{product_name}")
def delete_product_endpoint(product_name: str):
    """Delete a product."""
    product = get_product_by_name(product_name)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    delete_product(product_name)
    return {"detail": f"Product {product_name} deleted."}

@app.post("/products/{product_name}/videos")
def upload_video(product_name: str, file: UploadFile):
    """Upload a product video to S3."""
    product = get_product_by_name(product_name)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    s3_video_path = upload_video_to_s3(product_name, file)
    videos = product["videos"].split(",") if product["videos"] else []
    videos.append(s3_video_path)
    update_product(product_name, videos=videos)
    return {"detail": "Video uploaded", "video_path": s3_video_path}

@app.post("/products/{product_name}/run-pipeline")
def run_pipeline(product_name: str):
    """Trigger the NeRF pipeline via ECS."""
    product = get_product_by_name(product_name)
    if not product or not product["videos"]:
        raise HTTPException(status_code=404, detail="Product not found or no videos available.")

    video_s3_path = product["videos"].split(",")[0]
    try:
        task_arn = trigger_nerf_pipeline_task(product_name, video_s3_path)
        update_product(product_name, status="in-progress")
        return {"detail": f"Pipeline started for {product_name}. Task ARN: {task_arn}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_name}/status")
def get_pipeline_status(product_name: str, task_arn: str):
    """Check the ECS task status."""
    try:
        status = check_task_status(task_arn)
        return {"task_arn": task_arn, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check task status: {str(e)}")
