import os
import cv2
import numpy as np
import h5py
import scipy.ndimage as nd

def preprocess(im, globalStat=None, globalStatOpt=0):
    # im: x,y,t
    if globalStatOpt == 0: 
        # mean/std
        if globalStat is not None:
            mm = im.mean(axis=0).mean(axis=0)
            if globalStat[1]>0:
                tmp_std = np.std(im)
                if tmp_std<1e-3:
                    im = (im-mm)+globalStat[0]
                else:
                    im = (im-mm)/np.std(im)*globalStat[1]+globalStat[0]
            else:
                if globalStat[0]>0:
                    im = im-mm+globalStat[0]
    return im

def deflicker_batch(ims, opts=[0,0,0], globalStat=None, filterS_hsz=[15,15], filterT_hsz=2):
    # ims: x,y,t
    # opts: globalStat, fliterS, filterT

    # prepare parameters
    sizeS = [x*2+1 for x in filterS_hsz]
    sizeT = 2*filterT_hsz+1
    numSlice = ims.shape[2]

    print '1. global normalization'
    if globalStat is None:
        if opts[0]==0:
            # stat of the first image
            globalStat = [np.mean(ims[:,:,0]),np.std(ims[:,:,0])]
        else:
            raise('need to implement')
    ims = preprocess(ims.astype(np.float32), globalStat, opts[0])

    print '2. local normalization'
    print '2.1 compute spatial mean'
    if opts[1] == 0:
        filterS = np.ones((sizeS[0], sizeS[1], 1), dtype=np.float32)/(sizeS[0]*sizeS[1]) 
        meanTensor = nd.convolve(ims, filterS)
    else:
        raise('need to implement')

    print '2.2 compute temporal median'
    if opts[2] == 0:
        meanTensorF = nd.median_filter(meanTensor,(1, 1, sizeT)) 
    else:
        raise('need to implement')
    print '2.3. add back filtered difference'
    out = ims + nd.convolve(meanTensorF - meanTensor, filterS)
    out = np.clip(out,0,255).astype(np.uint8) # (-1).uint8=254
    return out 

def deflicker_online(getIm, numSlice=100, opts=[0,0,0], 
                     globalStat=None, filterS_hsz=[15,15], filterT_hsz=2, output=None):
    # im: x,y,t
    # filters: spatial=(filterS_hsz, opts[1]), temporal=(filterT_hsz, opts[2])
    # seq stats: imSize, globalStat, globalStatOpt

    im0 = getIm(0)
    imSize = im0.shape
    sizeS = [x*2+1 for x in filterS_hsz]
    sizeT = 2*filterT_hsz+1

    if opts[1]==0:# mean filter: sum to 1
        filterS = np.ones(sizeS, dtype=np.float32)/(sizeS[0]*sizeS[1])
    else:
        raise('need to implement')

    if output is None:
        out = np.zeros((imSize[0],imSize[1],numSlice),dtype=np.uint8)
    print '1. global normalization'
    if globalStat is None:
        if opts[0]==0:
            # stat of the first image
            globalStat = [np.mean(im0),np.std(im0)]
        else:
            raise('need to implement')

    print '2. local normalization'
    meanTensor = np.zeros((imSize[0],imSize[1],sizeT))
    # initial chunk
    # e.g. sizeT=7, filterT_hsz=3, mid_r=3
    for i in range(filterT_hsz+1): # 0-3
        # flip the initial frames to pad
        meanTensor[:,:,i] = cv2.filter2D(preprocess(getIm(filterT_hsz-i), globalStat,opts[0]), 
                                         -1, filterS, borderType=cv2.BORDER_REFLECT_101)
    for i in range(filterT_hsz-1): # 0-1 -> 4-5 
        meanTensor[:,:,filterT_hsz+1+i] = meanTensor[:,:,filterT_hsz-1-i].copy()

    # online change chunk
    print '2. local normalization'
    im_id = filterT_hsz # image 
    chunk_id = sizeT-1
    for i in range(numSlice):
        print 'process: '+str(i+1)+'/'+str(numSlice)
        # current frame
        im = preprocess(getIm(i), globalStat, opts[0])

        # last frame needed for temporal filter
        if filterT_hsz+i<numSlice:
            imM = preprocess(getIm(filterT_hsz+i), globalStat, opts[0])
        else: # reflection mean
            imM = preprocess(getIm(numSlice-1-filterT_hsz+(numSlice-1-i)), globalStat, opts[0])
        meanTensor[:,:,chunk_id] = cv2.filter2D(imM,-1,filterS, borderType=cv2.BORDER_REFLECT_101)

        # local temporal filtering
        if opts[2]==0: # median filter
            filterR = nd.filters.median_filter(meanTensor,(1,1,sizeT))
        else:
            raise('need to implement')

        filterRD = filterR[:,:,filterT_hsz]-meanTensor[:,:,im_id]
        imDiff = cv2.filter2D(filterRD,-1,filterS,borderType=cv2.BORDER_REFLECT_101)
        out_im = np.clip(im+imDiff,0,255).astype(np.uint8)

        if output is not None:
            cv2.imwrite(output%(i), out_im)
        else:
            out[:,:,i] = out_im

        im_id = (im_id+1) % sizeT
        chunk_id = (chunk_id+1) % sizeT
    if output is None:
        return out
