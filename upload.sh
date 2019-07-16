rm -rf dist build corels.egg-info
python setup.py sdist bdist_wheel
twine upload dist/*
