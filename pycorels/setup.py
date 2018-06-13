import setuptools
import numpy as np

pycorels = setuptools.Extension('pycorels',
                    sources = ['pycorels/pycorels.c'],
                    libraries = ['corels', 'gmpxx', 'gmp'],
                    include_dirs = ['../corels/src', np.get_include()],
		            extra_compile_args = ["-DGMP"])

long_description = ""
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name = 'pycorels',
       version = '0.9',
       author = 'Vassilios Kaxiras',
       author_email = 'vassilioskaxiras@gmail.com',
       description = 'Python binding of CORELS algorithm',
       long_description = long_description,
       url="https://github.com/fingoldin/corels",
       packages = setuptools.find_packages(),
       ext_modules = [pycorels],
       eager_resources = ['../src/libcorels.so'],
       classifiers=(
            "Programming Language :: C++",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent"
       )
)
