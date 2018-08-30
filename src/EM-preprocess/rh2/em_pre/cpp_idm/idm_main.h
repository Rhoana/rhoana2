#include <float.h>
#include <stdint.h>
#include <stdio.h>

void idm_dist(float *img1, float *img2, float *out, 
        int im_row, int im_col, int im_chan, 
        int patch_sz, int warp_sz, int step, int metric);
