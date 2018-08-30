import unittest
import pickle
import numpy as np

from em_segLib.seg_malis import malis_init, malis_loss_weights_both
from em_segLib.seg_util import mknhood3d

def sigmoid(x):
    return 0.5 + 0.5 * np.tanh(0.5*x)
    #return 1 / (1 + np.exp(-x))

class TestMalis(unittest.TestCase):
    def test_malis(self):
        D0='/n/coxfs01/donglai/malis_trans/keras_test/'
        pred = sigmoid(pickle.load(open(D0+'test_malis_caffe_conv18.pkl','rb')))
        seg = pickle.load(open(D0+'test_malis_ecs_seg.pkl','rb'))[0].astype(np.uint64)
        label = pickle.load(open(D0+'test_malis_ecs_aff.pkl','rb')).astype(np.float32)

        conn_dims = np.array(label.shape[1:]).astype(np.uint64)
        nhood_dims = np.array((3,3),dtype=np.uint64)
        nhood_data = mknhood3d(1).astype(np.int32).flatten()
        pre_ve, pre_prodDims, pre_nHood = malis_init(conn_dims, nhood_data, nhood_dims)
        weight = malis_loss_weights_both(seg.flatten(), conn_dims, nhood_data, nhood_dims, pre_ve, 
                                         pre_prodDims, pre_nHood, pred.flatten(), label.flatten(), 0.5).reshape(conn_dims)

        loss = np.sum(weight * (pred - label) ** 2)
        self.assertTrue(np.abs(loss-0.49248358)<1e-5)



if __name__ == '__main__':
    unittest.main()
