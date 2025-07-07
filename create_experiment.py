import os
import shutil
import pandas as pd

from utils import generate_dataset_json, synth_strip

class SEQUENCES:
    MP2RAGE = 'MP2RAGE'
    MPRAGE = 'MPRAGE'
    FLAIR = 'FLAIR'
    T1W = 'T1W'

class FOLDERS:
    IMAGES_TRAIN = 'imagesTr'
    IMAGES_TEST = 'imagesTs'
    LABELS_TRAIN = 'labelsTr'
    LABELS_TEST = 'labelsTs'
    DATASET = 'Dataset'

def create_nnUNet_folder_struct(main_dataset_folder:str):
    dataset_name = os.path.split(main_dataset_folder)[1]
    assert dataset_name.startswith(FOLDERS.DATASET)
    os.makedirs(main_dataset_folder, exist_ok=True)
    for folder in [FOLDERS.IMAGES_TRAIN, FOLDERS.IMAGES_TEST, FOLDERS.LABELS_TRAIN, FOLDERS.LABELS_TEST]:
        os.makedirs(os.path.join(main_dataset_folder, folder), exist_ok=True)

if __name__ == '__main__':
    import glob
    main_img_bids_path = '/media/chuv2/CL-Mock-BIDS/'
    main_img_split_path = '/media/chuv2/MSSeg/data/split4/'
    main_lbl_path = '/media/chuv2/MSSeg/data/split4/'
    splits_csv = '/media/chuv2/MSSeg/data/split4/cl-foundational_train_test_splits_bins-5_seed-42.csv'
    skull_stripping = True
    dataset_name = 'Dataset301_CL_Multisite'
    # some images are not present in the split. The labels are notin the BIDS because is really horrible to follow the stadard for it
    check_in_bids_for = {'train_tp2':'merged_insider','val_tp2':'merged_insider', 'test_tp2':'merged_insider','test_out':'advanced', 'test_out_nih_3t':'nih3t', 'test_out_nih_7t':'nih7t'}
    splits_df = pd.read_csv(splits_csv)

    dataset_path = os.path.join(main_img_split_path, dataset_name)
    create_nnUNet_folder_struct(dataset_path)
    nnunet_img_train = os.path.join(dataset_path, FOLDERS.IMAGES_TRAIN)
    nnunet_img_test = os.path.join(dataset_path, FOLDERS.IMAGES_TEST)
    nnunet_lbl_train = os.path.join(dataset_path, FOLDERS.LABELS_TRAIN)
    nnunet_lbl_test = os.path.join(dataset_path, FOLDERS.LABELS_TEST)
    
    n_train = 0
    #for row in splits_df.sample(n=3).itertuples():
    for row in splits_df.itertuples(): 
        lbl_pth = os.path.join(main_lbl_path, row.in_split4,'gt_cl', row.filename)
        img_dir = os.path.join(
            main_img_bids_path, 
            check_in_bids_for[row.in_split4], 
            row.subject_id, 
            'ses-0' + str(row.TP), 
            'anat', 
            '*T1w.nii.gz'
        ) if row.in_split4 in check_in_bids_for.keys() else os.path.join(
            main_img_split_path, 
            row.in_split4,
            'MP*RAGE', # Some datasets have MP2RAGE and MPRAGE images that we group as T1w
            row.subject_id+'_ses-0'+str(row.TP)+'*.nii.gz'
        )
        img_pth = glob.glob(img_dir) 

        if not os.path.exists(lbl_pth):
            print('Label',lbl_pth, 'not found')

        for img in img_pth:
            print('Processing',img)
            t1w_sequence = SEQUENCES.MP2RAGE if SEQUENCES.MP2RAGE.lower() in img.lower() else SEQUENCES.MPRAGE 
            nnunet_filename = f"{row.subject_id}_TP-0{str(row.TP)}_site-{row.site_exp}_seq-{t1w_sequence}_dom-{row.domain}_0000.nii.gz"
            save_img_pth_base = nnunet_img_train if row.train else nnunet_img_test
            save_img_pth = os.path.join(save_img_pth_base, nnunet_filename)
            save_lbl_pth = os.path.join(nnunet_lbl_train, f"{nnunet_filename}.nii.gz") if row.train else os.path.join(nnunet_lbl_test, f"{nnunet_filename}.nii.gz")
            if skull_stripping: # not sure how the skull stripping was done before so for homogenization I re-do it
                synth_strip(os.path.dirname(img), os.path.basename(img),save_img_pth_base, nnunet_filename)
            else:
                shutil.copyfile(img, save_img_pth)
            shutil.copyfile(lbl_pth, save_lbl_pth)    
            n_train = n_train +1 if row.train else n_train 

    
    ## generate json 
    description = f"This dataset joins the T1w images (MPRAGE and MP2RAGE) of Advanced, INsIDER and NIH for training letting UCL for testing"
    generate_dataset_json(dataset_path, 
                          channel_names={0:'T1w'}, 
                          labels={'background':0, "CL": 1,}, 
                          num_training_cases=n_train, 
                          file_ending='.nii.gz', 
                          dataset_name=dataset_name, 
                          description=description)   