import os
from setuptools import setup, find_packages

# generic helpers primarily for the long_description
try:
    import docutils
except ImportError:
    import warnings
    def validateReST(text):
        return ''
else:
    import docutils.utils
    import docutils.parsers.rst
    import StringIO
    def validateReST(text):
        doc = docutils.utils.new_document('validator')
        # our desired settings
        doc.reporter.halt_level = 5
        doc.reporter.report_level = 1
        stream = doc.reporter.stream = StringIO.StringIO()
        # docutils buglets (?)
        doc.settings.tab_width = 2
        doc.settings.pep_references = doc.settings.rfc_references = False
        doc.settings.trim_footnote_reference_space = None
        # and we're off...
        parser = docutils.parsers.rst.Parser()
        parser.parse(text, doc)
        return stream.getvalue()

def text(*args, **kwargs):
    # note: distutils explicitly disallows unicode for setup values :-/
    # http://docs.python.org/dist/meta-data.html
    tmp = []
    for a in args:
        if a.endswith('.txt'):
            f = open(os.path.join(*a.split('/')))
            tmp.append(f.read())
            f.close()
            tmp.append('\n\n')
        else:
            tmp.append(a)
    if len(tmp) == 1:
        res = tmp[0]
    else:
        res = ''.join(tmp)
    report = validateReST(res)
    if report:
        print report
        raise ValueError('ReST validation error')
    return res
# end helpers; below this line should be code custom to this package

setup(
    name='zope.sqlalchemy',
    version='0.4', # Remember to update __version__ in __init__.py
    
    packages=find_packages('src'),
    package_dir = {'':'src'},
    include_package_data=True,
    zip_safe=False,
    
    namespace_packages=['zope'],
    
    author='Laurence Rowe',
    author_email='laurence@lrowe.co.uk',
    url='http://pypi.python.org/pypi/zope.sqlalchemy',
    description=text('README.txt'),
    long_description=text('src/zope/sqlalchemy/README.txt',
                          'CHANGES.txt',
                          out=True),
    license='ZPL 2.1',
    keywords='zope zope3 sqlalchemy',                        
    classifiers=[
    "Framework :: Zope3",
    "Programming Language :: Python",
    "License :: OSI Approved :: Zope Public License",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires=[
      'setuptools',
      'SQLAlchemy>=0.4.7,!=0.5.0beta1,!=0.5.0beta2,!=0.5.0beta3,!=0.5.0rc1,!=0.5.0rc2,!=0.5.0rc3,!=0.5.0rc4,!=0.5.0', # or >=0.5.1
      'transaction',
      'zope.interface',
      ],
    extras_require={
        'test': [
            'zope.testing',
            'docutils',
            ]
        },
    )
