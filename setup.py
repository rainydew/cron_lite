#!/usr/bin/env python
# coding: utf-8
from distutils.core import setup
from os import path, chdir, system
from sys import argv

if "upload" in argv:
    chdir("json_compare")
    print("running test")
    assert system("python test_json_compare.py") == 0
    chdir("..")

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
    install_requires=['six>=1.12.0'],
    keywords='json comparison order unicode fuzzy',
    long_description=long_description,
    python_requires=">=3.6"
)
