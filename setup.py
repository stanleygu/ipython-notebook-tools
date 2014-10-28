#!/usr/bin/env python

from distutils.core import setup
import json

with open('package.json', 'r') as f:
      j = json.load(f)

setup(name='notebooktools',
      version=j['version'],
      description=j['description'],
      author=j['author'],
      author_email='stanleygu@gmail.com',
      url=j['homepage'],
      packages=['notebooktools', 'diffevolution', 'biomodeltoolbox']
      )
