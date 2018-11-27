from Cython.Distutils import build_ext
from distutils.sysconfig import get_python_inc
from setuptools import setup, Extension 
import numpy as np
import os

def getExt():
    # extensions under segmenation/
    return [
        Extension(
            name='em_segLib.seg_dist',
            sources=['em_segLib/seg_dist.pyx',
                     'em_segLib/cpp/seg_dist/cpp-distance.cpp'],
            extra_compile_args=['-O4', '-std=c++0x'],
            language='c++'
        ),
        Extension(
            name='em_segLib.seg_core',
            sources=['em_segLib/seg_core.pyx',
                     'em_segLib/cpp/seg_core/cpp-seg2seg.cpp',
                     'em_segLib/cpp/seg_core/cpp-seg2gold.cpp',
                     'em_segLib/cpp/seg_core/cpp-seg_core.cpp'],
            extra_compile_args=['-O4', '-std=c++0x'],
            language='c++'
        ),
        Extension(
            name='em_segLib.seg_eval',
            sources=['em_segLib/seg_eval.pyx',
                     'em_segLib/cpp/seg_eval/cpp-comparestacks.cpp'],
            extra_compile_args=['-O4', '-std=c++0x'],
            language='c++'
        ),
        Extension(
            name='em_segLib.seg_malis',
            sources=['em_segLib/seg_malis.pyx',
                     'em_segLib/cpp/seg_malis/cpp-malis_core.cpp'],
            extra_compile_args=['-O4', '-std=c++0x'],
            language='c++'
        )
    ]
def getInclude():
    dirName = get_python_inc()
    return [dirName, os.path.dirname(dirName), np.get_include()]
if __name__=='__main__':
    # python setup.py develop install

    setup(name='em_segLib',
       version='1.0',
       install_requires=['cython','scipy','boost'],
       cmdclass = {'build_ext': build_ext}, 
       include_dirs = getInclude(), 
       packages=['em_segLib'],
       ext_modules = getExt())


