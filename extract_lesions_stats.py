import numpy as np
import SimpleITK as sitk
import pandas as pd
from typing import Union, Tuple, List, Dict, Any

from utils import cast_label_image_to_int

def extract_label_stats(label_image: Union[str, sitk.Image], background_value: int = 0) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Extract statistics for each blob in the given label image and summary statistics.

    :param label_image: The input label image, either as a SimpleITK Image object or a file path.
    :type label_image: Union[str, sitk.Image]
    :param background_value: The value to be considered as background in the label image, defaults to 0.
    :type background_value: int, optional
    :return: A tuple containing a list of dictionaries with statistics for each label and a dictionary with summary statistics.
    :rtype: Tuple[List[Dict[str, Any]], Dict[str, Any]]
    """
    # read the label image
    label_image = (
        label_image
        if isinstance(label_image, sitk.Image)
        else sitk.ReadImage(label_image)
    )
    # Instatiate the different lesions in the label image
    connected_components = sitk.ConnectedComponentImageFilter()
    connected_components.SetBackgroundValue = background_value
    # Check if the image is float type and cast to int if necessary

    if label_image.GetPixelID() in [sitk.sitkFloat32, sitk.sitkFloat64]:
        print("Warning: Label image is float type. Casting to int for connected component analysis.")
        label_image = cast_label_image_to_int(label_image)

    label_image = connected_components.Execute(label_image)
    # extract the label stats
    stats = sitk.LabelShapeStatisticsImageFilter()
    stats.SetComputePerimeter(True)
    stats.SetComputeFeretDiameter(True)
    stats.SetComputeOrientedBoundingBox(True)
    stats.Execute(label_image)
    # Populate dictionary with each lesions and it features from LabelShapeStatisticsImageFilter
    lesions_stats = [{
            "Lesion": label,
            "BoundingBox": stats.GetBoundingBox(label),
            "Centroid": stats.GetCentroid(label),
            "Elongation": stats.GetElongation(label),
            "EquivalentEllipsoidDiameter": stats.GetEquivalentEllipsoidDiameter(label),
            "EquivalentSphericalPerimeter": stats.GetEquivalentSphericalPerimeter(label),
            "EquivalentSphericalRadius": stats.GetEquivalentSphericalRadius(label),
            "Flatness": stats.GetFlatness(label),
            "PrincipalMoments": stats.GetPrincipalMoments(label),
            "NumberOfPixels": stats.GetNumberOfPixels(label),
            "NumberOfPixelsOnBorder": stats.GetNumberOfPixelsOnBorder(label),
            "Perimeter": stats.GetPerimeter(label),
            "PerimeterOnBorder": stats.GetPerimeterOnBorder(label),
            "PerimeterOnBorderRatio": stats.GetPerimeterOnBorderRatio(label),
            "PhysicalSize": stats.GetPhysicalSize(label),
            "PrincipalAxes": stats.GetPrincipalAxes(label),
            "Roundness": stats.GetRoundness(label),
            "FeretDiameter": stats.GetFeretDiameter(label),
            "OrientedBoundingBoxVertices": stats.GetOrientedBoundingBoxVertices(label),
            "OrientedBoundingBoxOrigin": stats.GetOrientedBoundingBoxOrigin(label),
            "OrientedBoundingBoxSize": stats.GetOrientedBoundingBoxSize(label),
            "OrientedBoundingBoxDirection": stats.GetOrientedBoundingBoxDirection(label)}  for label in stats.GetLabels()]
    physical_sizes = [lesion["PhysicalSize"] for lesion in lesions_stats]
    if physical_sizes:
        summary_stats = {
            "N_lesions": len(lesions_stats),
            "Total_volume": np.sum(physical_sizes),
            "Lesion_volume_mean": np.mean(physical_sizes),
            "Lesion_volume_std": np.std(physical_sizes),
            "Lesion_volume_min": np.min(physical_sizes),
            "Lesion_volume_max": np.max(physical_sizes),
            "Lesion_volume_median": np.median(physical_sizes),
            "Lesion_iqr": np.percentile(physical_sizes, 75) - np.percentile(physical_sizes, 25)
        }
    else: # if no lesions are found
        summary_stats = {
            "N_lesions": 0,
            "Total_volume": 0,
            "Lesion_volume_mean": 0,
            "Lesion_volume_std": 0,
            "Lesion_volume_min": 0,
            "Lesion_volume_max": 0,
            "Lesion_volume_median": 0,
            "Lesion_iqr": 0
        }
    
    return lesions_stats, summary_stats

if __name__ == "__main__":
    import os
    import glob
    import pandas as pd
    main_dir = '/media/chuv2/MSSeg/data/split4'
    main_labels_dir = os.path.join(main_dir,'*/gt_cl/*.nii.gz')
    save_cls_path = os.path.join(main_dir,"all_cl_stats.csv")
    save_summary_path = os.path.join(main_dir,"summary_cl_stats.csv")
    cl_mask_paths = glob.glob(main_labels_dir)
    cl_list = []
    cl_summary_list = []

    for mask in cl_mask_paths:
        # Extract filename and folder name
        filename = os.path.basename(mask)
        subject_id = filename.split('_')[0]
        session = int(filename.split('_')[1].split('-')[1])
        folder_name = os.path.basename(os.path.dirname(os.path.dirname(mask)))
         # Switch for assigning site_exp based on folder_name
        site_exp_mapping = {
            'nih_7t': 'NIH_7T',
            'nih_3t': 'NIH_3T',
            'ucl_msmimic': 'UCL_MSMIMIC',
            'ucl': 'UCL_MS',
            'test_out': 'CHUV_Advanced',
        }

        folder_name_lower = folder_name.lower()
        site_exp = 'Unknown'

        for key, value in site_exp_mapping.items():
            if key in folder_name_lower:
                site_exp = value
                break

        if site_exp == 'Unknown':
            if any(split in folder_name_lower for split in ['val', 'train', 'test_in']):
                site_exp = 'Basel_INsIDER'

        print(f"Processing file: {filename} in {folder_name}")
        label_stats, summary_stats = extract_label_stats(mask)
        print(f"Number of lesions: {summary_stats['N_lesions']}")
        print(f"Total lesion volume: {summary_stats['Total_volume']:.2f}")
        print("---")
        
        # Create a dictionary with common metadata
        metadata = {
            'subject_id': subject_id,
            'TP': session,
            'in_split4': folder_name,
            'filename': filename,
            'site_exp': site_exp
        }
        
        # Update label_stats and summary_stats with metadata
        # Update each dictionary in label_stats with metadata
        for stats in label_stats:
            stats.update(metadata)
        cl_list += label_stats
        # Update summary_stats with metadata
        summary_stats.update(metadata)
        cl_summary_list.append(summary_stats)
    
    cl_df = pd.DataFrame(cl_list)
    cl_summary_df = pd.DataFrame(cl_summary_list)
  
    cl_df.to_csv(save_cls_path, index=False)
    cl_summary_df.to_csv(save_summary_path, index=False)

        

