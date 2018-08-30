import os,sys
import h5py
import numpy as np
import time
import tifffile

import em_segLib
from em_segLib.seg_dist import DilateData
from em_segLib.seg_util import relabel
from em_segLib.io_util import writeh5
from em_segLib.seg_eval import adapted_rand
# example: python do_snemi3d.py 0 0 1


opt = sys.argv[1] # 0: ..
mode = int(sys.argv[2]) # 0: train, 1: test
nn = ['train','test'][mode]
do_save=0
if len(sys.argv)>3:
    do_save = int(sys.argv[3]) # 1: save

## TODO:
# add affinity location
D_aff='/n/coxfs01/vcg_connectomics/snemi/affs/tmquan_0524_v2/model_snemi_dice_mls._'+nn+'_min.h5'
aff = np.array(h5py.File(D_aff)['main']) 

# ground truth
if mode==0:
    D0='/n/coxfs01/donglai/data/SNEMI3D/'
    seg = tifffile.imread(D0+nn+'-labels.tif').astype(np.uint32)

if opt =='0': 
    # 3D zwatershed
    import zwatershed
    print 'zwatershed'
    st = time.time()
    T_aff=[0.05,0.995,0.2]
    T_thres = [800]
    T_dust=600
    T_merge=0.9
    T_aff_rel=1
    out = zwatershed.zwatershed(aff, T_thres, T_aff=T_aff, \
                                T_dust=T_dust, T_merge=T_merge,T_aff_relative=T_aff_rel)[0][0]
    et = time.time()
    out = relabel(out)
    sn = '%s_%f_%f_%d_%f_%d_%f_%d.h5'%(opt,T_aff[0],T_aff[1],T_thres[0],T_aff[2],T_dust,T_merge) 
elif opt =='1':
    # 2D watershed + waterz
    import waterz
    print 'waterz-0.8'
    st = time.time()
    low=0.05;high=0.995
    mf = 'aff85_his256';T_thres = [0.2]
    out = waterz.waterz(aff, T_thres, merge_function=mf, gt_border=0,
                        aff_threshold=[low,high])[0]
    et = time.time()
    out = relabel(out)
    sn = '%s_%f_%f_%f_%s.h5'%(opt,low,high,T_thres[0],mf) 
elif opt =='2':
    # 2D zwatershed + waterz
    import waterz
    import zwatershed
    print 'zwatershed + waterz'
    st = time.time()
    T_thres = [800]
    T_aff=[0.05,0.95,0.2]
    T_dust=600
    T_merge=0.9
    T_aff_rel=1
    sz = np.array(aff.shape)
    out = np.zeros(sz[1:],dtype=np.uint64)
    id_st = np.uint64(0)
    # need to relabel the 2D seg, o/w out of bound
    for z in range(sz[1]):
        out[z] = relabel(zwatershed.zwatershed(aff[:,z:z+1], T_thres, T_aff=T_aff, \
                                T_dust=T_dust, T_merge=T_merge,T_aff_relative=T_aff_rel)[0][0])

        out[z][np.where(out[z]>0)] += id_st
        id_st = out[z].max()
    
    mf = 'aff50_his256';T_thres2 = [0.5]
    out = waterz.waterz(affs=aff, thresholds=T_thres2, fragments=out, merge_function=mf)[0]
    et = time.time()
    sn = '%s_%f_%f_%d_%f_%d_%f_%d_%f_%s.h5'%(opt,T_aff[0],T_aff[1],T_thres[0],T_aff[2],T_dust,T_merge,T_aff_rel,T_thres2[0],mf) 

print 'time: %.1f s'%((et-st))
# do evaluation
if mode==0:
    score = adapted_rand(out.astype(np.uint32), seg)
    print score 
    # 0: 0.22
    # 1: 0.098
    # 2: 0.137
# do save
if do_save==1:
    writeh5('result/'+sn+'.h5', 'main', out)
