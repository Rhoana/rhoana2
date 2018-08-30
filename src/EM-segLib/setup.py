from Cython.Distutils import build_ext
from distutils.sysconfig import get_python_inc
from setuptools import setup, Extension, find_packages
import numpy as np
import os
PKG_NME = 'rh2.em_segLib'
SRC_DIR = 'rh2/em_segLib'

def getExt():
    # extensions under segmenation/
    return [
        Extension(
            name= PKG_NME + '.seg_dist',
            sources=[ SRC_DIR + '/seg_dist.pyx',
                      SRC_DIR + '/cpp/seg_dist/cpp-distance.cpp'],
            extra_compile_args=['-O4', '-std=c++0x'],
            language='c++'
        ),
        Extension(
            name= PKG_NME + '.seg_core',
            sources=[ SRC_DIR + '/seg_core.pyx',
                      SRC_DIR + '/cpp/seg_core/cpp-seg2seg.cpp',
                      SRC_DIR + '/cpp/seg_core/cpp-seg2gold.cpp',
                      SRC_DIR + '/cpp/seg_core/cpp-seg_core.cpp'],
            extra_compile_args=['-O4', '-std=c++0x'],
            language='c++'
        ),
        Extension(
            name= PKG_NME + '.seg_eval',
            sources=[ SRC_DIR + '/seg_eval.pyx',
                      SRC_DIR + '/cpp/seg_eval/cpp-comparestacks.cpp'],
            extra_compile_args=['-O4', '-std=c++0x'],
            language='c++'
        ),
        Extension(
            name= PKG_NME + '.seg_malis',
            sources=[ SRC_DIR + '/seg_malis.pyx',
                     SRC_DIR + '/cpp/seg_malis/cpp-malis_core.cpp'],
            extra_compile_args=['-O4', '-std=c++0x'],
            language='c++'
        )
    ]
def getInclude():
    dirName = get_python_inc()
    return [dirName, os.path.dirname(dirName), np.get_include()]
if __name__=='__main__':
    # python setup.py develop install

    setup(name=PKG_NME,
       version='1.0',
       install_requires=['cython','scipy','boost'],
       cmdclass = {'build_ext': build_ext}, 
       include_dirs = getInclude(), 
       packages=find_packages(),
       ext_modules = getExt())


