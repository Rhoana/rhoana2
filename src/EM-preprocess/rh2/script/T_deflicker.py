# test video deflicker
import numpy as np
import h5py

from em_pre.deflicker import deflicker_batch, deflicker_online
from T_util import writeh5

def test_snemi():
    # load data: 100x1024x1024
    ims = np.array(h5py.File('/n/coxfs01/donglai/data/SNEMI3D/train-input.h5')['main'])

    # batch version
    out = deflicker_batch(ims.transpose((1,2,0)), opts=[0,0,0], globalStat=[150,-1], filterS_hsz=[15,15], filterT_hsz=2)
    writeh5('tmp/snemi_df150_batch.h5','main',out)

    # online version
    def getN(i):
        return ims[i]
    out = deflicker_online(getN, opts=[0,0,0], globalStat=[150,-1], filterS_hsz=[15,15], filterT_hsz=2)
    writeh5('tmp/snemi_df150_online.h5','main',out)

if __name__ == "__main__":
    test_snemi()
