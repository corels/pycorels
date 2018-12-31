import setuptools
import numpy as np
import os

pycorels = setuptools.Extension('_corels',
                    sources = ['corels/_corels.c', 'corels/src/utils.c',
                    'corels/src/corels/run.cc', 'corels/src/corels/pmap.cc', 
                    'corels/src/corels/utils.cc', 'corels/src/corels/corels.cc', 
                    'corels/src/corels/cache.cc', 'corels/src/corels/rulelib.c'],
                    libraries = ['gmp', 'm'],
                    include_dirs = ['corels/src/', 'corels/src/corels/', np.get_include()],
		            extra_compile_args = ["-DGMP"])

long_description = open("README.txt").read()

setuptools.setup(name = 'corels',
       version = '1.0.15',
       author = 'Vassilios Kaxiras',
       author_email = 'vassilioskaxiras@gmail.com',
       description = 'Python binding of the CORELS algorithm',
       long_description = long_description,
       url="https://github.com/fingoldin/pycorels",
       setup_requires = ['numpy>=0.x'],
       packages = ['corels'],
       ext_modules = [pycorels],
       classifiers=(
            "Programming Language :: C++",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent"
       )
)
