import os
import numpy as np
from numpy.distutils.misc_util import Configuration

def configuration():
    description = 'Python binding of the CORELS algorithm'
    long_description = description
    with open('README.txt') as f:
        long_description = f.read()

    version = '1.1.12'
    with open('VERSION.txt') as f:
        version = f.read()

    config = Configuration('corels')
    
    cpp_args = ['-O3', '-DGMP', '-std=c++11']
    libraries = ['gmp']
    
    if os.name == 'posix':
        libraries.append('m')
    
    config.add_extension('_corels',
                    sources = ['_corels.cpp', 'src/utils.cpp', 'src/corels/rulelib.cpp',
                    'src/corels/run.cpp', 'src/corels/pmap.cpp', 
                    'src/corels/utils.cpp', 'src/corels/corels.cpp', 'src/corels/cache.cpp'],
                    libraries = libraries,
                    include_dirs = ['src/', 'src/corels/', np.get_include()],
		            language = "c++",
                    extra_compile_args = cpp_args)
    
    config = config.todict()
    config['version'] = version
    config['author'] = 'Vassilios Kaxiras'
    config['author_email'] = 'vassilioskaxiras@gmail.com'
    config['description'] = description
    config['long_description'] = long_description
    config['url'] = 'https://github.com/fingoldin/pycorels'
    config['classifiers'] = (
        "Programming Language :: C++",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    )

    return config

if __name__ == "__main__":
    from numpy.distutils.core import setup
    setup(**configuration())
