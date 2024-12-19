#!/bin/bash

# Print the current working directory
echo "Current working directory is: $(pwd)"
echo "Make sure your input and output paths are relative to this directory!"

# Activate virtual environment
source /usr/src/app/venv/bin/activate || {
    echo "Error: Failed to activate virtual environment." >&2
    exit 1
}

echo "Pozdravljen! Prosim podaj poti do slik za poravnavo."

# Prompt for input interactively
read -p "Enter the path to the fixed image (e.g., input/fixed_image.nii.gz): " FIXED_IMAGE
read -p "Enter the path to the moving image (e.g., input/moving_image.nii.gz): " MOVING_IMAGE
read -p "Enter the fixed modality (ct or mri): " FIXED_MODALITY
read -p "Enter the moving modality (ct or mri): " MOVING_MODALITY
read -p "Enter the number of iterations (e.g., 100): " ITERATIONS
read -p "Enter the transformation output name (e.g., output/disp_fixed_moving.hdf5): " TRANSFORM_OUT
read -p "Enter the warped output name (e.g., output/warped_fixed_moving.nii.gz): " WARPED_OUT

# Confirm inputs
echo -e "\nYou entered:"
echo "  Fixed Image: $FIXED_IMAGE"
echo "  Fixed Modality: $FIXED_MODALITY"
echo "  Moving Image: $MOVING_IMAGE"
echo "  Moving Modality: $MOVING_MODALITY"
echo "  Number of Iterations: $ITERATIONS"
echo "  Transformation Output: $TRANSFORM_OUT"
echo "  Warped Output: $WARPED_OUT"

read -p "Proceed with these settings? (Y/n) " CONFIRM
if [[ "$CONFIRM" =~ ^[Nn]$ ]]; then
    echo "Operation cancelled by user."
    exit 0
fi

# Run the registration
echo "Running registration..."
if unigradicon-register \
    --fixed "$FIXED_IMAGE" \
    --moving "$MOVING_IMAGE" \
    --fixed_modality "$FIXED_MODALITY" \
    --moving_modality "$MOVING_MODALITY" \
    --transform_out "$TRANSFORM_OUT" \
    --warped_moving_out "$WARPED_OUT" \
    --io_iterations "$ITERATIONS"; then
    echo "Registration completed successfully."
else
    echo "Registration failed. Check resources or input files." >&2
    exit 1
fi

# Post-process prompt
read -p "Do you want to run post-processing? (Y/n) " RESPONSE
if [[ "$RESPONSE" =~ ^[Yy]$ ]] || [[ -z "$RESPONSE" ]]; then
    if [[ -f "$TRANSFORM_OUT" ]]; then
        python scripts/post_process.py \
            --fixed "$FIXED_IMAGE" \
            --warped "$WARPED_OUT" \
            --transform_file "$TRANSFORM_OUT"
        echo "Post-processing completed."
    else
        echo "Error: Transform file '$TRANSFORM_OUT' not found. Post-processing skipped." >&2
    fi
else
    echo "Post-processing skipped."
fi

# Data Transformation Prompt
read -p "Do you want to convert transformation fields from .hdf5 to .nii.gz? (Y/n) " RESPONSE
if [[ "$RESPONSE" =~ ^[Yy]$ ]] || [[ -z "$RESPONSE" ]]; then
    python scripts/data_transform_2.py || {
        echo "Error: Data transformation failed." >&2
        exit 1
    }
    echo "Data transformation to .nii.gz completed."
else
    echo "Data transformation to .nii.gz skipped."
fi

# Data reshaping prompt
read -p "Do you want to reshape the transformation for validation method? (Y/n) " RESPONSE
if [[ "$RESPONSE" =~ ^[Yy]$ ]] || [[ -z "$RESPONSE" ]]; then
    python scripts/data_reshape_2.py || {
        echo "Error: Data reshape failed." >&2
        exit 1
    }
    echo "Data reshape completed."
else
    echo "Data reshape skipped."
fi
echo "All processes completed successfully!"
exit 0




# # Validation prompt
# echo -e "\n*.nii.gz files are required for validation. Use scripts/data_transform.py to prepare the datasets."
# read -p "Proceed with validation? (Y/n) " CONFIRM_VALIDATION
# if [[ "$CONFIRM_VALIDATION" =~ ^[Yy]$ ]]; then
#     echo "Starting validation container..."
#     docker run \
#         --rm \
#         -u "$(id -u):$(id -g)" \
#         -v "$(pwd)/input:/input" \
#         -v "$(pwd)/output:/output" \
#         gitlab.lst.fe.uni-lj.si:5050/domenp/deformable-registration \
#         python evaluation.py -v

#     if [[ $? -eq 0 ]]; then
#         echo "Validation process completed successfully."
#     else
#         echo "Validation process encountered errors." >&2
#     fi
# else
#     echo "Validation skipped."
# fi

# echo "Script completed successfully."