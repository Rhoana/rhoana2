// This is a wrapper for Ce Liu's Coarse2Fine optical flow implementation.
// It converts the contiguous image array to the format needed by the optical
// flow code. Handling conversion in the wrapper makes the cythonization
// simpler.
// Author: Deepak Pathak (c) 2016

// override-include-guard
#include "Image.h"
#include "OpticalFlow.h"

extern void Coarse2FineFlowWrapper(double * vx, double * vy, double * warpI2,
                              const double * Im1, const double * Im2,
                              double alpha, double ratio, int minWidth,
                              int nOuterFPIterations, int nInnerFPIterations,
                              int nSORIterations, int colType,
                              int h, int w, int c, 
                              double warp_step, int medfilt_hsz, double flow_scale);
extern void Coarse2FineFlowWrapper_flows(double * warpI2,
                                  const double * Ims, int nIm,
                                  double alpha, double ratio, int minWidth,
                                  int nOuterFPIterations, int nInnerFPIterations,
                                  int nSORIterations, int colType,
                                  int h, int w, int c, 
                                  double warp_step, int im_step, int medfilt_hsz, double flow_scale);

