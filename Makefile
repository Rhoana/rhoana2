# 
#
#
clean:
	rm -rf ./src/*/build/ ./src/*/dist/ ./src/*/*.egg-info/	\
		./src/*/rh2/__init__.py*

install:
	./install.sh

