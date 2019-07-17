rm -rf dist build corels.egg-info
python setup.py sdist
twine upload dist/*
