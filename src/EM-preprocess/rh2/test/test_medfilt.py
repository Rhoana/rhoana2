import unittest 
import numpy as np
from scipy.ndimage.filters import median_filter

from em_pre import pad_image, medfilt2d

class TestMedianFilter(unittest.TestCase):
    def test_pad(self):
        sz=(100,100);w_hsz=10
        a=np.random.random(sz)
        out = pad_image(a[:,:,None],w_hsz)
        out_gt = np.pad(a,w_hsz,'reflect')
        self.assertTrue((np.abs(out[:,:,0]-out_gt)).max()<1e-5)

    def test_mf(self):
        sz=(100,100);w_hsz=10
        #sz=(3,3);w_hsz=1
        a=np.random.random(sz)
        #a=np.arange(9).reshape((3,3)).astype(float)
        o1 = np.pad(a,w_hsz,'reflect')
        o2 = median_filter(o1,2*w_hsz+1)[w_hsz:-w_hsz, w_hsz:-w_hsz]
        medfilt2d(a[:,:,None],w_hsz)
        self.assertTrue((np.abs(a-o2)).max()<1e-5)

if __name__ == '__main__':                                                                                                           
    unittest.main()
