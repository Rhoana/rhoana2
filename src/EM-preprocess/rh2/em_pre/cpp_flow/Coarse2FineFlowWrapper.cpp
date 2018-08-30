// This is a wrapper for Ce Liu's Coarse2Fine optical flow implementation.
// It converts the contiguous image array to the format needed by the optical
// flow code. Handling conversion in the wrapper makes the cythonization
// simpler.
// Author: Deepak Pathak (c) 2016

#include "Coarse2FineFlowWrapper.h"
using namespace std;

void Coarse2FineFlowWrapper(double * vx, double * vy, double * warpI2,
                              const double * Im1, const double * Im2,
                              double alpha, double ratio, int minWidth,
                              int nOuterFPIterations, int nInnerFPIterations,
                              int nSORIterations, int colType,
                              int h, int w, int c, 
                              double warp_step, int medfilt_hsz, double flow_scale) {
  DImage ImFormatted1, ImFormatted2;
  DImage vxFormatted, vyFormatted, warpI2Formatted;

  // format input in the format needed by backend
  ImFormatted1.allocate(w, h, c);
  ImFormatted2.allocate(w, h, c);
  memcpy(ImFormatted1.pData, Im1, h * w * c * sizeof(double));
  memcpy(ImFormatted2.pData, Im2, h * w * c * sizeof(double));
  ImFormatted1.setColorType(colType);
  ImFormatted2.setColorType(colType);
  vxFormatted.allocate(w, h);
  vyFormatted.allocate(w, h);

  // call optical flow backend
  //cout<<"do 1"<<endl;
  //cout<<h<<","<<w<<","<<c<<endl;
  //cout<<alpha<<","<<ratio<<","<<minWidth<<","<<nOuterFPIterations<<","<<nInnerFPIterations<<","<<nSORIterations<<","<<warp_step<<","<<medfilt_hsz<<","<<flow_scale<<endl;
  OpticalFlow::Coarse2FineFlow(vxFormatted, vyFormatted, warpI2Formatted,
                                ImFormatted1, ImFormatted2,
                                alpha, ratio, minWidth,
                                nOuterFPIterations, nInnerFPIterations,
                                nSORIterations, warp_step, medfilt_hsz, flow_scale);

  //cout<<"do 2"<<endl;
  // copy formatted output to a contiguous memory to be returned
  memcpy(vx, vxFormatted.pData, h * w * sizeof(double));
  memcpy(vy, vyFormatted.pData, h * w * sizeof(double));
  if(warp_step>0){
    //cout<<"do 3"<<endl;
    memcpy(warpI2, warpI2Formatted.pData, h * w * c * sizeof(double));
    warpI2Formatted.clear();
  }

  // clear c memory
  ImFormatted1.clear();
  ImFormatted2.clear();
  vxFormatted.clear();
  vyFormatted.clear();
  return;
}

void Coarse2FineFlowWrapper_flows(double * warpI2,
                              const double * Ims, int nIm,
                              double alpha, double ratio, int minWidth,
                              int nOuterFPIterations, int nInnerFPIterations,
                              int nSORIterations, int colType,
                              int h, int w, int c, 
                              double warp_step, int im_step, int medfilt_hsz, double flow_scale) {
  DImage ImFormatted1, ImFormatted2;
  DImage vxFormatted, vyFormatted, warpI2Formatted;

  // format input in the format needed by backend
  ImFormatted1.allocate(w, h, c);
  ImFormatted2.allocate(w, h, c);
  ImFormatted1.setColorType(colType);
  ImFormatted2.setColorType(colType);
  vxFormatted.allocate(w, h);
  vyFormatted.allocate(w, h);
  warpI2Formatted.allocate(w, h, c);

  size_t im_size = h * w * c ;
  
  for (int i=0;i<nIm-im_step;i++){
      cout<<"warp image: "<<(i+1)<<"/"<<nIm-1<<endl;
      memcpy(ImFormatted1.pData, Ims + i*im_size, im_size* sizeof(double));
      memcpy(ImFormatted2.pData, Ims + (i+im_step)*im_size, im_size* sizeof(double));
      // call optical flow backend
      OpticalFlow::Coarse2FineFlow(vxFormatted, vyFormatted, warpI2Formatted,
                                    ImFormatted1, ImFormatted2,
                                    alpha, ratio, minWidth,
                                    nOuterFPIterations, nInnerFPIterations,
                                    nSORIterations, warp_step, medfilt_hsz, flow_scale);

      // copy formatted output to a contiguous memory to be returned
      memcpy(warpI2 + i*im_size, warpI2Formatted.pData, im_size* sizeof(double));
  }

  // clear c memory
  ImFormatted1.clear();
  ImFormatted2.clear();
  vxFormatted.clear();
  vyFormatted.clear();
  warpI2Formatted.clear();

  return;
}
