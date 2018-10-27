import setuptools
import numpy as np

pycorels = setuptools.Extension('pycorels',
                    sources = ['pycorels/pycorels.c', 'pycorels/run.cc', 'pycorels/params.c', 'corels/src/pmap.cc', 'corels/src/utils.cc', 'corels/src/corels.cc', 'corels/src/cache.cc', 'corels/src/rulelib.c'],
                    libraries = ['gmpxx', 'gmp'],
                    include_dirs = ['pycorels/', 'corels/src/', np.get_include()],
		            extra_compile_args = ["-DGMP", "-std=c++11"])

long_description = ""
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name = 'pycorels',
       version = '1.0.1',
       author = 'Vassilios Kaxiras',
       author_email = 'vassilioskaxiras@gmail.com',
       description = 'Python binding of CORELS algorithm',
       long_description = long_description,
       long_description_content_type='text/markdown', 
       url="https://github.com/fingoldin/corels",
       install_requires = ['numpy'],
       packages = setuptools.find_packages(),
       ext_modules = [pycorels],
       classifiers=(
            "Programming Language :: C++",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent"
       )
)
