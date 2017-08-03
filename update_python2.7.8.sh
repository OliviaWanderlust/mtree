#!/bin/sh
yum install gcc python-devel readline-devel sqlite-devel libffi-devel openssl-devel -y
wget --no-check-certificate http://www.python.org/ftp/python/2.7.8/Python-2.7.8.tgz
tar zxf Python-2.7.8.tgz
cd Python-2.7.8
./configure &&make &&make install
cd ..
wget https://bootstrap.pypa.io/ez_setup.py -O - | python2.7
easy_install-2.7 pip
pip --default-timeout=100 install pyopenssl ndg-httpsclient pyasn1
