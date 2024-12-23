import json
import numpy as np

def generate_synthetic_transforms(output_path, original_transforms_path, crop_box, num_azimuths=72, num_elevations=18):
    """
    Generates a synthetic transforms.json file based on the manually defined crop box.

    Parameters:
    - output_path: Path to save the synthetic transforms.json file.
    - original_transforms_path: Path to the original transforms.json file from colmap2nerf.py.
    - crop_box: Dictionary with the crop box dimensions (min_x, max_x, min_y, max_y, min_z, max_z).
    - num_azimuths: Number of azimuth angles around the object.
    - num_elevations: Number of elevation angles to cover the upper hemisphere.
    """
    # Load the original transforms.json to extract camera parameters
    with open(original_transforms_path, 'r') as f:
        original_transforms = json.load(f)
    
    camera_angle_x = original_transforms["camera_angle_x"]
    camera_angle_y = original_transforms["camera_angle_y"]
    fl_x = original_transforms.get("fl_x", 0)
    fl_y = original_transforms.get("fl_y", 0)
    cx = original_transforms.get("cx", 0)
    cy = original_transforms.get("cy", 0)
    k1 = original_transforms.get("k1", 0)
    k2 = original_transforms.get("k2", 0)
    k3 = original_transforms.get("k3", 0)
    k4 = original_transforms.get("k4", 0)
    p1 = original_transforms.get("p1", 0)
    p2 = original_transforms.get("p2", 0)
    is_fisheye = original_transforms.get("is_fisheye", False)
    width = original_transforms["w"]/2
    height = original_transforms["h"]/2
    aabb_scale = original_transforms.get("aabb_scale", 1) 

    # Compute the center and radius of the crop box
    center_x = (crop_box["min_x"] + crop_box["max_x"]) / 2
    center_y = (crop_box["min_y"] + crop_box["max_y"]) / 2
    center_z = (crop_box["min_z"] + crop_box["max_z"]) / 2
    radius_x = (crop_box["max_x"] - crop_box["min_x"]) / 2 * 1.5 
    radius_y = (crop_box["max_y"] - crop_box["min_y"]) / 2 * 1.5
    radius_z = (crop_box["max_z"] - crop_box["min_z"]) / 2 * 1.5

    frames = []

    # Define a grid of azimuth and elevation angles for full spherical coverage
    azimuths = np.linspace(0, 2 * np.pi, num=num_azimuths)
    elevations = np.linspace(-np.pi / 8, np.pi / 8, num=num_elevations)  # Limited to the upper hemisphere

    for az in azimuths:
        for el in elevations:
            # Compute the camera position in spherical coordinates, centered on the crop box
            x = center_x + radius_x * np.cos(el) * np.cos(az)
            y = center_y + radius_y * np.sin(el)  
            z = center_z + radius_z * np.cos(el) * np.sin(az)

            # Camera position and forward vector (pointing from camera to origin)
            camera_position = np.array([x, y, z])
            forward = np.array([center_x, center_y, center_z]) - camera_position
            forward = forward / np.linalg.norm(forward)

            # "Up" direction in world coordinates
            up = np.array([0, 1, 0])
            if np.abs(np.dot(forward, up)) > 0.99:  # Avoid near-parallel vectors
                up = np.array([1, 0, 0])
            
            # Right and orthogonal up vectors
            right = np.cross(up, forward)
            right = right / np.linalg.norm(right)  # Normalize
            up = np.cross(forward, right)  # Recompute up to ensure orthogonality

            # Construct the camera transformation matrix
            pose = np.eye(4)
            pose[:3, 0] = right
            pose[:3, 1] = up
            pose[:3, 2] = forward
            pose[:3, 3] = camera_position

            # Add the frame to the list
            frames.append({
                "file_path": f"./{len(frames):04d}.jpg",
                "transform_matrix": pose.tolist(),
                "transform_matrix_start": pose.tolist()
            })

    # Create the synthetic transforms dictionary
    synthetic_transforms = {
        "camera_angle_x": camera_angle_x,
        "camera_angle_y": camera_angle_y,
        "fl_x": fl_x,
        "fl_y": fl_y,
        "cx": cx,
        "cy": cy,
        "k1": k1,
        "k2": k2,
        "k3": k3,
        "k4": k4,
        "p1": p1,
        "p2": p2,
        "is_fisheye": is_fisheye,
        "w": width,
        "h": height,
        "aabb_scale": aabb_scale,
        "frames": frames
    }

    # Save to a JSON file
    with open(output_path, 'w') as f:
        json.dump(synthetic_transforms, f, indent=4)
        
crop_box = {
    "min_x": 0.277,
    "min_y": 0.097,
    "min_z": 0.346,
    "max_x": 0.639,
    "max_y": 1.002,
    "max_z": 0.870
}        

PRODUCT = "hydro_flask"
input_dir = f"data/masked_{PRODUCT}/transforms.json"
output_dir = f"data/masked_{PRODUCT}/synthetic_transforms.json"

# Generate the synthetic transforms file
generate_synthetic_transforms(output_dir, input_dir, crop_box)
