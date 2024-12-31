#!/bin/bash

PRODUCT_NAME=$1
DATA_DIR="synthetic_image_generation/data/${PRODUCT_NAME}"
VIDEO_PATH="${DATA_DIR}/${PRODUCT_NAME}.mp4"
INSTANT_NGP_DIR="synthetic_image_generation/instant-ngp"

# Run colmap2nerf.py
python "${INSTANT_NGP_DIR}/scripts/colmap2nerf.py" --video_in "${VIDEO_PATH}" \
  --video_fps 8 --run_colmap --aabb_scale 8 --overwrite --output "${DATA_DIR}"

# Train NeRF
python "${INSTANT_NGP_DIR}/scripts/run.py" --scene "${DATA_DIR}" \
  --save_snapshot "${DATA_DIR}/${PRODUCT_NAME}.ingp" --n_steps 20000

echo "Training complete. Snapshot saved at ${DATA_DIR}/${PRODUCT_NAME}.ingp"
