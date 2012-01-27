#!/usr/bin/env python

import os
import sys

from distutils.core import setup

def publish():
    """Publish to Pypi"""
    os.system("python setup.py sdist upload")

def runtests():
    """Runs unit-tests in myblog example project"""
    newcwd = os.path.join(os.getcwd(), "examples/myblog")
    os.chdir(newcwd)
    os.system("python manage.py test")

if sys.argv[-1] == "publish":
    publish()
    sys.exit()
elif sys.argv[-1] == "test":
    runtests()
    sys.exit()

setup(name='django-dynamicresponse',
      version='0.1.5',
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
