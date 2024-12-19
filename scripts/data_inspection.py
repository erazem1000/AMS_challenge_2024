import nibabel as nib

# Prompt the user for the file path
file_path = input("Enter the path to your .nii.gz file: ").strip()

try:
    # Load the NIfTI file
    nii_img = nib.load(file_path)
    
    # Get the shape of the data
    data_shape = nii_img.shape

    print(f"\nShape of the above nifti file: {data_shape}")
except FileNotFoundError:
    print(f"\nError: File not found at '{file_path}'. Please check the path and try again.")
except Exception as e:
    print(f"\nError: {e}")

nii_img.dataobj