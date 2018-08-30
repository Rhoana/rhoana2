from setuptools import setup, find_packages

setup(
        name='rh2.waterz',
        version='0.8',
        description='Simple watershed and agglomeration for affinity graphs.',
        url='https://github.com/donglaiw/waterz',
        license='MIT',
        requires=['cython','numpy','scipy', 'mahotas'],
        packages=find_packages(),
        package_data={
            '': [
                'rh2/waterz/*.h',
                'rh2/waterz/*.hpp',
                'rh2/waterz/*.cpp',
                'rh2/waterz/*.pyx',
                'rh2/waterz/backend/*.hpp',
            ]
        },
        include_package_data=True,
        zip_safe=False
)
