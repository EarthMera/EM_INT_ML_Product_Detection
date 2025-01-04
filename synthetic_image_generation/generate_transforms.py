import json
import numpy as np

def load_transforms(file_path):
    """Load the original transforms.json."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def perturb_pose(pose, translation_range, rotation_range):
    """Apply perturbation to a pose matrix."""
    translation = np.random.uniform(-translation_range, translation_range, 3)
    rotation_angle = np.random.uniform(-rotation_range, rotation_range)
    rotation_matrix = np.array([
        [np.cos(rotation_angle), -np.sin(rotation_angle), 0],
        [np.sin(rotation_angle), np.cos(rotation_angle), 0],
        [0, 0, 1]
    ])
    perturbed_pose = pose.copy()
    perturbed_pose[:3, :3] = np.dot(rotation_matrix, perturbed_pose[:3, :3])
    perturbed_pose[:3, 3] += translation
    return perturbed_pose

def generate_synthetic_transforms(input_path, output_path, num_new_views=50):
    """Generate synthetic camera transforms."""
    data = load_transforms(input_path)
    original_poses = [np.array(frame["transform_matrix"]) for frame in data["frames"]]

    new_frames = []
    for i in range(num_new_views):
        base_pose = original_poses[i % len(original_poses)]
        new_pose = perturb_pose(base_pose, translation_range=0.1, rotation_range=0.05)
        new_frames.append({
            "transform_matrix_start": new_pose.tolist(),
            "file_path": f"synthetic_view_{i}.png"
        })

    synthetic_data = {
        "camera_angle_x": data["camera_angle_x"],
        "camera_angle_y": data["camera_angle_y"],
        "fl_x": data["fl_x"],
        "fl_y": data["fl_y"],
        "k1": data["k1"],
        "k2": data["k2"],
        "k3": data["k3"],
        "k4": data["k4"],
        "p1": data["p1"],
        "p2": data["p2"],
        "is_fisheye": data["is_fisheye"],
        "cx": data["cx"],
        "cy": data["cy"],
        "w": data["w"],
        "h": data["h"],
        "aabb_scale": data["aabb_scale"],
        "frames": new_frames
    }
    with open(output_path, 'w') as file:
        json.dump(synthetic_data, file, indent=4)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic transforms.")
    parser.add_argument("--input_path", type=str, help="Path to original transforms.json")
    parser.add_argument("--output_path", type=str, help="Path to save synthetic transforms.json")
    args = parser.parse_args()

    generate_synthetic_transforms(args.input_path, args.output_path)
