import h5py

def inspect_hdf5_file(hdf5_file):
    try:
        with h5py.File(hdf5_file, "r") as f:
            print("Keys in the HDF5 file:")
            for key in f.keys():
                print(f" - {key}: Type = {type(f[key])}")
    except Exception as e:
        print(f"Error: {e}")

def inspect_group_recursive(hdf5_file, group_name):
    try:
        with h5py.File(hdf5_file, "r") as f:
            if group_name in f:
                def print_group_contents(name, obj):
                    obj_type = "Group" if isinstance(obj, h5py.Group) else "Dataset"
                    print(f"{name}: Type = {obj_type}")
                f[group_name].visititems(print_group_contents)
            else:
                print(f"Group '{group_name}' not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    hdf5_file = input("Enter path to HDF5 file: ").strip()
    inspect_hdf5_file(hdf5_file)
    inspect_group_recursive(hdf5_file, "TransformGroup")