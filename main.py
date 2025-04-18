import os
import subprocess
import sys
from typing import Tuple
from src.scripts.radiometric_correction import apply_correction_to_all_images

def setup_environment():
    """Ensure that the virtual environment is set up and dependencies are installed."""
    setup_script_path = os.path.join(os.getcwd(), "src", "scripts", "setup_env.py")
    
    # Run the setup_env.py script
    result = subprocess.run([sys.executable, setup_script_path], capture_output=True, text=True)
    
    # Check the result
    if result.returncode != 0:
        print("Error setting up the environment:\n", result.stderr)
        sys.exit(1)
    
    print("Environment setup successfully")

def check_image_dimensions(data_folder: str) -> None:
    """Check if all images in cam folders are 640x928, and call split_cam_images.py if not."""
    cam_folders = [os.path.join(data_folder, f"cam{i}") for i in range(1, 9)]
    split_needed = False

    for folder in cam_folders:
        print(f"Checking {folder}...")
        print("Exists:", os.path.exists(folder))
        if os.path.exists(folder):
            print(f"Found {folder}")
            split_needed = True
            for file in os.listdir(folder):
                if file.endswith('.png'):
                    dimensions = get_image_dimensions(os.path.join(folder, file))
                    print(dimensions)
                    if dimensions != (640, 928):
                        split_needed = True
                        break
            if split_needed:
                break

    if split_needed:
        print("Images need splitting. Calling split_cam_images.py...")
        subprocess.run([sys.executable, "src/scripts/split_cam_images.py"], check=True)
    else:
        print("All images are already 640x928.")

def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """Get the dimensions of an image."""
    from PIL import Image
    with Image.open(image_path) as img:
        return img.size

def check_csv_files(csv_folder: str) -> None:
    """Check for the presence of CSV files and call detect.py if necessary."""
    required_csv_files = {f"cam{i}.csv" for i in range(1, 9)}

    existing_csv_files = {f for f in os.listdir(csv_folder) if f.endswith(".csv")}
    missing_csv_files = required_csv_files - existing_csv_files

    if missing_csv_files:
        print("CSV files are missing. Running detect.py to calculate radiometric reflectance...")
        subprocess.run([sys.executable, "model/panel/detect.py"], check=True)
    else:
        print("All required CSV files are present. Proceeding with radiometric correction...")
        apply_correction_to_all_images(input_dir='data/images', output_dir='data/corrected_images')  # Update paths accordingly

def main():
    # setup_environment()
    project_root = os.path.dirname(os.path.abspath(__file__))
    # data_folder = os.path.join(project_root, "data/images")
    # check_image_dimensions(data_folder)
    csv_folder = os.path.join(project_root, "panel_detection_output")
    check_csv_files(csv_folder)

if __name__ == "__main__":
    main()