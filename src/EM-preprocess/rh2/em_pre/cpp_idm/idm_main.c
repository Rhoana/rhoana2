#include "idm_main.h"
#include <math.h>

float patch_distance (int A_x,int A_y, int B_x, int B_y, int im_row, int im_col, int im_chan,
        int patch_sz, float *img1, float *img2, int metric){
    float dist=0,temp_h;
    int c,x,y,count=0;
    /* only move around patchB */
    int pre = im_col*im_chan;
    float patch_sum=0;

    switch(metric){
        case 0: // L1
            for(y=-patch_sz; y<=patch_sz; y++){
                for(x=-patch_sz; x<=patch_sz; x++){
                    if((A_x + x)>=0 && (A_y + y)>=0 && (A_x + x)<im_row && (A_y + y)<im_col
                            && (B_x + x)>=0 && (B_y + y)>=0 && (B_x + x)<im_row && (B_y + y)<im_col){
                        for(c=0; c<im_chan; c++){
                            temp_h = img1[(A_x + x)*pre + (A_y + y)*im_chan + c] -
                                    img2[(B_x + x)*pre + (B_y + y)*im_chan + c];
                            dist += fabsf(temp_h);
                            //dist+=temp_h*temp_h;
                            count++;
                        }
                    }
                }
            }
            break;
        case 1: // relative L1
            for(y=-patch_sz; y<=patch_sz; y++){
                for(x=-patch_sz; x<=patch_sz; x++){
                    if((A_x + x)>=0 && (A_y + y)>=0 && (A_x + x)<im_row && (A_y + y)<im_col
                            && (B_x + x)>=0 && (B_y + y)>=0 && (B_x + x)<im_row && (B_y + y)<im_col){
                        for(c=0; c<im_chan; c++){
                            temp_h = img1[(A_x + x)*pre + (A_y + y)*im_chan + c] -
                                    img2[(B_x + x)*pre + (B_y + y)*im_chan + c];
                            dist += fabsf(temp_h);
                            patch_sum += img1[(A_x + x)*pre + (A_y + y)*im_chan + c];
                            //dist+=temp_h*temp_h;
                            count++;
                        }
                    }
                }
            }
            dist = dist/patch_sum;
            break;
    }
    return dist/count;
}

void idm_dist(float *img1, float *img2, float *dis, 
        int im_row, int im_col, int im_chan, 
        int patch_sz, int warp_sz, int step, int metric){
    /* assume same size img */
    float best_dis;
    float temp;
    int x,y,xx,yy;
    
    /* 3) Return distance */
    int count=0;
    for (x=0; x<im_row; x+=step){
        for (y=0; y<im_col; y+=step){
                best_dis=FLT_MAX;
                for(xx=x-warp_sz; xx<=x+warp_sz; xx++){
                    for(yy=y-warp_sz; yy<=y+warp_sz; yy++){
                        if(xx >= 0 && yy >= 0 && xx < im_row && yy < im_col){
                            temp = patch_distance(x, y, xx, yy, im_row, im_col, im_chan, 
                                    patch_sz, img1, img2, metric);
                            if(temp<best_dis){
                                best_dis = temp;
                            }
                        }
                    }
                }
                dis[count] = best_dis;
                count++;
            }
        }
}
