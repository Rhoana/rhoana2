#!/usr/bin/env python
from Tkinter import *
#import Image, ImageTk
from PIL import Image, ImageTk

# for installation
# conda install h5py numpy pillow tk

import os, sys
import h5py
from numpy import array, unique, ravel, zeros, concatenate, expand_dims, uint8, amax, multiply, int32
from string import rjust
import pdb

import random
import colorsys

def get_random_color():
    hv,sv,vv = (random.uniform(0, 6.283), random.uniform(0.3, 1.0), random.uniform(0.3, 0.8))
    r,g,b = colorsys.hsv_to_rgb(hv, sv, vv)
    return r*255,g*255,b*255
  
def seg2overlay(seg):
    seg1d = seg.ravel()
    useg_ids = unique(seg1d)
    
    overlayr = zeros(seg.shape).astype(int)
    overlayg = zeros(seg.shape).astype(int)
    overlayb = zeros(seg.shape).astype(int)
    ovb1d = overlayb.ravel()
    ovr1d = overlayr.ravel()
    ovg1d = overlayg.ravel()
    
    max_id = int32(amax(useg_ids))
    cmapr = zeros(max_id+1)
    cmapg = zeros(max_id+1)
    cmapb = zeros(max_id+1)
    
    for i in range(len(useg_ids)):
        useg_id = useg_ids[i]
        rv,gv,bv = get_random_color()
        cmapr[useg_id] = int(rv)
        cmapg[useg_id] = int(gv)
        cmapb[useg_id] = int(bv)
    
    return cmapr, cmapg, cmapb
  

