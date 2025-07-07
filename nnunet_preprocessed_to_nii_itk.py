import numpy as np
import SimpleITK as sitk
import pickle
import os
from pathlib import Path

def load_pickle(file_path):
    """Load pickle file containing preprocessing information."""
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def load_array_file(file_path):
    """
    Load array from either .npy or .npz file.
    
    Args:
        file_path (Path): Path to the numpy file
    
    Returns:
        np.ndarray: The loaded array
    """
    if file_path.suffix == '.npy':
        return np.load(file_path)
    elif file_path.suffix == '.npz':
        npz_file = np.load(file_path)
        if 'data' in npz_file.files:
            return npz_file['data']
        else:
            first_key = npz_file.files[0]
            array = npz_file[first_key]
            print(f"Using array with key '{first_key}' from {file_path}")
            return array

def ensure_3d(array):
    """
    Ensure the array is 3D by removing singleton dimensions or selecting first channel.
    
    Args:
        array (np.ndarray): Input array
    
    Returns:
        np.ndarray: 3D array
    """
    # If it's already 3D, return as is
    if array.ndim == 3:
        return array
    
    # If it's 4D with shape (1, D, H, W) or (C, D, H, W)
    if array.ndim == 4:
        if array.shape[0] == 1:
            return array[0]  # Take the only channel
        else:
            print(f"Warning: Found {array.shape[0]} channels, using first channel")
            return array[1]  # Take the second channel
    
    raise ValueError(f"Unexpected array shape: {array.shape}. Expected 3D or 4D array")

def convert_to_nifti_sitk(data_array, properties, output_path, is_segmentation=False):
    """
    Convert numpy array back to NIfTI using original properties with SimpleITK.
    
    Args:
        data_array (np.ndarray): The image data
        properties (dict): Original image properties from pickle file
        output_path (str): Path to save the NIfTI file
        is_segmentation (bool): Whether this is a segmentation mask
    """
    # Ensure data is 3D
    data_array = ensure_3d(data_array)
    
    # If it's a segmentation mask, ensure it's integer type
    if is_segmentation:
        data_array = data_array.astype(np.uint8)
    
    # Create a SimpleITK image from the numpy array
    print(data_array.shape, data_array.T.shape)
    sitk_image = sitk.GetImageFromArray(data_array)
    
    # Get spacing, origin, and direction from sitk_stuff
    sitk_properties = properties['sitk_stuff']
    spacing = sitk_properties['spacing']
    origin = sitk_properties['origin']
    direction = sitk_properties['direction']
    
    # Set the spacing, origin, and direction
    sitk_image.SetSpacing(spacing)
    sitk_image.SetOrigin(origin)
    sitk_image.SetDirection(direction)
    
    # Save the image as a NIfTI file
    sitk.WriteImage(sitk_image, output_path)
    print(f"Saved 3D NIfTI with shape {data_array.shape} using SimpleITK")

def get_corresponding_files(base_path):
    """
    Find corresponding image files (.npy/.npz), segmentation file (_seg.npy) and .pkl files.
    
    Args:
        base_path (Path): Base path without extension
    
    Returns:
        tuple: (array_file_path, seg_file_path, pickle_file_path) or (None, None, None) if not found
    """
    # Check for main image file (.npy or .npz)
    if base_path.with_suffix('.npy').exists():
        array_path = base_path.with_suffix('.npy')
    elif base_path.with_suffix('.npz').exists():
        array_path = base_path.with_suffix('.npz')
    else:
        return None, None, None
    
    # Check for segmentation file
    seg_path = base_path.parent / f"{base_path.name}_seg.npy"
    if not seg_path.exists():
        seg_path = None
    
    # Check for .pkl file
    pkl_path = base_path.with_suffix('.pkl')
    if not pkl_path.exists():
        return None, None, None
    
    return array_path, seg_path, pkl_path

def process_directory(input_dir, output_dir):
    """
    Process all image files and their corresponding segmentation masks.
    
    Args:
        input_dir (str): Directory containing .npy/.npz and .pkl files
        output_dir (str): Directory to save output .nii.gz files
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Get all base filenames (without extensions and without _seg suffix)
    base_paths = set()
    for ext in ['.npy', '.npz', '.pkl']:
        for f in input_dir.glob(f'*{ext}'):
            # Remove _seg suffix if present
            base_name = f.stem[:-4] if f.stem.endswith('_seg') else f.stem
            base_paths.add(input_dir / base_name)
    
    for base_path in base_paths:
        array_path, seg_path, pkl_path = get_corresponding_files(base_path)
        
        if array_path is None or pkl_path is None:
            print(f"Skipping {base_path}: Missing required files")
            continue
        
        try:
            # Load properties (will be used for both image and segmentation)
            properties = load_pickle(pkl_path)
            
            # Process main image
            data_array = load_array_file(array_path)
            output_file = output_dir / f"{base_path.name}.nii.gz"
            convert_to_nifti_sitk(data_array, properties, str(output_file))
            print(f"Successfully converted {array_path} to {output_file}")
            
            # Process segmentation if available
            if seg_path is not None:
                seg_array = load_array_file(seg_path)
                seg_output_file = output_dir / f"{base_path.name}_seg.nii.gz"
                convert_to_nifti_sitk(seg_array, properties, str(seg_output_file), is_segmentation=True)
                print(f"Successfully converted segmentation {seg_path} to {seg_output_file}")
            
        except Exception as e:
            print(f"Error processing {base_path}: {str(e)}")
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert nnU-Net preprocessed files to NIfTI format using SimpleITK')
    parser.add_argument('--input_dir', type=str, required=True, help='Directory containing .npy/.npz and .pkl files')
    parser.add_argument('--output_dir', type=str, required=True, help='Directory to save output .nii.gz files')
    
    args = parser.parse_args()
    
    process_directory(args.input_dir, args.output_dir)
