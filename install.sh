#!/bin/bash
function install_pkg {
    echo "__path__ = __import__('pkgutil').extend_path(__path__, __name__)" > \
    ./src/$1/rh2/__init__.py;
    cd ./src/$1/;
	pip install -r ./rh2/requirements.txt .;
	cd ../..;
}

export -f install_pkg
packages=( waterz zwatershed EM-preprocess EM-segLib )
for package in "${packages[@]}"
do
    install_pkg $package
done
