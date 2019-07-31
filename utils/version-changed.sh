#!/bin/bash

wget https://pypi.python.org/pypi/corels/json
python utils/version-changed.py
out=$?
rm json
exit $out
