from setuptools import setup, Extension
import os

USE_CYTHON = True
try:
    from Cython.Build import cythonize
except ImportError:
    USE_CYTHON = False


def install(gmp):
    description = 'Python binding of the CORELS algorithm'
    long_description = description
    with open('corels/README.txt') as f:
        long_description = f.read()

    version = '1.1.17'

    pyx_file = 'corels/_corels.pyx' if USE_CYTHON else 'corels/_corels.cpp'

    sources = [pyx_file, 'corels/src/utils.cpp', 'corels/src/corels/rulelib.cpp',
        'corels/src/corels/run.cpp', 'corels/src/corels/pmap.cpp', 
        'corels/src/corels/utils.cpp', 'corels/src/corels/corels.cpp', 
        'corels/src/corels/cache.cpp', 'corels/src/corels/time.cpp']
    
    cpp_args = ['-Wall']
    libraries = []
    macros = []

    if os.name != 'nt':
        cpp_args.extend(['-O3', '-std=c++11'])

    if os.name == 'posix':
        libraries.append('m')

    if gmp:
        libraries.append('gmp')
        macros.append(('GMP', '1'))

    extension = Extension("corels._corels", 
                sources = sources,
                libraries = libraries,
                define_macros = macros,
                include_dirs = ['corels/src/', 'corels/src/corels'],
                language = "c++",
                extra_compile_args = cpp_args)

    extensions = [extension]
    if USE_CYTHON:
        extensions = cythonize(extensions)

    setup(
        name = 'corels',
        packages = ['corels'],
        ext_modules = extensions,
        version = version,
        author = 'Vassilios Kaxiras',
        author_email = 'vassilioskaxiras@gmail.com',
        description = description,
        long_description = long_description,
        setup_requires = ['numpy', 'cython'],
        install_requires = ['numpy', 'cython'],
        url = 'https://github.com/fingoldin/pycorels',
        classifiers = (
            "Programming Language :: C++",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent"
        )
    )

if __name__ == "__main__":
    install(True)
