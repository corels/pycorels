from __future__ import print_function, division, with_statement
import os
import numpy as np
import sys
from distutils.core import setup
from misc_util import Configuration

def configuration(gmp):
    description = 'Python binding of the CORELS algorithm'
    long_description = description
    with open('README.txt') as f:
        long_description = f.read()

    version = '1.1.15'

    config = Configuration('corels')
   
    cpp_args = []
    libraries = []
    
    if os.name != "nt":
        cpp_args = ['-Wall', '-O3', '-std=c++11']
    
    if os.name == 'posix':
        libraries = ['m']
    
    if gmp:
        cpp_args.append('-DGMP')
        libraries.append('gmp')
    
    sources = ['_corels.cpp', 'src/utils.cpp', 'src/corels/rulelib.cpp',
        'src/corels/run.cpp', 'src/corels/pmap.cpp', 
        'src/corels/utils.cpp', 'src/corels/corels.cpp', 'src/corels/cache.cpp',
        'src/corels/time.cpp']
    
    config.add_extension('_corels',
                    sources = sources,
                    libraries = libraries,
                    include_dirs = ['src/', 'src/corels/', np.get_include()],
                    language = "c++",
                    extra_compile_args = cpp_args)
    
    config = config.todict()
    config['version'] = version
    config['author'] = 'Vassilios Kaxiras'
    config['author_email'] = 'vassilioskaxiras@gmail.com'
    config['description'] = description
    config['install_requires'] = ['numpy']
    config['long_description'] = long_description
    config['url'] = 'https://github.com/fingoldin/pycorels'
    config['package_data'] = {'': ['VERSION.txt']}
    config['classifiers'] = (
        "Programming Language :: C++",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    )

    return config

if __name__ == "__main__":
    try:
        setup(**configuration(True))
    except:
        setup(**configuration(False))
        
