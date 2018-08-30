#include "MedianFilter.h"

void padImage(double *im, double *im_p, int hh, int ww, int cc, int win_hsize){
    // reflect padding 
    int imPre_p = cc*(ww+2*win_hsize);
    int imPre = cc*ww;
    // valid + top-left
    for (int y=0; y < hh+win_hsize; y++) {
        for (int x=0; x < ww+win_hsize; x++) {
            for (int c=0; c < cc; c++) {
                im_p[y*imPre_p + x*cc + c] = 
                    im[abs(y-win_hsize)*imPre + abs(x-win_hsize)*cc + c];
            }
        }
    }
    // bottom
    for (int y=hh+win_hsize; y < hh+2*win_hsize; y++) {
        for (int x=0; x < ww+win_hsize; x++) {
            for (int c=0; c < cc; c++) {
                im_p[y*imPre_p + x*cc + c] = 
                    im_p[(2*hh+2*win_hsize-2-y)*imPre_p + x*cc + c];
            }
        }
    }
    // right
    for (int y=0; y < hh+2*win_hsize; y++) {
        for (int x=ww+win_hsize; x < ww+2*win_hsize; x++) {
            for (int c=0; c < cc; c++) {
                im_p[y*imPre_p + x*cc + c] = 
                    im_p[y*imPre_p + (2*ww+2*win_hsize-2-x)*cc + c];
            }
        }
    }
}
void copyToBuffer(double *I, int row, int col, int c, int win_hsize, int ww, int cc, double *buffer) {
    int index = 0;
    int pre=ww*cc;
    for (int y=-win_hsize; y<=win_hsize; y++) {
        for (int x=-win_hsize; x<=win_hsize; x++) {
            buffer[index] = I[(row+y)*pre+(col+x)*cc+c];
            index++;
        }
    }
}
void medianFilter(double *im, int imHeight, int imWidth, int nChannels, int win_hsize){
    // h,w,c
    int win_size = 2*win_hsize+1;
    int win_size2 = win_size*win_size;
    int win_size_mid = win_hsize*(win_size+1);
    double *buffer = new double[win_size2];
    
    // pad image 
    int imHeight_p = imHeight+2*win_hsize;
    int imWidth_p = imWidth+2*win_hsize;
    double *im_pad = new double[imHeight_p * imWidth_p * nChannels];
    padImage(im, im_pad, imHeight, imWidth, nChannels, win_hsize);

    // median filter
    int index = 0;
    for (int y=win_hsize; y < imHeight+win_hsize; y++) {
        for (int x=win_hsize; x < imWidth+win_hsize; x++) {
            for (int c=0; c < nChannels; c++) {
                copyToBuffer(im_pad, y, x, c, win_hsize, imWidth_p, nChannels, buffer);
                std::sort(buffer, buffer + win_size2);
                im[index]=buffer[win_size_mid];
                index++;
            }
        }
    }
    delete buffer;
    delete im_pad;
}
