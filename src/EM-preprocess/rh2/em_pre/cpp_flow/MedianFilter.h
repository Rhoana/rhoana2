#include <stdlib.h>
#include <algorithm>

void copyToBuffer(double *I, int row, int col, int c, 
        int win_hsize, int ww, int cc, double *buffer);

void padImage(double *im, double *im_p, 
        int hh, int ww, int cc, int win_hsize);

void medianFilter(double *im, int mHeight, int imWidth, 
        int nChannels, int win_hsize);
