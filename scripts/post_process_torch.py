import argparse
import os
import numpy as np
import nrrd
import h5py
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
from scipy.ndimage import distance_transform_edt
from scipy.stats import pearsonr

# Loaders for Different File Types
def load_image(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".nrrd", ".nhdr"]:
        img, _ = nrrd.read(file_path)
        return torch.Tensor(img).unsqueeze(0).unsqueeze(0)
    elif ext in [".nii", ".nii.gz"]:
        img = sitk.GetArrayFromImage(sitk.ReadImage(file_path))
        return torch.Tensor(img).unsqueeze(0).unsqueeze(0)
    elif ext == ".hdf5":
        with h5py.File(file_path, "r") as f:
            img = f["warped_image"][:]
        return torch.Tensor(img).unsqueeze(0).unsqueeze(0)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

# Preprocessing Function
def preprocess(img, img_type="mri"):
    if img_type == "ct":
        clamp = [-1000, 1000]
        img = (torch.clamp(img, clamp[0], clamp[1]) - clamp[0]) / (clamp[1] - clamp[0])
    elif img_type == "mri":
        im_min, im_max = torch.min(img), torch.quantile(img, 0.99)
        img = torch.clip(img, im_min, im_max)
        img = (img - im_min) / (im_max - im_min)
    else:
        raise ValueError(f"Unsupported image type: {img_type}")
    return F.interpolate(img, [175, 175, 175], mode="trilinear", align_corners=False)

# Evaluation Functions
def compute_dsc(fixed, warped):
    fixed_bin = fixed > 0
    warped_bin = warped > 0
    intersection = torch.logical_and(fixed_bin, warped_bin).sum().item()
    union = fixed_bin.sum().item() + warped_bin.sum().item()
    return 2 * intersection / union if union > 0 else 0.0

def compute_hd95(fixed, warped):
    fixed_bin = fixed > 0
    warped_bin = warped > 0
    fw_distances = distance_transform_edt(~fixed_bin.numpy())[warped_bin.numpy()].ravel()
    bw_distances = distance_transform_edt(~warped_bin.numpy())[fixed_bin.numpy()].ravel()
    hd95 = max(np.percentile(fw_distances, 95), np.percentile(bw_distances, 95))
    return hd95

def compute_intensity_correlation(fixed, warped):
    fixed_flat = fixed.view(-1)
    warped_flat = warped.view(-1)
    correlation, _ = pearsonr(fixed_flat.numpy(), warped_flat.numpy())
    return correlation

# Main Evaluation Function
def evaluate(fixed_path, warped_path):
    fixed_image = load_image(fixed_path)
    warped_image = load_image(warped_path)

    # Resample using PyTorch
    fixed_resampled = preprocess(fixed_image, "mri")
    warped_resampled = preprocess(warped_image, "mri")

    # Metrics
    dsc = compute_dsc(fixed_resampled, warped_resampled)
    hd95 = compute_hd95(fixed_resampled, warped_resampled)
    correlation = compute_intensity_correlation(fixed_resampled, warped_resampled)

    print("\nAggregated Results:")
    print(f"DSC                 : {dsc:.5f}")
    print(f"HD95                : {hd95:.5f}")
    print(f"Intensity Correlation: {correlation:.5f}")

    # Visualization
    slice_idx = fixed_resampled.shape[2] // 2
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(fixed_resampled[0, 0, slice_idx].numpy(), cmap="gray")
    axes[0].set_title("Fixed Image")
    axes[1].imshow(warped_resampled[0, 0, slice_idx].numpy(), cmap="gray")
    axes[1].set_title("Warped Image")
    axes[2].imshow(
        torch.abs(fixed_resampled[0, 0, slice_idx] - warped_resampled[0, 0, slice_idx]).numpy(),
        cmap="hot",
    )
    axes[2].set_title("Difference (Fixed - Warped)")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate registration metrics.")
    parser.add_argument("--fixed", required=True, help="Path to the fixed image (.nrrd, .nii, .hdf5).")
    parser.add_argument("--warped", required=True, help="Path to the warped image (.nrrd, .nii, .hdf5).")
    args = parser.parse_args()

    evaluate(args.fixed, args.warped)