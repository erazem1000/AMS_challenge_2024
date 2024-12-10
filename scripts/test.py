import os
import argparse
import subprocess
from datetime import datetime
import torch
import sys

# Disable CUDA for macOS
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Setup directories
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(script_dir, ".."))

print(f"Python Version: {sys.version}")
print(f"Current Directory: {os.getcwd()}")

def generate_timestamped_filename(base_name, extension):
    """Generate a filename with the current date and time."""
    current_time = datetime.now()
    timestamp = current_time.strftime("%d_%m_%Y_%H_%M")
    return f"{timestamp}_{base_name}{extension}"

def main(fixed, moving, fixed_modality, moving_modality, io_iterations, io_sim):
    # Ensure output directory exists
    os.makedirs(os.path.join(base_dir, "outputs"), exist_ok=True)

    # Generate output filenames
    transform_out = generate_timestamped_filename("trans", ".hdf5")
    warped_out = generate_timestamped_filename("warped_C01_1", ".nrrd")

    # Registration command
    venv_activate = os.path.join(base_dir, "unigradicon_venv/bin/activate")
    registration_command = f"""
    source {venv_activate} && unigradicon-register \
        --fixed={os.path.join(base_dir, 'data', fixed)} \
        --fixed_modality={fixed_modality} \
        --moving={os.path.join(base_dir, 'data', moving)} \
        --moving_modality={moving_modality} \
        --transform_out={os.path.join(base_dir, 'outputs', transform_out)} \
        --warped_moving_out={os.path.join(base_dir, 'outputs', warped_out)} \
        --io_iterations={io_iterations} \
        --io_sim={io_sim}
    """

    print(f"Running registration command: {registration_command}")
    try:
        subprocess.run(registration_command, shell=True, check=True, executable="/bin/bash", env={**os.environ, "CUDA_VISIBLE_DEVICES": "-1"})
        print("Registration completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error during registration: {e}")
        return

    # Post-processing command
    post_process_command = [
        "python", os.path.join(base_dir, "scripts/post_process.py"),
        f"--fixed={os.path.join(base_dir, 'data', fixed)}",
        f"--warped={os.path.join(base_dir, 'outputs', warped_out)}"
    ]

    print(f"Running post-processing command: {' '.join(post_process_command)}")
    try:
        subprocess.run(post_process_command, check=True)
        print("Post-processing completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error during post-processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run unigradicon-register and post-process the results.")
    parser.add_argument("--fixed", required=True, help="Path to the fixed image (.nrrd).")
    parser.add_argument("--moving", required=True, help="Path to the moving image (.nrrd).")
    parser.add_argument("--fixed_modality", required=True, choices=["mri", "ct"], help="Modality of the fixed image (e.g., mri, ct).")
    parser.add_argument("--moving_modality", required=True, choices=["mri", "ct"], help="Modality of the moving image (e.g., mri, ct).")
    parser.add_argument("--io_iterations", type=int, required=True, help="Number of IO iterations.")
    parser.add_argument("--io_sim", required=True, choices=["lncc", "lncc2", "mind"], help="Similarity metric for IO optimization.")
    args = parser.parse_args()

    main(
        fixed=args.fixed,
        moving=args.moving,
        fixed_modality=args.fixed_modality,
        moving_modality=args.moving_modality,
        io_iterations=args.io_iterations,
        io_sim=args.io_sim,
    )