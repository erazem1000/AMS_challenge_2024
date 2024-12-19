import h5py
import SimpleITK as sitk
import numpy as np

def hdf5_to_nii(hdf5_file, dataset_name, reference_image_path, output_file):
    try:
        # Load HDF5 file
        print("Loading HDF5 file...")
        with h5py.File(hdf5_file, "r") as f:
            if dataset_name not in f:
                print(f"Dataset '{dataset_name}' not found in HDF5 file.")
                return
            
            # Load dataset into a numpy array
            data = f[dataset_name][()]

        # Load reference image
        print("Loading reference NIfTI image...")
        reference_image = sitk.ReadImage(reference_image_path)

        # Convert numpy array to SimpleITK image
        print("Converting to SimpleITK image...")
        sitk_image = sitk.GetImageFromArray(data)
        sitk_image.CopyInformation(reference_image)

        # Save to NIfTI
        print(f"Saving NIfTI file to {output_file}...")
        sitk.WriteImage(sitk_image, output_file)
        print("Conversion successful!")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    hdf5_file = input("Enter path to HDF5 file: ").strip()
    dataset_name = input("Enter dataset name inside HDF5 file: ").strip()
    reference_image_path = input("Enter path to reference NIfTI image: ").strip()
    output_file = input("Enter output NIfTI file path: ").strip()

    hdf5_to_nii(hdf5_file, dataset_name, reference_image_path, output_file)