import argparse
import os
import numpy as np
import nrrd
import h5py
import SimpleITK as sitk
import matplotlib.pyplot as plt
from scipy.ndimage import distance_transform_edt
from scipy.stats import pearsonr
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

def save_results(results, output_dir="outputs"):
    # Ensuring the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generating a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"results_{timestamp}.json")

    # Saving the results to the .json file
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Results saved to {output_file}")

def load_csv(file_path):
    if file_path:
        return pd.read_csv(file_path, header=None).to_numpy()
    return None
# python post_process.py --fixed=data/RegLib_C01_1.nrrd --warped=outputs/warped_C01_1.nrrd
# Resample function due to size mismatch
def resample_image(image, reference_image):
    """Resample image to match the reference image using SimpleITK."""
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(reference_image)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetOutputSpacing(reference_image.GetSpacing())
    resampler.SetSize(reference_image.GetSize())
    resampler.SetOutputOrigin(reference_image.GetOrigin())
    resampler.SetOutputDirection(reference_image.GetDirection())
    return resampler.Execute(image)

# Loaders for different file types
def load_image(file_path):
    """Load image based on file extension."""
    ext = Path(file_path).suffixes

    if ext == [".nii", ".gz"]:
        img = sitk.ReadImage(file_path)  # Read directly as SimpleITK Image

    elif ext == [".nrrd", ".nhdr"]:
        img, _ = nrrd.read(file_path)
        img = sitk.GetImageFromArray(img)  # Convert to SimpleITK Image
    
    elif ext == [".hdf5"]:
        with h5py.File(file_path, "r") as f:
            if "warped_image" in f:
                img = f["warped_image"][:]
                img = sitk.GetImageFromArray(img)  # Convert to SimpleITK Image
            else:
                raise ValueError("Missing 'warped_image' in HDF5 file.")
    
    else:
        raise ValueError(f"Unsupported file format: {''.join(ext)}")
    
    return img

# Applying Transformation to Keypoints
def apply_transformation(points, transform_file):
    with h5py.File(transform_file, "r") as f:
        for key in f["TransformGroup"].keys():
            transform_type = f["TransformGroup"][key]["TransformType"][()][0].decode()
            print(f"Processing TransformType: {transform_type}")

            if transform_type == "CenteredAffineTransform_double_3_3":
                # Handle affine transforms (already implemented)
                transform_params = np.array(f[f"TransformGroup/{key}/TransformParameters"][:])
                print(f"Transform Parameters Length: {len(transform_params)}")

                if len(transform_params) == 15:  # Handle center of rotation
                    affine_matrix = np.reshape(transform_params[:9], (3, 3))
                    translation = transform_params[9:12]
                    center = transform_params[12:]
                    points = np.dot(points - center, affine_matrix.T) + center + translation

                elif len(transform_params) == 12:  # Standard affine transformation
                    affine_matrix = np.reshape(transform_params[:9], (3, 3))
                    translation = transform_params[9:]
                    points = np.dot(points, affine_matrix.T) + translation

                else:
                    raise ValueError("Unexpected affine parameter length.")

            elif transform_type == "DisplacementFieldTransform_double_3_3":
                # Handle displacement field
                displacement_field = np.array(f[f"TransformGroup/{key}/TransformParameters"][:])
                field_shape = displacement_field.shape

                print(f"Displacement Field Shape: {field_shape}")
                if len(field_shape) == 1:  # Flattened displacement field
                    # Assuming the field represents a 3D volume and needs reshaping
                    grid_size = int(round(len(displacement_field) ** (1 / 3)))  # Assuming cubic grid
                    displacement_field = displacement_field.reshape((grid_size, grid_size, grid_size, 3))

                for point in points:
                    x, y, z = point.astype(int)
                    displacement = displacement_field[x, y, z]
                    point += displacement

            elif transform_type == "CompositeTransform_double_3_3":
                # Handle composite transforms
                print(f"Composite transform requires sequential handling of sub-transforms.")
                # Add handling for nested transforms if required.

            else:
                raise ValueError(f"Unsupported TransformType: {transform_type}")

    return points

# Evaluation Functions
def compute_tre(points_fixed, points_warped):
    """Compute Target Registration Error (TRE)."""
    distances = np.linalg.norm(points_fixed - points_warped, axis=-1)
    return distances.mean()

