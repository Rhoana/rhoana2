import numpy as np
from scipy.signal import medfilt2d as sp_medfilt2d
cimport numpy as np
import cv2

cdef extern from "cpp_flow/Coarse2FineFlowWrapper.h":
    void Coarse2FineFlowWrapper(double * vx, double * vy, double * warpI2,
                                const double * Im1, const double * Im2,
                                double alpha, double ratio, int minWidth,
                                int nOuterFPIterations, int nInnerFPIterations,
                                int nSORIterations, int colType,
                                int h, int w, int c, 
                                double warp_step, int medfilt_hsz, double flow_scale);
    void Coarse2FineFlowWrapper_flows(double * warpI2,
                                    const double * Ims, int nIm,
                                    double alpha, double ratio, int minWidth,
                                    int nOuterFPIterations, int nInnerFPIterations,
                                    int nSORIterations, int colType,
                                    int h, int w, int c, 
                                    double warp_step,int im_step,int medfilt_hsz, double flow_scale);

# for debug
cdef extern from "cpp_flow/MedianFilter.h":
    void padImage(double *im, double *im_p, 
            int hh, int ww, int cc, int win_hsize);
    void medianFilter(double *im, int mHeight, int imWidth, 
            int nChannels, int win_hsize);


def pad_image(np.ndarray[double, ndim=3] im not None,
                int win_hsize=5):
    cdef int h = im.shape[0]
    cdef int w = im.shape[1]
    cdef int c = im.shape[2]
    cdef np.ndarray[double, ndim=3] im_p = np.ascontiguousarray(np.zeros((h+2*win_hsize, w+2*win_hsize, c), dtype=np.float64))
    padImage(&im[0,0,0], &im_p[0,0,0], h, w, c, win_hsize)
    return im_p

def medfilt2d(np.ndarray[double, ndim=3] im not None,
                int win_hsize=5):
    cdef int h = im.shape[0]
    cdef int w = im.shape[1]
    cdef int c = im.shape[2]
    medianFilter(&im[0,0,0], h, w, c, win_hsize)

def warpback_image(img, flow, opt_interp=0, opt_border=0):
    # input: im2, flow(im1->im2)
    # output: warped im2 (similar to im1)
    # flow: h*w*2
    h, w = flow.shape[:2]
    #flow = -flow.copy()
    # make copy, so won't overwrite the flow value
    flow = flow.copy()
    flow[:,:,0] += np.arange(w)
    flow[:,:,1] += np.arange(h)[:,np.newaxis]
    interps=[cv2.INTER_NEAREST, cv2.INTER_LINEAR, cv2.INTER_AREA, cv2.INTER_CUBIC]
    borders=[cv2.BORDER_REPLICATE, cv2.BORDER_CONSTANT, cv2.BORDER_REFLECT]
    res = cv2.remap(img, flow[:,:,0].astype(np.float32), flow[:,:,1].astype(np.float32), 
                    interps[opt_interp], borderMode = borders[opt_border])
    return res

def coarse2fine_flow(np.ndarray[double, ndim=3] Im1 not None,
                     np.ndarray[double, ndim=3] Im2 not None,
                     double warp_step=1.0, int medfilt_hsz=2, 
                     double alpha=0.01, double ratio=0.75, int minWidth=64,
                     int nOuterFPIterations=7, int nInnerFPIterations=1,
                     int nSORIterations=30, int colType=0, 
                     double flow_scale=1):
    # basic: Horn-Shunck flow estimation
    """
    Input Format:
      double * vx, double * vy, double * warpI2,
      const double * Im1 (range [0,1]), const double * Im2 (range [0,1]),
      double alpha (1), double ratio (0.5), int minWidth (40),
      int nOuterFPIterations (3), int nInnerFPIterations (1),
      int nSORIterations (20),
      int colType (0 or default:RGB, 1:GRAY)
      double flow_scale: flow coarse/fine
    Images Format: (h,w,c): float64: [0,1]
    """
    cdef int h = Im1.shape[0]
    cdef int w = Im1.shape[1]
    cdef int c = Im1.shape[2]
    cdef np.ndarray[double, ndim=2, mode="c"] vx = \
        np.ascontiguousarray(np.zeros((h, w), dtype=np.float64))
    cdef np.ndarray[double, ndim=2, mode="c"] vy = \
        np.ascontiguousarray(np.zeros((h, w), dtype=np.float64))
    cdef np.ndarray[double, ndim=3, mode="c"] warpI2
    if warp_step>0:
         warpI2 = np.ascontiguousarray(np.zeros((h, w, c), dtype=np.float64))
    else: # no warp
         warpI2 = np.ascontiguousarray(np.zeros((1, 1, 1), dtype=np.float64))

    Im1 = np.ascontiguousarray(Im1)
    Im2 = np.ascontiguousarray(Im2)

    Coarse2FineFlowWrapper(&vx[0, 0], &vy[0, 0], &warpI2[0, 0, 0],
                            &Im1[0, 0, 0], &Im2[0, 0, 0],
                            alpha, ratio, minWidth, nOuterFPIterations,
                            nInnerFPIterations, nSORIterations, colType,
                            h, w, c, warp_step, medfilt_hsz, flow_scale)
    return vx, vy, warpI2

