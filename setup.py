#!/usr/bin/env python

from distutils.core import setup

version = '0.1.0'

setup(name='notebooktools',
      version=version,
      description='Tools for IPython Notebook used with Tellurium',
      author='Stanley Gu',
      author_email='stanleygu@gmail.com',
      url='https://github.com/stanleygu/ipython-notebook-modules',
      packages=['notebooktools', 'diffevolution', 'biomodels']
      )
