import setuptools
import numpy as np
import os
from Cython.Build import cythonize

pycorels = setuptools.Extension('libcorels',
                    sources = ['libcorels.pyx', 'src/utils.c', 'src/corels/src/run.cc', 'src/corels/src/pmap.cc', 'src/corels/src/utils.cc', 'src/corels/src/corels.cc', 'src/corels/src/cache.cc', 'src/corels/src/rulelib.c'],
                    libraries = ['gmp', 'm'],
                    include_dirs = ['src/', 'src/corels/src/', np.get_include()],
		            extra_compile_args = ["-DGMP"])

long_description = ""

setuptools.setup(name = 'corels',
       version = '1.0.3',
       author = 'Vassilios Kaxiras',
       author_email = 'vassilioskaxiras@gmail.com',
       description = 'Python binding of the CORELS algorithm',
       long_description = long_description,
       url="https://github.com/fingoldin/pycorels",
       install_requires = ['numpy'],
       packages = setuptools.find_packages(),
       ext_modules = cythonize([pycorels]),
       zip_safe=False,
       classifiers=(
            "Programming Language :: C++",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent"
       )
)