class Viewer:
    def __init__(self, master, cmapr, cmapg, cmapb, imvol, segvol, title='seg'):
        self.top = master
        self.index = 0
        self.cmapr = cmapr
        self.cmapg = cmapg
        self.cmapb = cmapb
        self.segvol = segvol
        self.curr_highlighted = -1
        self.images = imvol
        self.numI = self.images.shape[0]
        self.title = Label(text=title)
        self.title.pack(expand=True)

        #display first image
        self.alpha = 0.3
        self.prev_alpha = self.alpha
        im = self.blend(self.images[0,:,:], self.segvol[0,:,:])
    
        self.size = im.size
        self.tkimage = ImageTk.PhotoImage(im)
        tfr = Frame(master)
        tfr.pack()
        
        self.lbl = Label(tfr, image=self.tkimage)
        self.lbl.grid(row=0, column=0)
        self.lbl.bind("<Button-1>", self.highlight)
        
        fr = Frame(master)
        fr.pack(side='bottom',  expand=1, fill='x')
        # the button frame
        back = Button(fr, text="Up (u)", command=lambda : self.nextframe(-1))
        back.grid(row=0, column=0, sticky="w", padx=4, pady=4)
        
        ilabel = Label(fr, text="image number:")
        ilabel.grid(row=0, column=1, sticky='w',  pady=4)
        self.evar = IntVar()
        self.evar.set(1)
        
        entry = Entry(fr, textvariable=self.evar)
        entry.grid(row=0, column=2, pady=4)
        entry.bind('<Return>', self.getimgnum)
        
        next = Button(fr, text="Down (d)", command=lambda : self.nextframe(1))
        next.grid(row=0, column=3,  padx=4, pady=4)
        
        master.bind_all('<Key>', self.keypressed)
        
    def blend(self, fib_im, seg_im):
        mask = seg_im>0 
        masked_im = multiply(fib_im,1-mask)
        
        overlayr = multiply(self.cmapr[seg_im],mask)
        overlayg = multiply(self.cmapg[seg_im],mask)
        overlayb = multiply(self.cmapb[seg_im],mask)
        
        imarr = (1-self.alpha)*fib_im +  self.alpha*(overlayr) + self.alpha*masked_im
        imarr = expand_dims(imarr, axis = 2)
        imarr = concatenate((imarr, expand_dims((1-self.alpha)*fib_im +  self.alpha*(overlayg) + self.alpha*masked_im,axis=2)), axis = 2)
        imarr = concatenate((imarr, expand_dims((1-self.alpha)*fib_im +  self.alpha*(overlayb) + self.alpha*masked_im,axis=2)), axis = 2)
        im = Image.fromarray(uint8(imarr))
        return im
      
    def nextframe(self,i=1, imgnum=-1):
        if imgnum == -1:
            self.index += i
        else:
            self.index = imgnum - 1
        if self.index >= self.numI:
            self.index = self.numI-1
        elif self.index < 0:
            self.index = 0
        
        self.evar.set(self.index+1)
        
        fib_im = self.images[self.index,:,:]
        im = self.blend(fib_im, self.segvol[self.index,:,:])
        self.tkimage.paste(im)

    def getimgnum(self, event=None):
        self.nextframe(imgnum=self.evar.get())
    
    def highlight(self, event):
        highlighted_seg_id = self.segvol[self.index, event.y, event.x]
        if highlighted_seg_id == 0:
            return
        #pdb.set_trace()
        
        if (self.curr_highlighted >= 0): # restore segment already highlighted
            self.cmapb[self.curr_highlighted] = self.highlight_prev_colorb
            self.cmapg[self.curr_highlighted] = self.highlight_prev_colorg
            self.cmapr[self.curr_highlighted] = self.highlight_prev_colorr
        
        if (self.curr_highlighted == highlighted_seg_id):
            self.curr_highlighted = -1
            self.nextframe(0)
            return
            
        # highlight new segment
        self.curr_highlighted = highlighted_seg_id  
        self.highlight_prev_colorr = self.cmapr[self.curr_highlighted]
        self.highlight_prev_colorg = self.cmapg[self.curr_highlighted]
        self.highlight_prev_colorb = self.cmapb[self.curr_highlighted]
        print "Highlighted region: {0}".format(self.curr_highlighted)
        self.cmapr[self.curr_highlighted] = 255
        self.cmapg[self.curr_highlighted] = 255
        self.cmapb[self.curr_highlighted] = 255
        
        self.nextframe(0)
    
    def exclusive_highlight(self):
        self.cmapr = zeros(self.cmapr.shape)
        self.cmapg = zeros(self.cmapg.shape)
        self.cmapb = zeros(self.cmapb.shape)
        
        print "Highlighted region: {0}".format(self.curr_highlighted)
        self.cmapr[self.curr_highlighted] = 255
        self.cmapg[self.curr_highlighted] = 255
        self.cmapb[self.curr_highlighted] = 0
        
        self.nextframe(0)
    
    def keypressed(self,event):
        if event.char == 'd':
            self.nextframe(1)
        elif event.char == 'u':
            self.nextframe(-1)
        elif event.char =='f':
            self.toggle_alpha()
        elif event.char =='r':
            self.exclusive_highlight()
        elif event.char =='s':
            self.save_image()
        elif event.char =='m':
            self.save_all_images()
        elif event.char =='+':
            self.increase_alpha()
        elif event.char =='-':
            self.decrease_alpha()

    def increase_alpha(self):
        self.alpha = self.alpha*1.25
        self.nextframe(0)

    def decrease_alpha(self):
        self.alpha = self.alpha*0.8
        self.nextframe(0)
    
    def toggle_alpha(self):
        if self.alpha > 0:
           self.prev_alpha = self.alpha
           self.alpha = 0
        else:
           self.alpha = self.prev_alpha

        self.nextframe(0)                   

    def save_image(self):
        idxstr = str(self.index)
        idxstr = idxstr.rjust(5,'0')
        fib_im = self.images[self.index,:,:]
        im = self.blend(fib_im, self.segvol[self.index,:,:])
        imname = 'composite.'+ idxstr +'.png'
        im.save(imname)
    
    def save_all_images(self):
        #pdb.set_trace()
        output_dir='output-images'
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        for index in range(self.images.shape[0]):
            idxstr = str(index)
            idxstr = idxstr.rjust(5,'0')
            fib_im = self.images[index,:,:]
            im = self.blend(fib_im, self.segvol[index,:,:])
            imname = output_dir+ '/composite.'+ idxstr +'.png'
            im.save(imname)
        
# --------------------------------------------------------------------
if __name__ == "__main__":
    if not sys.argv[1:]:
        print "Usage: viewh5.py img-h5file img-h5_dataset  seg-h5file seg-h5_dataset do_trans"
        sys.exit()
    
    im_fn = sys.argv[1]
    im_dset = sys.argv[2]
    seg_fn = sys.argv[3]
    seg_dset = sys.argv[4]
    do_trans = False
    if len(sys.argv)>5:
        do_trans = sys.argv[5]=='1'
    
    im = array(h5py.File(im_fn,'r')[im_dset])
    seg = array(h5py.File(seg_fn,'r')[seg_dset])
    if do_trans:
        im = im.transpose((3,2,1))
        seg = seg.transpose((3,2,1))
    
    print "opened volume with {0} regions".format(unique(seg).shape[0])
    cmapr, cmapg, cmapb = seg2overlay(seg)

    root = Tk()
    app = Viewer(root, cmapr, cmapg, cmapb, im, seg, seg_fn)
    root.mainloop() 
