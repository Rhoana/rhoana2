import numpy as np
cimport numpy as np

cdef extern from "cpp_idm/idm_main.h":
    void idm_dist(float *img1, float *img2, float *out, 
                  int im_chan, int im_col, int im_row, 
                  int patch_sz, int warp_sz, int patch_step, int metric);

def idm(np.ndarray[np.float32_t, ndim=3] img1, 
             np.ndarray[np.float32_t, ndim=3] img2, 
             patch_sz=11, warp_sz=5, patch_step=1, metric=1):
    # size: x*y*c (C-order, change last dim first)
    img1 = np.ascontiguousarray(img1)
    img2 = np.ascontiguousarray(img2) 
    dim = img1.shape
    cdef np.ndarray[np.float32_t, ndim=2] dist
    dist = np.zeros((int(np.ceil(dim[0]/float(patch_step))), int(np.ceil(dim[1]/float(patch_step))))
                    , dtype=np.float32);
    idm_dist(&img1[0,0,0], &img2[0,0,0], &dist[0,0], 
             dim[0], dim[1], dim[2], patch_sz, warp_sz, patch_step, metric);
    return dist

def idm_ims(np.ndarray[np.float32_t, ndim=4] imgs, img_step=1,
             patch_sz=11, warp_sz=5, patch_step=1, metric=1):
    # size: n*x*y*c (C-order, change last dim first)
    dim = imgs.shape
    out = np.zeros((dim[0]-img_step, int(np.ceil(dim[1]/float(patch_step))), int(np.ceil(dim[2]/float(patch_step)))),dtype=np.float32)
    cdef np.ndarray[np.float32_t, ndim=2] dist = np.zeros((int(np.ceil(dim[1]/float(patch_step))), int(np.ceil(dim[2]/float(patch_step)))), dtype=np.float32);
    cdef np.ndarray[np.float32_t, ndim=3] img1 = np.zeros((dim[1], dim[2], dim[3]), dtype=np.float32);
    cdef np.ndarray[np.float32_t, ndim=3] img2 = np.zeros((dim[1], dim[2], dim[3]), dtype=np.float32);

    for im_id in range(dim[0]-img_step):
        print('idm: %d/%d'%(im_id+1,dim[0]-1))
        img1 = np.ascontiguousarray(imgs[im_id])
        img2 = np.ascontiguousarray(imgs[im_id+img_step]) 
        idm_dist(&img1[0,0,0], &img2[0,0,0], &dist[0,0], 
                 dim[1], dim[2], dim[3], patch_sz, warp_sz, patch_step, metric);
        out[im_id] = dist[:]
    return out
