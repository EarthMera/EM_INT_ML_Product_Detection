import os
import torch
import torchvision
from torchvision.transforms import functional as F
from torchvision.models.detection import maskrcnn_resnet50_fpn
from PIL import Image
import numpy as np
import cv2
import json

PRODUCT = 'hydro_flask'

def load_model(device):
    """
    Load a pre-trained Mask R-CNN model from Torchvision.
    """
    model = maskrcnn_resnet50_fpn(pretrained=True)
    model.eval()  # Set the model to evaluation mode
    model.to(device)
    return model


def segment_and_mask_images(image_dir, output_dir, model, device, confidence_threshold=0.5):
    """
    Perform segmentation using Mask R-CNN and apply masks to images.

    Parameters:
    - image_dir: Directory containing the input images.
    - output_dir: Directory to save masked images.
    - model: Pre-trained Mask R-CNN model.
    - device: Device to run the model on ('cuda' or 'cpu').
    - confidence_threshold: Minimum confidence score for considering a detection.
    """
    os.makedirs(output_dir, exist_ok=True)

    for image_file in os.listdir(image_dir):
        if not image_file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        image_path = os.path.join(image_dir, image_file)
        image = Image.open(image_path).convert("RGB")

        # Convert the image to a tensor
        image_tensor = F.to_tensor(image).unsqueeze(0).to(device)

        # Perform inference
        with torch.no_grad():
            outputs = model(image_tensor)

        # Filter predictions based on confidence threshold
        masks = outputs[0]["masks"]
        scores = outputs[0]["scores"]
        filtered_masks = [
            masks[i, 0].cpu().numpy() > 0.5
            for i in range(len(scores))
            if scores[i] > confidence_threshold
        ]

        if filtered_masks:
            # Combine all masks into one
            combined_mask = np.any(filtered_masks, axis=0).astype(np.uint8) * 255

            # Apply the mask to the image
            image_np = np.array(image)
            masked_image = cv2.bitwise_and(image_np, image_np, mask=combined_mask)

            # Save the masked image
            output_path = os.path.join(output_dir, image_file)
            cv2.imwrite(output_path, masked_image)
        else:
            print(f"No confident predictions for {image_file}. Skipping...")

    print("Segmentation and masking complete.")


def update_transforms(transforms_path, output_dir, updated_transforms_path):
    """
    Update the transforms.json file to reference the masked images.

    Parameters:
    - transforms_path: Path to the original transforms.json file.
    - output_dir: Directory containing the masked images.
    - updated_transforms_path: Path to save the updated transforms.json.
    """
    with open(transforms_path, "r") as f:
        transforms = json.load(f)

    for frame in transforms["frames"]:
        file_name = os.path.basename(frame["file_path"])
        frame["file_path"] = os.path.join("./images/", file_name)

    with open(updated_transforms_path, "w") as f:
        json.dump(transforms, f, indent=4)

    print("Transforms.json updated successfully.")


if __name__ == "__main__":
    # Paths
    image_dir = f"data/{PRODUCT}/images/"  # Directory containing extracted images
    output_dir = "data/masked_{PRODUCT}/images/"  # Directory to save masked images
    transforms_path = f"data/{PRODUCT}/transforms.json"  # Path to the original transforms.json
    updated_transforms_path = f"data/masked_{PRODUCT}/transforms.json"  # Path to save the updated transforms.json

    # Load the pre-trained model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(device)

    # Perform segmentation and masking
    segment_and_mask_images(image_dir, output_dir, model, device)

    # Update the transforms.json file
    update_transforms(transforms_path, output_dir, updated_transforms_path)
