import SimpleITK as sitk
import numpy as np
import os

def transform_hdf5_to_nii(hdf5_path, reference_image_path, output_path):
    """
    Load an HDF5 transformation file and save it as a NIfTI (.nii.gz) displacement field.

    Args:
        hdf5_path (str): Path to the HDF5 transformation file.
        reference_image_path (str): Path to the reference NIfTI image.
        output_path (str): Path to save the output NIfTI displacement field.
    """
    try:
        # Load the reference image
        print("\nLoading the reference image...")
        reference_image = sitk.ReadImage(reference_image_path)

        # Load the transformation from HDF5
        print("Loading the transformation from HDF5...")
        transform = sitk.ReadTransform(hdf5_path)

        # Generate a displacement field from the transformation
        print("Generating displacement field...")
        displacement_field = sitk.TransformToDisplacementField(
            transform, 
            sitk.sitkVectorFloat64,
            reference_image.GetSize(),
            reference_image.GetOrigin(),
            reference_image.GetSpacing(),
            reference_image.GetDirection()
        )

        # Ensure the correct shape for the displacement field
        displacement_field_np = sitk.GetArrayFromImage(displacement_field)

        if displacement_field_np.shape[-1] != 3:
            print("Adjusting displacement field to correct shape...")
            fixed_field = np.zeros((*displacement_field_np.shape[:-1], 3), dtype=np.float64)
            fixed_field[..., :displacement_field_np.shape[-1]] = displacement_field_np

            # Save corrected displacement field
            displacement_field = sitk.GetImageFromArray(fixed_field, isVector=True)
            displacement_field.CopyInformation(reference_image)

        # Save the displacement field as NIfTI
        print(f"Saving the displacement field to: {output_path}")
        sitk.WriteImage(displacement_field, output_path)

        print("\nTransformation successfully saved as NIfTI.")
    except Exception as e:
        print(f"Error occurred: {e}")

def main():
    print("Interactive HDF5 to NIfTI Conversion Tool")

    # Prompt user for inputs
    hdf5_path = input("Enter the path to the HDF5 transformation file: ").strip()
    reference_image_path = input("Enter the path to the reference NIfTI image: ").strip()
    output_path = input("Enter the path to save the output NIfTI file: ").strip()

    # Validate paths
    if not os.path.exists(hdf5_path):
        print(f"Error: HDF5 file not found at '{hdf5_path}'")
        return
    if not os.path.exists(reference_image_path):
        print(f"Error: Reference image file not found at '{reference_image_path}'")
        return

    # Run transformation
    transform_hdf5_to_nii(hdf5_path, reference_image_path, output_path)

if __name__ == "__main__":
    main()