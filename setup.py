#!/usr/bin/env python

import os
import sys

from distutils.core import setup

def publish():
    """Publish to Pypi"""
    os.system("python setup.py sdist upload")

if sys.argv[-1] == "publish":
    publish()
    sys.exit()

setup(name='django-dynamicresponse',
      version='0.1.4',
      description='Lightweight framework for easily providing REST APIs for web apps built with Django.',
      long_description=open('README.md').read(),
      author='Funkbit AS',
      author_email='post@funkbit.no',
      url='http://github.com/funkbit/django-dynamicresponse',
      packages=['dynamicresponse', 'dynamicresponse.middleware'],
      license='BSD',
      classifiers = (
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        )
     )
