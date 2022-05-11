#!/usr/bin/env python
# coding: utf-8
from distutils.core import setup
from os import path, system
from sys import argv

if "upload" in argv:
    print("running test")
    assert system("python test_cron_lite.py") == 0

this_directory = path.abspath(path.dirname(__file__))

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    long_description = ""

setup(
    name='cron-lite',
    version='1.0',
    description='A very light library to run python functions like cron jobs do.',
    author='Rainy Chan',
    author_email='rainydew@qq.com',
    url='https://github.com/rainydew/cron_lite',
    py_modules=["cron_lite"],
    install_requires=['croniter>=1.3.4'],
    keywords='cron task decorator schedule',
    long_description=long_description,
    python_requires=">=3.6"
)
