#!/bin/bash

wget https://test.pypi.org/pypi/corels/json
python utils/version-changed.py
out=$?
rm json
exit $out
