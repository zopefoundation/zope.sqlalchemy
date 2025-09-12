import os.path

from setuptools import setup


tests_require = ['zope.testing']

setup(
    name='zope.sqlalchemy',
    version='4.0',
    include_package_data=True,
    zip_safe=False,
    test_suite='zope.sqlalchemy.tests.test_suite',
    author='Laurence Rowe',

    author_email='laurence@lrowe.co.uk',
    url='https://github.com/zopefoundation/zope.sqlalchemy',
    description="Minimal Zope/SQLAlchemy transaction integration",
    long_description=(
        open(os.path.join('src', 'zope', 'sqlalchemy', 'README.rst')).read() +
        "\n\n" +
        open('CHANGES.rst').read()),
    license='ZPL 2.1',
    keywords='zope zope3 sqlalchemy',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pyramid",
        "Framework :: Zope :: 3",
        "Framework :: Zope :: 5",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.7',
    install_requires=[
        'packaging',
        'setuptools',
        'SQLAlchemy>=1.1,!=1.4.0,!=1.4.1,!=1.4.2,!=1.4.3,!=1.4.4,!=1.4.5,!=1.4.6,!=2.0.32,!=2.0.33,!=2.0.34,!=2.0.35',  # noqa: E501 line too long
        'transaction>=1.6.0',
        'zope.interface>=3.6.0',
    ],
    extras_require={'test': tests_require},
    tests_require=tests_require,
)
