cythonize _corels.pyx
rm -rf dist build
python setup.py sdist
twine upload dist/*
