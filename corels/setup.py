import os
from numpy.distutils.misc_util import Configuration
import numpy as np

def configuration():
    description = 'Python binding of the CORELS algorithm'
    long_description = description
    with open('README.txt') as f:
        long_description = f.read()

    config = Configuration('corels')
    
    args = ['-O3', '-DGMP', '-std=c++11']
    libraries = ['gmp']
    
    if os.name == 'posix':
        libraries.append('m')
    
    config.add_extension('_corels',
                    sources = ['_corels.c', 'src/utils.c',
                    'src/corels/run.cc', 'src/corels/pmap.cc', 
                    'src/corels/utils.cc', 'src/corels/corels.cc', 
                    'src/corels/cache.cc', 'src/corels/rulelib.c'],
                    libraries = libraries,
                    include_dirs = ['src/', 'src/corels/', np.get_include()],
		            language = "C++",
                    extra_compile_args = args)

    config = config.todict()
    config['version'] = '1.1.4'
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
