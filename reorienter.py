import nibabel as nib
import numpy as np
import os

def reorient_mask_to_match_image(image_path, mask_path, output_path=None):
    """
    Reorient a mask to match the orientation of a reference image using nibabel.
    
    Args:
        image_path (str): Path to the reference image
        mask_path (str): Path to the mask that needs reorientation
        output_path (str): Path to save the reoriented mask. If None, will use original path with prefix
    
    Returns:
        str: Path to the reoriented mask
    """
    # Load images
    ref_img = nib.load(image_path)
    mask_img = nib.load(mask_path)
    
    # Print original orientations
    #print("Original image orientation:")
    #print(f"Affine:\n{ref_img.affine}")
    #print(f"\nOriginal mask orientation:")
    #print(f"Affine:\n{mask_img.affine}")


    # Check if affines are already equal (using np.allclose for float comparison)
    if np.allclose(ref_img.affine, mask_img.affine):
        #print("Mask already has the same orientation as the reference image. Skipping reorientation.")
        return mask_path
    
    
    # Get the mask data
    mask_data = mask_img.get_fdata()
    
    # Create new mask image with reference image's affine
    reoriented_mask = nib.Nifti1Image(mask_data, ref_img.affine)
    
    # If no output path specified, create one
    if output_path is None:
        mask_dir = os.path.dirname(mask_path)
        mask_filename = os.path.basename(mask_path)
        output_path = os.path.join(mask_dir, f"reoriented_{mask_filename}")
    
    # Save the reoriented mask
    nib.save(reoriented_mask, output_path)
    
    # Verify the result
    final_mask = nib.load(output_path)
    #print(f"\nReoriented mask orientation:")
    #print(f"Affine:\n{final_mask.affine}")
    
    # Print some statistics to verify data preservation
    #print("\nMask statistics:")
    #print(f"Original unique values: {np.unique(mask_data)}")
    #print(f"Reoriented unique values: {np.unique(final_mask.get_fdata())}")
    subs = mask_data - final_mask.get_fdata()
    if np.max(mask_data) > 0:
        print(f"Arrays Substraction {np.mean(subs)}")
    if np.max(mask_data) > 0:
        print(f"Non zeros mask")
    
    return output_path

# Example usage
if __name__ == "__main__":
    import glob
    main_path = "/home/petermcgor/Documents/Projects/nnUNet2/nnUNet_raw/Dataset301_CL_Multisite/labelsTr/"
    masks = glob.glob(os.path.join(main_path,'*.nii.gz'))
    for mask_path in masks:
        print(mask_path)
        image_path = mask_path.replace('labels','images')
        image_path = image_path.replace(".nii.gz","_0000.nii.gz")
    
        reoriented_path = reorient_mask_to_match_image(image_path, mask_path, output_path=mask_path)
        print(f"Reoriented mask saved to: {reoriented_path}")
        print('---')