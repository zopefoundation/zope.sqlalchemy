import sys

import os.path
from setuptools import setup, find_packages

PY3 = sys.version_info[0] == 3

if PY3:
    extras_require = {'test':[]}
else:
    extras_require= {
        'test': [
            'pysqlite',
            ]
        }

setup(
    name='zope.sqlalchemy',
    version='0.7.2dev', # Remember to update __version__ in __init__.py
    packages=find_packages('src'),
    package_dir = {'':'src'},
    include_package_data=True,
    zip_safe=False,
    namespace_packages=['zope'],
    test_suite='zope.sqlalchemy',
    author='Laurence Rowe',
    author_email='laurence@lrowe.co.uk',
    url='http://pypi.python.org/pypi/zope.sqlalchemy',
    description="Minimal Zope/SQLAlchemy transaction integration",
    long_description=open(os.path.join('src', 'zope', 'sqlalchemy', 'README.txt')).read() + "\n\n" +
                     open('CHANGES.txt').read(),
    license='ZPL 2.1',
    keywords='zope zope3 sqlalchemy',                        
    classifiers=[
    "Framework :: Zope3",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "License :: OSI Approved :: Zope Public License",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires=[
      'setuptools',
      'SQLAlchemy>=0.5.1',
      'transaction',
      'zope.interface>=3.6.0',
      ],
    extras_require = extras_require,
    )
