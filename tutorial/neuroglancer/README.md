# Neuroglancer

## Installation 

(for vcg user: directly activate the existing env)
1. setup environment:
```
conda env create -f env_ng.yml -n YOUR-ENV-NAME
```

2. download and compile neuroglancer
``` 
git clone https://github.com/google/neuroglancer
```

## Demo
Display the training image and groundtruth segmentation for SNEMI dataset
```
python -i ng_data.py
```
