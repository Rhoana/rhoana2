from setuptools import setup, Extension
from Cython.Distutils import build_ext
import numpy as np
import glob

NAME = "em_pre"
VERSION = "0.1"
DESCR = "cython implementation of Deformation Models for Image Recognition"
REQUIRES = ['cython','numpy']

AUTHOR = "Donglai Wei"
EMAIL = "weiddoonngglai@gmail.com"
LICENSE = "Apache 2.0"
SRC_DIR = "em_pre"
URL = 'https://github.com/donglaiw/IDM'
PACKAGES = [SRC_DIR]
EXTENSIONS = []

EXTENSIONS += [Extension(SRC_DIR + ".idm",
                  [SRC_DIR + "/cpp_idm/idm_main.c", SRC_DIR + "/idm.pyx"],
                  language='c',
                  include_dirs=[np.get_include()])]

flow_files = [SRC_DIR +'/pyflow.pyx']
flow_files.extend(glob.glob(SRC_DIR +"/cpp_flow/*.cpp"))
EXTENSIONS += [Extension(SRC_DIR + ".pyflow",
                  flow_files,
                  extra_compile_args=['-fPIC','-static'],
                  language='c++',
                  include_dirs=[np.get_include()])]

if __name__ == "__main__":
    # python setup.py develop install
    setup(install_requires=REQUIRES,
          packages=PACKAGES,
          zip_safe=False,
          url=URL,
          name=NAME,
          version=VERSION,
          description=DESCR,
          author=AUTHOR,
          author_email=EMAIL,
          license=LICENSE,
          cmdclass={"build_ext": build_ext},
          ext_modules=EXTENSIONS
          )
