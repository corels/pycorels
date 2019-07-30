#!/bin/bash

cd ../docs
make html
cd ../utils
git clone https://github.com/saligrama/corels-ui.git
cd corels-ui
git config user.name "fingoldin"
git config user.email "vassilioskaxiras@gmail.com"
cp -r ../../docs/build/html/* ./ui/public/corels/pycorels
git add -A
git commit -m "Update docs"
git push origin master
cd ../
rm -rf corels-ui
ssh corels@corels.eecs.harvard.edu "cd corels-ui; git pull origin master"
