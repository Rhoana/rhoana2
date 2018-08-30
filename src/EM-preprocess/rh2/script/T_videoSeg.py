import os,sys
opt = sys.argv[1]

if opt=='0':
    # video shot detection 
    # python script/T_videoSeg.py 1
    import h5py
    import numpy as np
    import em_pre
    from T_util import writeh5

    D0 = '/n/coxfs01/vcg_cellDiv/D2016.01.08_S0973_I313_WELL01/'
    fn = 'F0'
    # input data
    dataN = D0+'img/'+fn+'_data.h5'

    # idm parameters
    step = 1 # frame step
    psz = 5 # patch size
    wsz = 9 # warp size to search
    stride = 5 # stride for efficient approximation
    metric = 1 # 0: L1, 1: L1-ratio

    outN = D0+'dist/'+fn+'_%d_%d_%d_%d_%d.h5' %(step,psz,wsz,stride,metric)
    if os.path.exists(outN):
        print 'done: ',outN
    else:
        if not os.path.exists(dataN):
            print 'create h5'
            import cv2,glob
            imN = sorted(glob.glob(D0+'img/'+fn+'/*.JPG'))
            im0 = cv2.imread(imN[0], 0) 
            sz = im0.shape
            out = np.zeros((len(imN),sz[0],sz[1]), dtype=np.uint8)
            for i in range(len(imN)):
                out[i,:,:] = cv2.imread(imN[i], 0)
            writeh5(dataN, 'main', out)
        else:
            print 'load h5'
            out = np.array(h5py.File(dataN)['main'])
            out = out[:,25:-25].astype(np.float32)/255.0 # remove the margin
        sz = out.shape
        dist = em_pre.idm_ims(out.reshape((sz[0],sz[1],sz[2],1)), step, psz, wsz, stride, metric)
        writeh5(outN, 'main', dist)


