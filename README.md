# Benchmarking and Explaining Deep Learning Multiple Sclerosis Cortical Lesion Segmentation Performance

This repository contains the research code associated with the paper **"Benchmarking and Explaining Deep Learning Multiple Sclerosis Cortical Lesion Segmentation Performance"** (provisional title).

## 📄 Paper Abstract

*[Abstract to be added]*

This work presents a comprehensive benchmarking study of deep learning approaches for multiple sclerosis cortical lesion segmentation, with particular focus on performance explanation and multi-site generalization.

## 🔬 Research Overview

This study addresses the critical need for robust and explainable cortical lesion segmentation in multiple sclerosis. Our research encompasses:

- **Multi-site benchmarking**: Evaluation across Advanced, INsIDER, NIH (3T/7T), and UCL datasets
- **Cross-domain validation**: Assessment of model generalization across different clinical sites
- **Performance explanation**: Analysis of factors influencing segmentation accuracy
- **Stratified evaluation**: Balanced assessment considering lesion characteristics and site diversity

## 📁 Repository Contents

### Preprocessing Pipeline

- **`create_experiment.py`**: Creates nnU-Net compatible dataset structure from multi-site BIDS data
- **`create_splits.py`**: Implements stratified splitting methodology ensuring balanced representation
- **`extract_lesions_stats.py`**: Extracts comprehensive lesion characteristics for analysis
- **`utils.py`**: Core utilities including dataset.json generation and SynthStrip integration

### Data Conversion Tools

- **`nnunet_preprocessed_to_nii.py`**: Converts nnU-Net preprocessed data back to NIfTI format
- **`nnunet_preprocessed_to_nii_itk.py`**: Alternative implementation using SimpleITK
- **`reorienter.py`**: Ensures consistent orientation between images and segmentation masks

### Analysis Framework

- **`latent_space_analysis/`**: Analyze the 3D nnU-Net bottleneck features in relationship with categorical and continuous features.
- **`metrics.py`**: Used for model robustness and calibration evaluation.

<!-- The analysis framework will include:
- Cross-site performance benchmarking
- Lesion detection sensitivity analysis  
- Explanation of model performance factors
- Statistical validation across domains
- Visualization tools for research findings -->

## 🐳 Trained Model Access

### Docker Container

The primary deliverable of this research is a containerized model for cortical lesion segmentation, available at:

**[https://hub.docker.com/repository/docker/petermcgor/nnunetv2/general](https://hub.docker.com/repository/docker/petermcgor/nnunetv2/general)**

**Model Specifications:**
- **Architecture**: nnU-Net 3D full resolution  
- **Input**: T1-weighted MRI (MP2RAGE/MPRAGE sequences)
- **Output**: Binary cortical lesion probability maps
- **Training**: Multi-site MS cohort with stratified cross-validation
- **Validation**: Cross-domain evaluation on independent test sets

**Preprocessing Requirements for Predictions:**
The only preprocessing required for new images is skull stripping using [SynthStrip](https://surfer.nmr.mgh.harvard.edu/docs/synthstrip/). Detailed usage instructions and examples are provided in the Docker repository's README.

## 🔬 Reproducibility

### Data Preparation

The preprocessing pipeline ensures reproducible data preparation:

1. **Multi-site integration**: Harmonized processing across clinical sites
2. **Stratified splitting**: Maintains balanced representation while preventing data leakage
3. **Quality control**: Automated exclusion of low-quality scans based on MRIQC metrics
4. **Standardization**: Consistent skull stripping and orientation across datasets

### Cross-Validation Strategy

Our stratified approach ensures:
- Subject-level grouping (no data leakage between train/test)
- Balanced site representation across folds
- Lesion characteristic stratification (count, volume, distribution)
- Domain separation (development vs. deployment datasets)

## 📊 Benchmarking Results

*[Results section to be expanded with paper publication]*

Key findings from our benchmarking study:
- Cross-site generalization performance
- Impact of training data diversity
- Lesion size and location bias analysis
- Comparison with existing methods

## 🔍 Performance Explanation

The latent space analysis was used to get insight into the model performance. 
The proposed analysis is described in a corresponding [README](https://github.com/NataliiaMolch/nnu-net-latent-space-analysis/blob/main/readme.md).

Our explanation framework investigates:
- Site-specific performance factors
- Model confidence and uncertainty quantification
- Feature attribution analysis
- Cross-domain adaptation mechanisms

## 📚 Citation

If you use this code or model in your research, please cite:

```bibtex
@article{[PAPER_KEY],
    title={Benchmarking and Explaining Deep Learning Multiple Sclerosis Cortical Lesion Segmentation Performance},
    author={[AUTHORS]},
    journal={[JOURNAL]},
    year={2024},
    url={https://arxiv.org/abs/[ARXIV_ID]}
}
```

### Dataset Citation

```bibtex
@dataset{[DATASET_KEY],
    title={Multi-site Multiple Sclerosis Cortical Lesion Dataset},
    author={[AUTHORS]},
    year={2024},
    publisher={Zenodo},
    doi={[ZENODO_DOI]},
    url={https://zenodo.org/record/[RECORD_ID]}
}
```


## 📄 Code Availability

### Training Data
- **Multi-site cohort**: Advanced, INsIDER, NIH (3T/7T) datasets
- **Ground truth**: Expert-annotated cortical lesion segmentations  
- **Metadata**: Comprehensive lesion statistics and site information

### Code Availability
- **Preprocessing pipeline**: Available in this repository
- **Model weights**: ??
- **Analysis scripts**: Available in this repository and [here](https://github.com/NataliiaMolch/nnu-net-latent-space-analysis/blob/main/readme.md)

## 🔗 Links

- **ArXiv preprint**: [https://arxiv.org/abs/[ARXIV_ID]](https://arxiv.org/abs/[ARXIV_ID])
- **Zenodo dataset**: [https://zenodo.org/record/[RECORD_ID]](https://zenodo.org/record/[RECORD_ID])  
- **Docker model**: [https://hub.docker.com/repository/docker/petermcgor/nnunetv2/general](https://hub.docker.com/repository/docker/petermcgor/nnunetv2/general)

## 📧 Contact

For questions regarding this research:

- **Corresponding author**: [Email]
- **Code issues**: Open GitHub issue
- **Collaboration**: [Research collaboration contact]

---

**Acknowledgments**: This work was supported by the Hasler Foundation Responsible AI program (MSxplain) and the Research Commission of the Faculty of Biology and Medicine (CRFBM) of UNIL. We acknowledge access to the facilities and expertise of the CIBM Center for Biomedical Imaging, a Swiss research center of excellence founded and supported by Lausanne University Hospital (CHUV), University of Lausanne (UNIL), École polytechnique fédérale de Lausanne(EPFL), University of Geneva (UNIGE), and Geneva University Hospitals(HUG). AC is supported by EUROSTAR E!113682 HORIZON2020. DR and CT are supported by the Intramural Research Program of NINDS, NIH. CVB received funding from the Fonds de Recherche Clinique (FRC) from Cliniques Universitaires Saint-Luc (CUSL). AS has the financial support of the Fédération Wallonie Bruxelles – FRIA du Fonds de la Recherche Scientifique – FNRS. SB is supported by the Funds Claire Fauconnier, Ginette Kryksztein José and Marie Philippart-Hoffelt, managed by the King Baudouin Foundation. PM is supported by the Fondation Charcot Stichting Research Fund 2023, the Fund for Scientific Research (F.R.S, FNRS; grant 40008331), Cliniques universitaires Saint-Luc “Fonds de Recherche Clinique” and Biogen.

**Ethics**: All data collection and usage protocols were approved by relevant institutional review boards and ethics committees.
