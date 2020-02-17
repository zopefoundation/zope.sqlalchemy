***************
zope.sqlalchemy
***************

.. contents::
   :local:

Introduction
============

The aim of this package is to unify the plethora of existing packages
integrating SQLAlchemy with Zope's transaction management. As such it seeks
only to provide a data manager and makes no attempt to define a `zopeish` way
to configure engines.

For WSGI applications, Zope style automatic transaction management is
available with `repoze.tm2`_ (used by `Turbogears 2`_ and other systems).

This package is also used by `pyramid_tm`_ (an add-on of the `Pyramid`_) web
framework.

You need to understand `SQLAlchemy`_ and the `Zope transaction manager`_ for
this package and this README to make any sense.

.. _repoze.tm2: http://docs.repoze.org/tm2/

.. _pyramid_tm: https://docs.pylonsproject.org/projects/pyramid_tm/dev/

.. _Pyramid: http://pylonsproject.org/

.. _Turbogears 2: http://turbogears.org/

.. _SQLAlchemy: http://sqlalchemy.org/docs/

.. _Zope transaction manager: http://www.zodb.org/en/latest/#transactions

Running the tests
=================

This package is distributed as a buildout. Using your desired python run:

$ python bootstrap.py
$ ./bin/buildout

This will download the dependent packages and setup the test script, which may
be run with:

$ ./bin/test

or with the standard setuptools test command:

$ ./bin/py setup.py test

To enable testing with your own database set the TEST_DSN environment variable
to your sqlalchemy database dsn. Two-phase commit behaviour may be tested by
setting the TEST_TWOPHASE variable to a non empty string. e.g:

$ TEST_DSN=postgres://test:test@localhost/test TEST_TWOPHASE=True bin/test

Usage in short
==============

The integration between Zope transactions and the SQLAlchemy event system is
done using the ``register()`` function on the session factory class.

.. code-block:: python

    from zope.sqlalchemy import register
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session

    engine = sqlalchemy.create_engine("postgresql://scott:tiger@localhost/test")

    DBSession = scoped_session(sessionmaker(bind=engine))
    register(DBSession)

Instantiated sessions commits and rollbacks will now be integrated with Zope
transactions.

.. code-block:: python

    import transaction

    session = DBSession()

    result = session.execute("DELETE FROM objects WHERE id=:id", {"id": 2})
    row = result.fetchone()

    transaction.commit()


Full Example
============

This example is lifted directly from the SQLAlchemy declarative documentation.
First the necessary imports.

    >>> from sqlalchemy import *
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> from sqlalchemy.orm import scoped_session, sessionmaker, relation
    >>> from zope.sqlalchemy import register
    >>> import transaction

Now to define the mapper classes.

    >>> Base = declarative_base()
    >>> class User(Base):
    ...     __tablename__ = 'test_users'
    ...     id = Column('id', Integer, primary_key=True)
    ...     name = Column('name', String(50))
    ...     addresses = relation("Address", backref="user")
    >>> class Address(Base):
    ...     __tablename__ = 'test_addresses'
    ...     id = Column('id', Integer, primary_key=True)
    ...     email = Column('email', String(50))
    ...     user_id = Column('user_id', Integer, ForeignKey('test_users.id'))

Create an engine and setup the tables. Note that for this example to work a
recent version of sqlite/pysqlite is required. 3.4.0 seems to be sufficient.

    >>> engine = create_engine(TEST_DSN)
    >>> Base.metadata.create_all(engine)

Now to create the session itself. As zope is a threaded web server we must use
scoped sessions. Zope and SQLAlchemy sessions are tied together by using the
register

    >>> Session = scoped_session(sessionmaker(bind=engine,
    ... twophase=TEST_TWOPHASE))

