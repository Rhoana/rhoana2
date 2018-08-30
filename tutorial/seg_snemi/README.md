# Step-by-Step Example for SNEMI3D Challenge

## 1. Preparation

- Install Minicoda [python 2.7](https://conda.io/miniconda.html)

- Change script permission: `chmod +x *.sh`

- Install github repos: `./install_snemi3d.sh`

- Download data: `./download_data.sh`

## 2. Pipeline
### 2.1 Image Deflickering
(not ready yet)

### 2.2. Affinity Prediction 
(not ready yet, download affinity for [SNEMI-train](http://140.247.107.75/rhoana_product/snemi/aff/model_snemi_dice_mls._train_min.h5))

### 2.3. Segmentation and Evaluation
- METHOD_ID: 0=zwatershed, 1=waterz, 2=zwatershed+waterz
- DO_TRAIN: 0=train, 1=test
- SAVE_SEG: 0=no save
```
python do_snemi3d.py METHOD_ID DO_TRAIN SAVE_SEG
```