def coarse2fine_flow_large(np.ndarray[double, ndim=3] Im1 not None,
                     np.ndarray[double, ndim=3] Im2 not None,
                     double warp_step=1.0, int medfilt_hsz=0,
                     double alpha=1, double ratio=0.5, int minWidth=40,
                     int nOuterFPIterations=3, int nInnerFPIterations=1,
                     int nSORIterations=20, int colType=0, 
                     int tile_size=1024, int flow_pad=10, 
                     int stripe_w=10, int stripe_k=2, double flow_scale=1):
    cdef int h = Im1.shape[0]
    cdef int w = Im1.shape[1]
    cdef int c = Im1.shape[2]

    # divide into tiles
    num_tile = [int(np.ceil(h/float(tile_size))), \
                int(np.ceil(w/float(tile_size)))]
    hh = int(np.ceil(h/float(num_tile[0])))
    ww = int(np.ceil(w/float(num_tile[1])))

    cdef np.ndarray[double, ndim=2, mode="c"] vx = \
        np.ascontiguousarray(np.zeros((hh+flow_pad*2, ww+flow_pad*2), dtype=np.float64))
    cdef np.ndarray[double, ndim=2, mode="c"] vy = \
        np.ascontiguousarray(np.zeros((hh+flow_pad*2, ww+flow_pad*2), dtype=np.float64))
    cdef np.ndarray[double, ndim=3, mode="c"] tmp = \
        np.ascontiguousarray(np.zeros((1, 1, 1), dtype=np.float64))
    cdef np.ndarray[double, ndim=3, mode="c"] Tile1 = \
        np.ascontiguousarray(np.zeros((hh+flow_pad*2, ww+flow_pad*2, c), dtype=np.float64))
    cdef np.ndarray[double, ndim=3, mode="c"] Tile2 = \
        np.ascontiguousarray(np.zeros((hh+flow_pad*2, ww+flow_pad*2, c), dtype=np.float64))

    out_flow = np.zeros((h,w,2), dtype=np.float16)
    for i in range(num_tile[0]):
        # assumption: tile_size > flow_pad
        out_indH = range(i*hh, np.min([h, (i+1)*hh]))
        flo_indH = range(flow_pad, hh+flow_pad)
        # pad the input
        if i != 0:
            im_indH = range(i*hh-flow_pad,i*hh) + out_indH
        else:
            im_indH = range(flow_pad,0,-1) + out_indH
        if i != num_tile[0]-1:
            im_indH += im_indH[-2:-2-flow_pad:-1]
        else: #pad to the same size
            flo_indH = flo_indH[:len(out_indH)] 
            im_indH += im_indH[-2:-2-(hh+2*flow_pad-len(im_indH)):-1]
        for j in range(num_tile[1]):
            print 'tile: %d-%d/%d-%d' %(i,j,num_tile[0],num_tile[1])
            out_indW = range(j*ww, np.min([w, (j+1)*ww]))
            flo_indW = range(flow_pad, ww+flow_pad)
            if j != 0:
                im_indW = range(j*ww-flow_pad,j*ww)+out_indW
            else:
                im_indW = range(flow_pad,0,-1)+out_indW
            if j != num_tile[1]-1:
                im_indW += im_indW[-2:-2-flow_pad:-1]
            else:
                flo_indW = flo_indW[:len(out_indW)] 
                im_indW += im_indW[-2:-2-(ww+2*flow_pad-len(im_indW)):-1]
            np.copyto(Tile1, Im1[im_indH][:,im_indW]) 
            np.copyto(Tile2, Im2[im_indH][:,im_indW]) 
            Coarse2FineFlowWrapper(&vx[0, 0], &vy[0, 0], &tmp[0, 0, 0],
                            &Tile1[0, 0, 0], &Tile2[0, 0, 0],
                            alpha, ratio, minWidth, nOuterFPIterations,
                            nInnerFPIterations, nSORIterations, colType,
                            hh+2*flow_pad, ww+2*flow_pad, c, -1, medfilt_hsz, flow_scale)
            out_flow[np.ix_(out_indH,out_indW,[0])] = vx[flo_indH][:,flo_indW][:,:,None]
            out_flow[np.ix_(out_indH,out_indW,[1])] = vy[flo_indH][:,flo_indW][:,:,None]

    # consolidate intersecting flow
    # median filter horizontal stripe
    # use scipy, no need to make ndarray arrays
    for i in range(1,num_tile[0]):
        flo_stripe = out_flow[(i*hh-stripe_w-stripe_k):i*hh+stripe_w+stripe_k].copy().astype(np.float64)
        medfilt2d(flo_stripe, stripe_k*2+1)
        out_flow[(i*hh-stripe_w):(i*hh+stripe_w)] = \
                flo_stripe[stripe_k:-stripe_k,:][:]
    # median filter vertical stripe
    for i in range(1,num_tile[1]):
        flo_stripe = out_flow[:,(i*ww-stripe_w-stripe_k):(i*ww+stripe_w+stripe_k)].copy().astype(np.float64)
        medfilt2d(flo_stripe, stripe_k*2+1)
        out_flow[:,(i*ww-stripe_w):(i*ww+stripe_w)] = \
                flo_stripe[:,stripe_k:-stripe_k][:]
    
    warpI2 = None
    if warp_step > 0: # warp   
        warpI2 = np.zeros((h,w,c), dtype=np.uint8)
        for i in range(num_tile[0]):
            # assumption: tile_size > flow_pad
            out_indH = range(i*hh, np.min([h, (i+1)*hh]))
            # constant pad at bd
            if i != 0:
                im_indH = range(i*hh-flow_pad,i*hh) + out_indH
            else:
                im_indH = [0]*flow_pad + out_indH
            if i != num_tile[0]-1:
                im_indH += range(i*hh,i*hh+flow_pad)
            else: #pad to the same size
                im_indH += [im_indH[-1]]*flow_pad
            for j in range(num_tile[1]):
                out_indW = range(j*ww, np.min([w, (j+1)*ww]))
                if j != 0:
                    im_indW = range(j*ww-flow_pad,j*ww)+out_indW
                else:
                    im_indW = [0]*flow_pad + out_indW
                if j != num_tile[1]-1:
                    im_indW += range(i*ww,i*ww+flow_pad)
                else: # replicate pad
                    im_indW += [im_indW[-1]]*flow_pad
                warpI2[np.ix_(out_indH,out_indW,range(c))] = np.clip(255*warpback_image(Im2[im_indH][:,im_indW], \
                                                         out_flow[im_indH][:,im_indW]*warp_step, 
                                                         opt_interp=1, opt_border=1).reshape((len(im_indH),len(im_indW),c))[flow_pad:-flow_pad, flow_pad:-flow_pad],0,255)

    return out_flow[:,:,0], out_flow[:,:,1], warpI2

