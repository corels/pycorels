from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import os
import sys

USE_CYTHON = True
try:
    from Cython.Build import cythonize
except ImportError:
    USE_CYTHON = False

class build_numpy(build_ext):
    def finalize_options(self):
        build_ext.finalize_options(self)
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())

def install(gmp):
    description = 'Python binding of the CORELS algorithm'
    long_description = description
    with open('corels/README.txt') as f:
        long_description = f.read()

    version = '1.1.28'

    pyx_file = 'corels/_corels.pyx' if USE_CYTHON else 'corels/_corels.cpp'

    sources = [pyx_file, 'corels/src/utils.cpp', 'corels/src/corels/rulelib.cpp',
        'corels/src/corels/run.cpp', 'corels/src/corels/pmap.cpp', 
        'corels/src/corels/utils.cpp', 'corels/src/corels/corels.cpp', 
        'corels/src/corels/cache.cpp', 'corels/src/corels/time.cpp']
    
    cpp_args = ['-Wall', '-O3', '-std=c++11']
    libraries = []

    if os.name == 'posix':
        libraries.append('m')

    if gmp:
        libraries.append('gmp')
        cpp_args.append('-DGMP')

    if os.name == 'nt':
        cpp_args.append('-D_hypot=hypot')

    extension = Extension("corels._corels", 
                sources = sources,
                libraries = libraries,
                include_dirs = ['corels/src/', 'corels/src/corels'],
                language = "c++",
                extra_compile_args = cpp_args)

    extensions = [extension]
    if USE_CYTHON:
        extensions = cythonize(extensions)

    numpy_version = 'numpy'

    if sys.version_info[0] < 3 or sys.version_info[1] < 5:
        numpy_version = 'numpy<=1.16'

    setup(
        name = 'corels',
        packages = ['corels'],
        ext_modules = extensions,
        version = version,
        author = 'Elaine Angelino, Nicholas Larus-Stone, Hongyu Yang, Cythnia Rudin, Vassilios Kaxiras, Margo Seltzer',
        author_email = 'vassilioskaxiras@gmail.com',
        description = description,
        long_description = long_description,
        setup_requires = [numpy_version],
        install_requires = [numpy_version],
        python_requires = '>=2.7',
        url = 'https://github.com/fingoldin/pycorels',
        cmdclass = {'build_ext': build_numpy},
        classifiers = (
            "Programming Language :: C++",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent"
        )
    )

if __name__ == "__main__":
    try:
        install(True)
    except:
        install(False)
