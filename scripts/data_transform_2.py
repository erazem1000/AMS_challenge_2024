import h5py
import SimpleITK as sitk
from pathlib import Path

# Set the root path
root_path = "output"
root_dir = Path(root_path)

# Create output directory if it doesn't exist
output_dir = root_dir / "reshaped"
output_dir.mkdir(exist_ok=True)

# Reference size, origin, spacing, and direction
size = [256, 192, 192]  # Correct size for the displacement field
spacing = [1.0, 1.0, 1.0]  # Adjust spacing as needed (e.g., real-world units)
origin = [0.0, 0.0, 0.0]  # Set to align with the domain
direction = [1.0, 0.0, 0.0,  # Identity direction matrix (modify if needed)
             0.0, 1.0, 0.0,
             0.0, 0.0, 1.0]

# Process each HDF5 file
for file_path in root_dir.glob("*.hdf5"):
    try:
        print(f"Processing file: {file_path}")

        # Load the transform from the HDF5 file
        transform = sitk.ReadTransform(str(file_path))  # Convert Path to string for compatibility

        # Convert the transform to a displacement field (image)
        displacement_field = sitk.TransformToDisplacementField(
            transform,
            sitk.sitkVectorFloat64,  # Ensures 3D vector type
            size,
            origin,
            spacing,
            direction
        )

        # Print the size of the created displacement field
        print(f"Displacement field size: {displacement_field.GetSize()}")
        print(f"Number of components per pixel: {displacement_field.GetNumberOfComponentsPerPixel()}")

        # Validate displacement field
        if displacement_field.GetSize() != tuple(size):
            raise ValueError(f"Displacement field has wrong size: {displacement_field.GetSize()}")

        if displacement_field.GetNumberOfComponentsPerPixel() != 3:
            raise ValueError("Displacement field must have 3 components per pixel.")

        # Save the displacement field as a NIfTI image
        output_file = output_dir / f"{file_path.stem}.nii.gz"
        sitk.WriteImage(displacement_field, str(output_file))
        print(f"Saved displacement field: {output_file}")

    except FileNotFoundError:
        print(f"\nError: File not found at '{file_path}'. Please check the path and try again.")
    except Exception as e:
        print(f"\nError processing '{file_path}': {e}")