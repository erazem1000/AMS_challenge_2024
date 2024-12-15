#!/bin/bash

# Print the current working directory
echo "Current working directory is: $(pwd)"
echo "Make sure your input and output paths are relative to this directory!"

# Activate virtual environment
source /usr/src/app/venv/bin/activate

echo "Pozdravljen! Prosim podaj poti do slik za poravnavo."

# Prompt for input interactively
read -p "Enter the path to the fixed image: " FIXED_IMAGE
read -p "Enter the path to the moving image: " MOVING_IMAGE
read -p "Enter the fixed modality (ct or mri): " FIXED_MODALITY
read -p "Enter the moving modality (ct or mri): " MOVING_MODALITY
read -p "Enter the number of iterations: " ITERATIONS

# Confirm and run
echo "You entered:"
echo "  Fixed Image: $FIXED_IMAGE"
echo "  Fixed Modality: $FIXED_MODALITY"
echo "  Moving Image: $MOVING_IMAGE"
echo "  Moving Modality: $MOVING_MODALITY"
echo "  Number of Iterations: $ITERATIONS"

# Ask for confirmation
read -p "Proceed with these images? (Y/n) " CONFIRM
if [[ "$CONFIRM" != "n" && "$CONFIRM" != "N" ]]; then

  echo "Running: unigradicon-register --fixed \"$FIXED_IMAGE\" --moving \"$MOVING_IMAGE\" --fixed_modality \"$FIXED_MODALITY\" --moving_modality \"$MOVING_MODALITY\" --transform_out output/0011_0001_trans.hdf5 --warped_moving_out output/warped_image_Docker.nii.gz --io_iterations \"$ITERATIONS\""

  # Perform the registration
  if unigradicon-register \
    --fixed "$FIXED_IMAGE" \
    --moving "$MOVING_IMAGE" \
    --fixed_modality "$FIXED_MODALITY" \
    --moving_modality "$MOVING_MODALITY" \
    --transform_out output/0011_0001_trans.hdf5 \
    --warped_moving_out output/warped_image_Docker.nii.gz \
    --io_iterations "$ITERATIONS"; then
    
    # Ask if post-processing should be run
    echo "Registration completed. Do you want to run post-process? (Y/n)"
    read -r RESPONSE
  else
    echo "Registration failed. Check resources or input files." >&2
    exit 1
  fi 

  if [[ "$RESPONSE" =~ ^[Yy]$ ]] || [[ -z "$RESPONSE" ]]; then
    if [[ -f output/0011_0001_trans.hdf5 ]]; then
      python scripts/post_process.py \
        --fixed "$FIXED_IMAGE" \
        --warped output/warped_image_Docker.nii.gz \
        --transform_file output/0011_0001_trans.hdf5
    else
      echo "Error: Transform file 'output/0011_0001_trans.hdf5' not found. Post-processing cannot proceed." >&2
      exit 1
    fi
  else
    echo "Post-process skipped."
  fi

fi