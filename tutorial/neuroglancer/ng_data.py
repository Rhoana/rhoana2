import neuroglancer
import numpy as np
import sys
import tifffile

# to run it:
# python -i ng_data.py

#### TO CHANGE
ip='140.247.107.75'
pp=98092
DD='/n/coxfs01/donglai/data/SNEMI3D/'


neuroglancer.set_server_bind_address(bind_address=ip,bind_port=pp)
viewer=neuroglancer.Viewer()

# SNEMI
res=[6,6,30]; # resolution of the data


print 'load im'
im = tifffile.imread(DD+'train-input.tif')
with viewer.txn() as s:
    s.layers.append(
        name='im',
        layer=neuroglancer.LocalVolume(
            data=im,
            voxel_size=res
        ))

print 'load gt'
im = tifffile.imread(DD+'train-labels.tif')
with viewer.txn() as s:
    s.layers.append(
        name='gt',
        layer=neuroglancer.LocalVolume(
            data=gt.astype(np.uint16),
            voxel_size=res
        ))

print viewer
