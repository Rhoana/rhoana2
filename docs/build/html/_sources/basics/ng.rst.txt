L1. 3D Volume Visualization
=============================

We use `neuroglancer <https://github.com/google/neuroglancer>`_ for 3D image stack and segmentation visualization
    
#. (Windows Only) Install `Microsoft Visual C++
   <https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2017>`_ (Community version)

#. Install Python Package Manager (`Miniconda <https://conda.io/en/latest/miniconda.html>`_)

#. Install Neuroglancer
    
    .. code-block:: none 

        conda create -n ng python=3.7
        conda activate ng
        conda install pip imageio h5py numpy tornado=5.1.1
        pip install neuroglancer==1.1.6
        # optional for jupyter kernel
        conda install ipykernel
        python -m ipykernel install --user --name ng --display-name "ng"

#. Example: 

   #. (Optional) `Download <http://hp03.mindhackers.org/rhoana_product/dataset/snemi.zip>`_ SNEMI neuron segmentation dataset
   
   #. `python -i THIS_FILE.py` (in "ng" conda env) or open a jupyter notebook (choose "ng" kernel)

    .. code-block:: python
        
        import neuroglancer
        import numpy as np
        import imageio

        ip='localhost' # or public IP of the machine for sharable display
        port=98092 # change to an unused port number
        neuroglancer.set_server_bind_address(bind_address=ip,bind_port=port)
        viewer=neuroglancer.Viewer()

        # SNEMI
        D0='path/to/folder/'
        res=[6,6,30]; # resolution of the data dim (x,y,z)
        print('load im and gt seg')
        # 3d vol dim: z,y,x 
        im = imageio.volread(D0+'image/train-input.tif')
        gt = imageio.volread(D0+'seg/train-labels.tif').astype(np.uint16)
        
        def ngLayer(data,res,oo=[0,0,0],tt='segmentation'):
            return neuroglancer.LocalVolume(data,volume_type=tt,voxel_size=res,offset=oo)

        with viewer.txn() as s:
            s.layers.append(name='im',layer=ngLayer(im,res,tt='image'))
            s.layers.append(name='gt',layer=ngLayer(gt,res))

        print(viewer)

   #. (Optional) Create 3D volume in h5 from 2D slices

    .. code-block:: python
        
        import numpy as np
        from imageio import imread
        import glob

        def folder2Vol(Do,dt=np.uint16,maxF=-1,ratio=[1,1,1],fns=None):
            # ratio: downsample ratio for (z,y,x) dimension
            if fns is None:
                fns = sorted(glob.glob(Do+'*.png'))
            numF = len(fns)
            if maxF>0:
                numF = min(numF,maxF)
            numF = numF//ratio[0]
            sz = np.array(imread(fns[0]).shape)[:2]//ratio[1:]

            vol = np.zeros((numF,sz[0],sz[1]), dtype=dt)
            for zi in range(numF):
                if os.path.exists(fns[zi*ratio[0]]):
                    tmp = imread(fns[zi*ratio[0]])
                    if tmp.ndim==3:
                        tmp = tmp[:,:,0]
                    vol[zi] = tmp[::ratio[1],::ratio[2]]
            return vol
        # read a folder of image files into vol at full resolution 
        vol = folder2Vol(Do)
        # read the first 10 images in a folder
        vol = folder2Vol(Do, maxF=10)
        # read a folder of image files into vol with downsampled (z,y,x) resolution 
        vol = folder2Vol(Do, ratio=[2,2,2])
