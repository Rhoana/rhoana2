#!/bin/bash


function install_pkg {
    echo "__path__ = __import__('pkgutil').extend_path(__path__, __name__)" > \
        src/$1/rh2/__init__.py;
    cd src/$1/;
    python setup.py install;
    cd ../..;
}

export -f install_pkg

install_pkg EM-preprocess
install_pkg EM-segLib
install_pkg waterz
install_pkg zwatershed