def coarse2fine_flows(np.ndarray[double, ndim=4] Ims not None,
                    double alpha=1, double ratio=0.5, int minWidth=40,
                    int nOuterFPIterations=3, int nInnerFPIterations=1,
                    int nSORIterations=20, int colType=0, 
                    double warp_step=1, int im_step=2, int medfilt_hsz=0, double flow_scale=1):
    """
    Input Format:
      double * vx, double * vy, double * warpI2,
      const double * Im1 (range [0,1]), const double * Im2 (range [0,1]),
      double alpha (1), double ratio (0.5), int minWidth (40),
      int nOuterFPIterations (3), int nInnerFPIterations (1),
      int nSORIterations (20),
      int colType (0 or default:RGB, 1:GRAY)
    Images Format: (n,h,w,c): float64: [0,1]
    """
    cdef int n = Ims.shape[0]
    cdef int h = Ims.shape[1]
    cdef int w = Ims.shape[2]
    cdef int c = Ims.shape[3]
    cdef np.ndarray[double, ndim=4, mode="c"] warpI2
    if warp_step>0:
        warpI2 = np.ascontiguousarray(np.zeros((n-im_step, h, w, c), dtype=np.float64))
    else:
        warpI2 = np.ascontiguousarray(np.zeros((1, 1, 1, 1), dtype=np.float64))

    Ims = np.ascontiguousarray(Ims)
    Coarse2FineFlowWrapper_flows(&warpI2[0, 0, 0, 0],
                            &Ims[0, 0, 0, 0], n,
                            alpha, ratio, minWidth, nOuterFPIterations,
                            nInnerFPIterations, nSORIterations, colType,
                            h, w, c, warp_step, im_step, medfilt_hsz, flow_scale)
    return warpI2
