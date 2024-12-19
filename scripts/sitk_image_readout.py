import SimpleITK as sitk

input_image = sitk.ReadImage("input_image.nii.gz")
displacement_field = sitk.TransformToDisplacementField(
    input_image,
    sitk.sitkVectorFloat64,
    input_image.GetSize(),
    input_image.GetOrigin(),
    input_image.GetSpacing(),
    input_image.GetDirection()
)