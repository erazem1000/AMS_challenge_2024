from pathlib import Path
import nibabel as nib
import numpy as np

# Input and output directories
root_path = "output/reshaped"
output_path = "output/reshaped_validation"

# Ensure the output directory exists
output_dir = Path(output_path)
output_dir.mkdir(exist_ok=True)

# Process each .nii.gz file in the input directory
root_dir = Path(root_path)
file_paths = list(root_dir.glob("*.nii.gz"))

for file_path in file_paths:
    try:
        # Load the NIfTI file
        nii_img = nib.load(file_path.as_posix())
        
        # Get the shape of the data
        data_shape = nii_img.shape
        print(f"\nProcessing file: {file_path}")
        print(f"Shape of the above NIfTI file: {data_shape}")
        
        # Get the data array
        data = nii_img.get_fdata()

        # Check and fix the shape if necessary
        if len(data_shape) == 5 and data_shape[3] == 1:  # Check for extra dimension
            data_reshaped = np.squeeze(data, axis=3)  # Remove the singleton dimension
            reshaped_file_path = output_dir / file_path.name
            
            # Save the reshaped file
            new_img = nib.Nifti1Image(data_reshaped, nii_img.affine, nii_img.header)
            nib.save(new_img, reshaped_file_path)
            print(f"Fixed NIfTI shape and saved to: {reshaped_file_path}")
        else:
            print(f"No need to fix shape for: {file_path}")
    except FileNotFoundError:
        print(f"\nError: File not found at '{file_path}'. Please check the path and try again.")
    except Exception as e:
        print(f"\nError processing file '{file_path}': {e}")