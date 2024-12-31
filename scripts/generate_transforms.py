import json
import numpy as np

def create_transform_matrix(look_at, view_dir, up_dir, scale):
    # Normalize view direction
    forward = -np.array(view_dir)
    forward /= np.linalg.norm(forward)

    # Calculate right and up vectors
    right = np.cross(up_dir, forward)
    right /= np.linalg.norm(right)
    up = np.cross(forward, right)

    # Camera position
    position = np.array(look_at) - scale * forward

    # Create transform matrix
    transform_matrix = np.eye(4)
    transform_matrix[0:3, 0] = right
    transform_matrix[0:3, 1] = up
    transform_matrix[0:3, 2] = forward
    transform_matrix[0:3, 3] = position
    return transform_matrix

def generate_transforms(product_name):
    # Load the original transforms.json
    with open(f"../synthetic_image_generation/data/{product_name}/transforms.json", "r") as f:
        original_data = json.load(f)    

    # Extract shared metadata
    shared_metadata = {
        "camera_angle_x": original_data.get("camera_angle_x", 0),
        "camera_angle_y": original_data.get("camera_angle_y", 0),
        "fl_x": original_data.get("fl_x", 0),
        "fl_y": original_data.get("fl_y", 0),
        "k1": original_data.get("k1", 0),
        "k2": original_data.get("k2", 0),
        "k3": original_data.get("k3", 0),
        "k4": original_data.get("k4", 0),
        "p1": original_data.get("p1", 0),
        "p2": original_data.get("p2", 0),
        "is_fisheye": original_data.get("is_fisheye", False),
        "cx": original_data.get("cx", 0),
        "cy": original_data.get("cy", 0),
        "w": original_data.get("w", 800),  # Default resolution if not available
        "h": original_data.get("h", 800),
        "aabb_scale": original_data.get("aabb_scale", 1),
    }

    # Define camera configurations for new views
    configurations = [
        {
            "name": "front",
            "look_at": [0.5, 0.5, 0.5],
            "view_dir": [0.894, 0.219, -0.390],
            "up_dir": [0.236, 0.972, 0.000],
            "scale": 1.364
        },
        {
            "name": "top",
            "look_at": [0.5, 0.5, 0.5],
            "view_dir": [0.229, -0.950, -0.210],
            "up_dir": [0.236, 0.972, 0.000],
            "scale": 1.364
        },
        {
            "name": "back",
            "look_at": [0.5, 0.5, 0.5],
            "view_dir": [-0.810, -0.437, 0.391],
            "up_dir": [0.236, 0.972, 0.000],
            "scale": 1.364
        },
        {
            "name": "bottom",
            "look_at": [0.5, 0.5, 0.5],
            "view_dir": [-0.171, 0.959, 0.225],
            "up_dir": [0.236, 0.972, 0.000],
            "scale": 1.364
        }
    ]

    # Create frames for the new transforms
    frames = []
    for config in configurations:
        matrix = create_transform_matrix(
            config["look_at"],
            config["view_dir"],
            config["up_dir"],
            config["scale"]
        )
        frame = {
            "file_path": f"./{config['name']}",
            "transform_matrix": matrix.tolist()
        }
        frames.append(frame)

    # Combine metadata and frames
    new_transforms = {**shared_metadata, "frames": frames}

    # Save the new transforms.json
    with open(f"../synthetic_image_generation/data/{product_name}/synthetic_transforms.json", "w") as f:
        json.dump(new_transforms, f, indent=2)

    print(f"New transforms.json created")

if __name__ == "__main__":
    import sys
    product_name = sys.argv[1]
    generate_transforms(product_name)