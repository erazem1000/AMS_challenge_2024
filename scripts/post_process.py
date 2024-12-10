import argparse
import os
import numpy as np
import nrrd
import h5py
import SimpleITK as sitk
import matplotlib.pyplot as plt
from scipy.ndimage import distance_transform_edt
from scipy.stats import pearsonr

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
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".nrrd", ".nhdr"]:
        img, _ = nrrd.read(file_path)
        img = sitk.GetImageFromArray(img)  # Convert to SimpleITK Image
    
    elif ext in [".nii", ".nii.gz"]:
        img = sitk.ReadImage(file_path)  # Read directly as SimpleITK Image
    
    elif ext == ".hdf5":
        with h5py.File(file_path, "r") as f:
            if "warped_image" in f:
                img = f["warped_image"][:]
                img = sitk.GetImageFromArray(img)  # Convert to SimpleITK Image
            else:
                raise ValueError("Missing 'warped_image' in HDF5 file.")
    
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    
    return img

# Evaluation Functions

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
def evaluate(fixed_path, warped_path):
    fixed_image = load_image(fixed_path)
    warped_image = load_image(warped_path)

    # Resample warped image to match fixed image
    warped_resampled = resample_image(warped_image, fixed_image)

    # Convert to numpy arrays for evaluation
    fixed_np = sitk.GetArrayFromImage(fixed_image)
    warped_np = sitk.GetArrayFromImage(warped_resampled)

    # Metrics
    dsc = compute_dsc(fixed_np, warped_np)
    hd95 = compute_hd95(fixed_np, warped_np)
    correlation = compute_intensity_correlation(fixed_np, warped_np)

    print("\nAggregated Results:")
    print(f"DSC                 : {dsc:.5f}")
    print(f"HD95                : {hd95:.5f}")
    print(f"Intensity Correlation: {correlation:.5f}")

    # Visualization
    slice_idx = fixed_np.shape[0] // 2
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(fixed_np[slice_idx], cmap="gray")
    axes[0].set_title("Fixed Image")
    axes[1].imshow(warped_np[slice_idx], cmap="gray")
    axes[1].set_title("Warped Image")
    axes[2].imshow(np.abs(fixed_np[slice_idx] - warped_np[slice_idx]), cmap="hot")
    axes[2].set_title("Difference (Fixed - Warped)")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate registration metrics.")
    parser.add_argument("--fixed", required=True, help="Path to the fixed image (.nrrd, .nii, .hdf5).")
    parser.add_argument("--warped", required=True, help="Path to the warped image (.nrrd, .nii, .hdf5).")
    args = parser.parse_args()

    evaluate(args.fixed, args.warped)