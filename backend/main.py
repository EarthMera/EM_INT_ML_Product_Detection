from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List
from contextlib import asynccontextmanager
from db import initialize_db, add_product, get_products, get_product_by_id, update_product, delete_product, initialize_connection_pool
from services import run_nerf_pipeline, get_synthetic_images

class ProductInput(BaseModel):
    """Input model for creating a product."""
    name: str
    description: str

class PipelineInput(BaseModel):
    """Input model for triggering the pipeline."""
    video_path: str

class ProductUpdateInput(BaseModel):
    """Input model for updating a product."""
    name: str = Field(None, description="New name for the product")
    description: str = Field(None, description="New description for the product")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management: Initialize database on startup."""
    print("Initializing the database...")
    initialize_connection_pool()
    initialize_db()
    yield  # Application runs here
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.post("/products")
def create_product(product: ProductInput):
    """Create a new product."""
    try:
        product_id = add_product(product.name, product.description)
        return {"id": product_id, "name": product.name, "description": product.description}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating product: {str(e)}")

@app.get("/products")
def list_products() -> List[dict]:
    """List all products."""
    return get_products()

@app.get("/products/{product_id}")
def retrieve_product(product_id: int) -> dict:
    """Retrieve a product by ID."""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product

@app.put("/products/{product_id}")
def update_product_endpoint(product_id: int, product_update: ProductUpdateInput, videos: List[str] = None):
    """Update a product's name, description, and/or videos."""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    try:
        update_product(
            product_id=product_id,
            name=product_update.name,
            description=product_update.description,
            videos=videos,
        )
        updated_product = get_product_by_id(product_id)
        return {
            "detail": f"Product {product_id} updated successfully.",
            "product": updated_product,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")

@app.delete("/products/{product_id}")
def delete_product_endpoint(product_id: int):
    """Delete a product."""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    delete_product(product_id)
    return {"detail": f"Product {product_id} deleted."}

@app.post("/products/{product_id}/run-pipeline")
def run_pipeline(product_id: int, pipeline_input: PipelineInput):
    """Run the NeRF pipeline locally within the current container."""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    video_s3_path = pipeline_input.video_path
    try:
        run_nerf_pipeline(product_id, video_s3_path)
        return {
            "detail": f"Pipeline executed locally for product {product_id}.",
            "status": "completed",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

@app.get("/products/{product_id}/synthetic-images")
def get_images(product_id: int):
    """Retrieve synthetic images for a product."""
    try:
        image_urls = get_synthetic_images(product_id)
        return {"product_id": product_id, "images": image_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve synthetic images: {str(e)}")
