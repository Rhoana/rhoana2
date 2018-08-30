import unittest 

import em_pre
import pickle
import imageio
import numpy as np

class TestIDM(unittest.TestCase):
    def test_01(self):
        psz=3;wsz=0;step=3;
        im1 = np.zeros((5,5,1)).astype(np.float32)
        im2 = np.ones((5,5,1)).astype(np.float32)
        dist = em_pre.idm(im1, im2, psz, wsz, step, 0)
        self.assertTrue(np.max(np.abs(dist-1.0))<1e-4)

    def test_im(self):
        psz=11;wsz=5;step=11;

        im1 = imageio.imread('./test/im1.png')[:,:,None].astype(np.float32) / 255.
        im2 = imageio.imread('./test/im2.png')[:,:,None].astype(np.float32) / 255.
        dist = em_pre.idm(im1, im2, psz, wsz, step)

        ims = np.stack([im1,im2],axis=0)
        dist2 = em_pre.idm_ims(ims, psz, wsz, step)
        
        self.assertTrue(np.max(np.abs(dist-dist2))<1e-4)

if __name__ == '__main__':                                                                                                           
    unittest.main()