def compute_dsc(fixed, warped):
    """Compute Dice Similarity Coefficient (DSC)."""
    fixed_bin = fixed > 0
    warped_bin = warped > 0
    intersection = np.logical_and(fixed_bin, warped_bin).sum()
    union = fixed_bin.sum() + warped_bin.sum()
    return 2 * intersection / union if union > 0 else 0.0

def compute_hd95(fixed, warped):
    """Compute 95th percentile Hausdorff Distance (HD95)."""
    fixed_bin = fixed > 0
    warped_bin = warped > 0
    fixed_dt = distance_transform_edt(~fixed_bin)
    warped_dt = distance_transform_edt(~warped_bin)
    fw_distances = fixed_dt[warped_bin].ravel()
    bw_distances = warped_dt[fixed_bin].ravel()
    hd95 = max(np.percentile(fw_distances, 95), np.percentile(bw_distances, 95))
    return hd95

def compute_intensity_correlation(fixed, warped):
    """Compute Pearson correlation between fixed and warped."""
    fixed_flat = fixed.ravel()
    warped_flat = warped.ravel()
    correlation, _ = pearsonr(fixed_flat, warped_flat)
    return correlation

# Main Evaluation Function
def evaluate(fixed_path, warped_path, transform_file, kp_fixed=None, kp_moving=None, lm_fixed=None, lm_moving=None):
    fixed_image = load_image(fixed_path)
    warped_image = load_image(warped_path)

    # Resampling if needed
    warped_resampled = resample_image(warped_image, fixed_image)

    # Converting to numpy arrays
    fixed_np = sitk.GetArrayFromImage(fixed_image)
    warped_np = sitk.GetArrayFromImage(warped_resampled)


    kp_warped = apply_transformation(kp_moving, transform_file) if kp_moving is not None else None
    lm_warped = apply_transformation(lm_moving, transform_file) if lm_moving is not None else None

    # Computing metrics
    results = {
        "TRE_kp": compute_tre(kp_fixed, kp_warped) if kp_fixed is not None and kp_warped is not None else "N/A",
        "TRE_lm": compute_tre(lm_fixed, lm_warped) if lm_fixed is not None and lm_warped is not None else "N/A",
        "DSC": compute_dsc(fixed_np, warped_np),
        "HD95": compute_hd95(fixed_np, warped_np),
        "Intensity Correlation": compute_intensity_correlation(fixed_np, warped_np),
    }

    print("\nAggregated Results:")
    for key, value in results.items():
        print(f"{key:<20}: {value:.5f}" if value != "N/A" else f"{key:<20}: N/A")

    # Saving thee results
    save_results(results)

    # Visualization
    slice_idx = fixed_np.shape[0] // 2
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(fixed_np[slice_idx], cmap="gray")
    axes[0].set_title("Fixed Image")
    axes[1].imshow(warped_np[slice_idx], cmap="gray")
    axes[1].set_title("Warped Image")
    # Difference image with colorbar
    im = axes[2].imshow(np.abs(fixed_np[slice_idx] - warped_np[slice_idx]), cmap="hot")
    axes[2].set_title("Difference (Fixed - Warped)")
    cbar = fig.colorbar(im, ax=axes[2], orientation="vertical", shrink=0.8)
    cbar.set_label("Difference Intensity", rotation=270, labelpad=15)
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate registration metrics.")
    parser.add_argument("--fixed", required=True, help="Path to the fixed image (.nrrd, .nii, .hdf5).")
    parser.add_argument("--warped", required=True, help="Path to the warped image (.nrrd, .nii, .hdf5).")
    
    # Optional keypoints and landmarks
    parser.add_argument("--kp_fixed", help="Path to the fixed keypoints file.")
    parser.add_argument("--kp_moving", help="Path to the moving keypoints file.")
    parser.add_argument("--lm_fixed", help="Path to the fixed landmarks file.")
    parser.add_argument("--lm_moving", help="Path to the moving landmarks file.")
    parser.add_argument("--transform_file", required=True, help="Path to the transformation file.")
    args = parser.parse_args()

    # Loading opt. keypoints/landmarks
    kp_fixed = load_csv(args.kp_fixed)
    kp_moving = load_csv(args.kp_moving)
    lm_fixed = load_csv(args.lm_fixed)
    lm_moving = load_csv(args.lm_moving)

    evaluate(
        args.fixed, args.warped, args.transform_file, 
        kp_fixed=kp_fixed, kp_moving=kp_moving, 
        lm_fixed=lm_fixed, lm_moving=lm_moving
    )    