import numpy as np                                                                                   
import h5py 

def writeh5(filename, datasetname, dtarray):                                                         
    fid=h5py.File(filename,'w')                                                                      
    ds = fid.create_dataset(datasetname, dtarray.shape, compression="gzip", dtype=dtarray.dtype)     
    ds[:] = dtarray                                                                                  
    fid.close()


### data io
def getTile(D0, sliceNames, xId, yId, zId, imSize=None, suf=''):
    rid = zId
    while rid>0 and not os.path.exists(D0+sliceNames[rid].replace('{row}',str(xId))
                             .replace('{column}',str(yId))[:-4]+suf+'.png'):
        rid -=1
    if imSize is None:
        return cv2.imread(D0+sliceNames[rid].replace('{row}',str(xId)) \
                  .replace('{column}',str(yId))[:-4]+suf+'.png' \
                 ,cv2.IMREAD_GRAYSCALE).astype(np.float16)
    else:
        return cv2.resize(cv2.imread(D0+sliceNames[rid].replace('{row}',str(xId)) \
                  .replace('{column}',str(yId))[:-4]+suf+'.png' \
                 ,cv2.IMREAD_GRAYSCALE), imSize).astype(np.float16)

def getTensor(D0, sliceNames, xId, yId, zId, imSize=None, suf=''):
    #if os.path.exists('orig_input.h5'):
    #    imTensor = np.array(h5py.File('orig_input.h5')['main']).astype(np.float32)
    #else:
    imTensor = np.zeros((imSize[0]+2*padSize[0], imSize[1]+2*padSize[1],
                           numSlice), dtype=np.float32)
    # I/O speed bound, not memory bound
    for i,zId in enumerate(zIds):
        print zId
        if zId>0 and sliceNames[zId] == sliceNames[zId-1]: # missing slice
            imTensor[:,:,i] = imTensor[:,:,i-1].copy()
        else:
            # load middle
            imTensor[padSize[0]:-padSize[0], padSize[1]:-padSize[1],i] = getTile(imDir, sliceNames, xId, yId, zId, imSize)
            # load up
            if xId == xRan[0]:
                tmpSlice = imTensor[2*padSize[0]:padSize[0]:-1, padSize[1]:-padSize[1],i]
            else:
                tmpSlice = getTile(olapDir, sliceNames, xId-1, yId, zId, suf='_d')[-padSize[0]:]
            imTensor[:padSize[0], padSize[1]:-padSize[1],i] = tmpSlice.copy()
            # load down
            if xId == xRan[1]:
                tmpSlice = imTensor[-1:-padSize[0]-1:-1, padSize[1]:-padSize[1],i]
            else:
                tmpSlice = getTile(olapDir, sliceNames, xId+1, yId, zId, suf='_u')[:padSize[0]]
            imTensor[-padSize[0]:, padSize[1]:-padSize[1],i] = tmpSlice.copy()
            # load left
            if yId == yRan[0]:
                tmpSlice = imTensor[:,2*padSize[0]:padSize[0]:-1,i]
            else:
                # left-middle
                tmpM = getTile(olapDir, sliceNames, xId, yId-1, zId, suf='_r')[:,-padSize[0]:]
                # left-up
                if xId == xRan[0]:
                    tmpU = tmpM[2*padSize[0]:padSize[0]:-1]
                else:
                    tmpU = getTile(olapDir, sliceNames, xId-1, yId-1, zId, suf='_r')[-padSize[0]:,-padSize[0]:]
                # left-down
                if xId == xRan[1]:
                    tmpL = tmpM[-1:-padSize[0]-1:-1]
                else:
                    tmpL = getTile(olapDir, sliceNames, xId+1, yId-1, zId, suf='_r')[:padSize[0],-padSize[0]:]
                tmpSlice = np.vstack((tmpU, tmpM, tmpL))
            imTensor[:, :padSize[1], i] = tmpSlice.copy()
            # load right
            if yId == yRan[1]:
                tmpSlice = imTensor[:,-1:-padSize[0]-1:-1,i]
            else:
                # right-middle
                tmpM = getTile(olapDir, sliceNames, xId, yId+1, zId, suf='_l')[:,:padSize[0]]
                # right-up
                if xId == xRan[0]:
                    tmpU = tmpM[2*padSize[0]:padSize[0]:-1]
                else:
                    tmpU = getTile(olapDir, sliceNames, xId-1, yId+1, zId, suf='_l')[-padSize[0]:,:padSize[0]]
                # right-down
                if xId == xRan[1]:
                    tmpL = tmpM[-1:-padSize[0]-1:-1]
                else:
                    tmpL = getTile(olapDir, sliceNames, xId+1, yId+1, zId, suf='_l')[:padSize[0],:padSize[0]]
                tmpSlice = np.vstack((tmpU, tmpM, tmpL))
            imTensor[:, -padSize[1]:, i] = tmpSlice.copy()
    return imTensor
