# -*- coding: utf-8 -*-
#
# Copyright 2009: Johannes Raggam, BlueDynamics Alliance
#                 http://bluedynamics.com
# GNU Lesser General Public License Version 2 or later

__author__ = """Johannes Raggam <johannes@raggam.co.at>"""
__docformat__ = 'plaintext'

from setuptools import setup, find_packages
import sys, os

version = '1.0'
shortdesc ="Metamodel for activities"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.txt')).read()

setup(name='activities.metamodel',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Framework :: Zope3',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ], # Get strings from http://pypi.python.org/pypi?:action=list_classifiers
      keywords='UML Activities model metamodel',
      author='Johannes Raggam',
      author_email='johannes@raggam.co.at',
      url='',
      license='LGPL',
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['activities'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.interface',
          'zodict',
          # -*- Extra requirements: -*
      ],
      extras_require={
          'test': [
              'interlude',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
