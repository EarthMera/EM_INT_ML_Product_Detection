#!/bin/bash

PRODUCT_NAME=$1
DATA_DIR="synthetic_image_generation/data/${PRODUCT_NAME}"
OUTPUT_DIR="${DATA_DIR}/synthetic_images"
TRANSFORMS_PATH="${DATA_DIR}/synthetic_transforms.json"
SNAPSHOT_PATH="${DATA_DIR}/${PRODUCT_NAME}.ingp"
INSTANT_NGP_DIR="synthetic_image_generation/instant-ngp"

python "${INSTANT_NGP_DIR}/scripts/run.py" --load_snapshot "${SNAPSHOT_PATH}" \
  --screenshot_transforms "${TRANSFORMS_PATH}" --screenshot_dir "${OUTPUT_DIR}" \
  --screenshot_spp 16

echo "Synthetic images saved in ${OUTPUT_DIR}."
