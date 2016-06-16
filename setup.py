# -*- coding: utf-8 -*-
import os, io
from setuptools import setup

from PrintOnline.PrintOnline import __version__
here = os.path.abspath(os.path.dirname(__file__))
README = io.open(os.path.join(here, 'README.rst'), encoding='UTF-8').read()
CHANGES = io.open(os.path.join(here, 'CHANGES.rst'), encoding='UTF-8').read()
setup(name='PrintOnline',
      version=__version__,
      description='A online printer manager for Windows.',
      keywords=('svn', 'svn client', 'svn online'),
      long_description=README + '\n\n\n' + CHANGES,
      url='https://github.com/sintrb/PrintOnline',
      classifiers=[
          'Intended Audience :: End Users/Desktop',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python :: 2.7',
      ],
      author='sintrb',
      author_email='sintrb@gmail.com',
      license='Apache',
      packages=['PrintOnline'],
      scripts=['PrintOnline/PrintOnline.bat'],
      include_package_data=True,
      install_requires=['win32api'],
      zip_safe=False)
