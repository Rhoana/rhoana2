# 
#
#

packages =EM-preprocess EM-segLib waterz zwatershed
cp_init_file = 

define install_pkg                                                   
    echo "__path__ = __import__('pkgutil').extend_path(__path__, __name__)" > \ 
    ./src/$(1)/rh2/__init__.py                                                 
    cd ./src/$(1)/                                                                 
	python setup.py install                                                    
	cd ../..
endef

clean:
	rm -rf ./src/*/build/ ./src/*/dist/ ./src/*/*.egg-info/	\
		./src/*/rh2/__init__.py*

install:
	$(foreach packages, $(package), $(call install_pkg,$(package)))
