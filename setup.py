"""
Setup of core python codebase
Author: Jeff Mahler
"""
from setuptools import setup

setup(name='core',
      version='0.1.dev0',
      description='AutoLab core utilites code',
      author='Jeff Mahler',
      author_email='jmahler@berkeley.edu',
      package_dir = {'': '.'},
      packages=['core'],
      #test_suite='test'
     )

