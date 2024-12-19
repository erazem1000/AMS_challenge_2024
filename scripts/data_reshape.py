from pathlib import Path
import nibabel as nib
import numpy as np

# Prompt the user for the file path
# file_path = input("Enter the path to your .nii.gz file: ").strip()
# file_path= "input/disp_0012_0001_0012_0000.nii.gz"
root_path = "output/reshaped"

root_dir = Path(root_path)

file_paths = [file for file in root_dir.glob("*.nii.gz")]

for file_path in file_paths:
    try:
        # Load the NIfTI file
        nii_img = nib.load(file_path.as_posix())
        
        # Get the shape of the data
        data_shape = nii_img.shape

        print(f"\nShape of the above nifti file: {data_shape}")

        # Load the NIfTI file
        nii_img = nib.load(file_path)
        nii_array = nii_img.dataobj
        nii_array = nii_array[np.newaxis, ...]
        array_img = nib.Nifti1Image(nii_array, nii_img.affine)

        print(file_path)

        new_file_path = f"./reshaped/{file_path.name}"

        print(new_file_path)
        array_img.to_filename(new_file_path)

    except FileNotFoundError:
        print(f"\nError: File not found at '{file_path}'. Please check the path and try again.")
    except Exception as e:
        print(f"\nError: {e}")