Call the scoped session factory to retrieve a session. You may call this as
many times as you like within a transaction and you will always retrieve the
same session. At present there are no users in the database.

    >>> session = Session()
    >>> register(session)
    <zope.sqlalchemy.datamanager.ZopeTransactionEvents object at ...>
    >>> session.query(User).all()
    []

We can now create a new user and commit the changes using Zope's transaction
machinery, just as Zope's publisher would.

    >>> session.add(User(id=1, name='bob'))
    >>> transaction.commit()

Engine level connections are outside the scope of the transaction integration.

    >>> engine.connect().execute('SELECT * FROM test_users').fetchall()
    [(1, ...'bob')]

A new transaction requires a new session. Let's add an address.

    >>> session = Session()
    >>> bob = session.query(User).all()[0]
    >>> str(bob.name)
    'bob'
    >>> bob.addresses
    []
    >>> bob.addresses.append(Address(id=1, email='bob@bob.bob'))
    >>> transaction.commit()
    >>> session = Session()
    >>> bob = session.query(User).all()[0]
    >>> bob.addresses
    [<Address object at ...>]
    >>> str(bob.addresses[0].email)
    'bob@bob.bob'
    >>> bob.addresses[0].email = 'wrong@wrong'

To rollback a transaction, use transaction.abort().

    >>> transaction.abort()
    >>> session = Session()
    >>> bob = session.query(User).all()[0]
    >>> str(bob.addresses[0].email)
    'bob@bob.bob'
    >>> transaction.abort()

By default, zope.sqlalchemy puts sessions in an 'active' state when they are
first used. ORM write operations automatically move the session into a
'changed' state. This avoids unnecessary database commits. Sometimes it
is necessary to interact with the database directly through SQL. It is not
possible to guess whether such an operation is a read or a write. Therefore we
must manually mark the session as changed when manual SQL statements write
to the DB.

    >>> session = Session()
    >>> conn = session.connection()
    >>> users = Base.metadata.tables['test_users']
    >>> conn.execute(users.update(users.c.name=='bob'), name='ben')
    <sqlalchemy.engine...ResultProxy object at ...>
    >>> from zope.sqlalchemy import mark_changed
    >>> mark_changed(session)
    >>> transaction.commit()
    >>> session = Session()
    >>> str(session.query(User).all()[0].name)
    'ben'
    >>> transaction.abort()

If this is a problem you may register the events and tell them to place the
session in the 'changed' state initially.

    >>> Session.remove()
    >>> register(Session, 'changed')
    <zope.sqlalchemy.datamanager.ZopeTransactionEvents object at ...>
    >>> session = Session()
    >>> conn = session.connection()
    >>> conn.execute(users.update(users.c.name=='ben'), name='bob')
    <sqlalchemy.engine...ResultProxy object at ...>
    >>> transaction.commit()
    >>> session = Session()
    >>> str(session.query(User).all()[0].name)
    'bob'
    >>> transaction.abort()

Long-lasting session scopes
---------------------------

The default behaviour of the transaction integration is to close the session
after a commit. You can tell by trying to access an object after committing:

    >>> bob = session.query(User).all()[0]
    >>> transaction.commit()
    >>> bob.name
    Traceback (most recent call last):
    DetachedInstanceError: Instance <User at ...> is not bound to a Session; attribute refresh operation cannot proceed...

To support cases where a session needs to last longer than a transaction (useful
in test suites) you can specify to keep a session when registering the events:

    >>> Session = scoped_session(sessionmaker(bind=engine,
    ... twophase=TEST_TWOPHASE))
    >>> register(Session, keep_session=True)
    <zope.sqlalchemy.datamanager.ZopeTransactionEvents object at ...>
    >>> session = Session()
    >>> bob = session.query(User).all()[0]
    >>> bob.name = 'bobby'
    >>> transaction.commit()
    >>> bob.name
    u'bobby'

The session must then be closed manually:

    >>> session.close()


Development version
===================

`GIT version <https://github.com/zopefoundation/zope.sqlalchemy>`_
