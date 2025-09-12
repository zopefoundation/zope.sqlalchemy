Changes
=======

4.0 (2025-09-12)
----------------

- Replace ``pkg_resources`` namespace with PEP 420 native namespace.

- SQLAlchemy's versions 2.0.32 up to 2.0.35 run into dead locks when running
  the tests on Python 3.11+, so excluding them from the list of supported
  versions.
  (`#84 <https://github.com/zopefoundation/zope.sqlalchemy/issues/84>`_)

3.1 (2023-09-12)
----------------

- Fix ``psycopg.errors.OperationalError.sqlstate`` can be ``None``.
  (`#81 <https://github.com/zopefoundation/zope.sqlalchemy/issues/81>`_)


3.0 (2023-06-01)
----------------

- Add support for SQLAlchemy 2.0 and for new psycopg v3 backend.
  (`#79 <https://github.com/zopefoundation/zope.sqlalchemy/pull/79>`_)

**Breaking Changes**

- No longer allow calling ``session.commit()`` within a manual nested database
  transaction (a savepoint). If you want to use savepoints directly in code that is
  not aware of ``transaction.savepoint()`` with ``session.begin_nested()`` then
  use the savepoint returned by the function to commit just the nested transaction
  i.e. ``savepoint = session.begin_nested(); savepoint.commit()`` or use it as a
  context manager i.e. ``with session.begin_nested():``.
  (`for details see #79 <https://github.com/zopefoundation/zope.sqlalchemy/pull/79#issuecomment-1516069841>`_)


2.0 (2023-02-06)
----------------

- Drop support for Python 2.7, 3.5, 3.6.

- Drop support for ``SQLAlchemy < 1.1``
  (`#65 <https://github.com/zopefoundation/zope.sqlalchemy/issues/65>`_)

- Add support for Python 3.10, 3.11.


1.6 (2021-09-06)
----------------

- Add support for Python 2.7 on SQLAlchemy 1.4.
  (`#71 <https://github.com/zopefoundation/zope.sqlalchemy/issues/71>`_)


1.5 (2021-07-14)
----------------

- Call ``mark_changed`` also on the ``do_orm_execute`` event if the operation
  is an insert, update or delete. This is SQLAlchemy >= 1.4 only, as it
  introduced that event.
  (`#67 <https://github.com/zopefoundation/zope.sqlalchemy/issues/67>`_)

- Fixup get transaction. There was regression introduced in 1.4.
  (`#66 <https://github.com/zopefoundation/zope.sqlalchemy/issues/66>`_)


1.4 (2021-04-26)
----------------

- Add ``mark_changed`` and ``join_transaction`` methods to
  ``ZopeTransactionEvents``.
  (`#46 <https://github.com/zopefoundation/zope.sqlalchemy/issues/46>`_)

- Reduce DeprecationWarnings with SQLAlchemy 1.4 and require at least
  SQLAlchemy >= 0.9.
  (`#54 <https://github.com/zopefoundation/zope.sqlalchemy/issues/54>`_)

- Add support for SQLAlchemy 1.4.
  (`#58 <https://github.com/zopefoundation/zope.sqlalchemy/issues/58>`_)

- Prevent using an SQLAlchemy 1.4 version with broken flush support.
  (`#57 <https://github.com/zopefoundation/zope.sqlalchemy/issues/57>`_)


1.3 (2020-02-17)
----------------

* ``.datamanager.register()`` now returns the ``ZopeTransactionEvents``
  instance which was used to register the events. This allows to change its
  parameters afterwards.
  (`#40 <https://github.com/zopefoundation/zope.sqlalchemy/pull/40>`_)

* Add preliminary support for Python 3.9a3.


1.2 (2019-10-17)
----------------

**Breaking Changes**

* Drop support for Python 3.4.

* Add support for Python 3.7 and 3.8.

* Fix deprecation warnings for the event system. We already used it in general
  but still leveraged the old extension mechanism in some places.
  (`#31 <https://github.com/zopefoundation/zope.sqlalchemy/issues/31>`_)

  To make things clearer we renamed the ``ZopeTransactionExtension`` class
  to ``ZopeTransactionEvents``. Existing code using the 'register' version
  stays compatible.

**Upgrade from 1.1**

Your old code like this:

.. code-block:: python

    from zope.sqlalchemy import ZopeTransactionExtension

    DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), **options))

becomes:

.. code-block:: python

    from zope.sqlalchemy import register

    DBSession = scoped_session(sessionmaker(**options))
    register(DBSession)



1.1 (2019-01-03)
----------------

* Add support to MySQL using pymysql.


1.0 (2018-01-31)
----------------

* Add support for Python 3.4 up to 3.6.

* Support SQLAlchemy 1.2.

* Drop support for Python 2.6, 3.2 and 3.3.

* Drop support for transaction < 1.6.0.

* Fix hazard that could cause SQLAlchemy session not to be committed when
  transaction is committed in rare situations.
  (`#23 <https://github.com/zopefoundation/zope.sqlalchemy/pull/23>`_)


0.7.7 (2016-06-23)
------------------

* Support SQLAlchemy 1.1.
  (`#15 <https://github.com/zopefoundation/zope.sqlalchemy/issues/15>`_)


0.7.6 (2015-03-20)
------------------

* Make version check in register compatible with prereleases.

0.7.5 (2014-06-17)
------------------

* Ensure mapped objects are expired following a ``transaction.commit()`` when
  no database commit was required.
  (`#8 <https://github.com/zopefoundation/zope.sqlalchemy/issues/8>`_)


0.7.4 (2014-01-06)
------------------

* Allow ``session.commit()`` on nested transactions to facilitate integration
  of existing code that might not use ``transaction.savepoint()``.
  (`#1 <https://github.com/zopefoundation/zope.sqlalchemy/issues/1>`_)

* Add a new function zope.sqlalchemy.register(), which replaces the
  direct use of ZopeTransactionExtension to make use
  of the newer SQLAlchemy event system to establish instrumentation on
  the given Session instance/class/factory.   Requires at least
  SQLAlchemy 0.7.
  (`#4 <https://github.com/zopefoundation/zope.sqlalchemy/issues/4>`_)

* Fix `keep_session=True` doesn't work when a transaction is joined by flush
  and other manngers bug.
  (`#5 <https://github.com/zopefoundation/zope.sqlalchemy/issues/5>`_)


0.7.3 (2013-09-25)
------------------

* Prevent the ``Session`` object from getting into a "wedged" state if joining
  a transaction fails. With thread scoped sessions that are reused this can cause
  persistent errors requiring a server restart.
  (`#2 <https://github.com/zopefoundation/zope.sqlalchemy/issues/2>`_)

0.7.2 (2013-02-19)
------------------

* Make life-time of sessions configurable. Specify `keep_session=True` when
  setting up the SA extension.

* Python 3.3 compatibility.

0.7.1 (2012-05-19)
------------------

* Use ``@implementer`` as a class decorator instead of ``implements()`` at
  class scope for compatibility with ``zope.interface`` 4.0.  This requires
  ``zope.interface`` >= 3.6.0.

0.7 (2011-12-06)
----------------

* Python 3.2 compatibility.

0.6.1 (2011-01-08)
------------------

* Update datamanager.mark_changed to handle sessions which have not yet logged
  a (ORM) query.


0.6 (2010-07-24)
----------------

* Implement should_retry for sqlalchemy.orm.exc.ConcurrentModificationError
  and serialization errors from PostgreSQL and Oracle.
  (Specify transaction>=1.1 to use this functionality.)

* Include license files.

* Add ``transaction_manager`` attribute to data managers for compliance with
  IDataManager interface.

0.5 (2010-06-07)
----------------

* Remove redundant session.flush() / session.clear() on savepoint operations.
  These were only needed with SQLAlchemy 0.4.x.

* SQLAlchemy 0.6.x support. Require SQLAlchemy >= 0.5.1.

* Add support for running ``python setup.py test``.

* Pull in pysqlite explicitly as a test dependency.

* Setup sqlalchemy mappers in test setup and clear them in tear down. This
  makes the tests more robust and clears up the global state after. It
  caused the tests to fail when other tests in the same run called
  clear_mappers.

0.4 (2009-01-20)
----------------

Bugs fixed:

* Only raise errors in tpc_abort if we have committed.

* Remove the session id from the SESSION_STATE just before we de-reference the
  session (i.e. all work is already successfuly completed). This fixes cases
  where the transaction commit failed but SESSION_STATE was already cleared.  In
  those cases, the transaction was wedeged as abort would always error.  This
  happened on PostgreSQL where invalid SQL was used and the error caught.

* Call session.flush() unconditionally in tpc_begin.

* Change error message on session.commit() to be friendlier to non zope users.

Feature changes:

* Support for bulk update and delete with SQLAlchemy 0.5.1

0.3 (2008-07-29)
----------------

Bugs fixed:

* New objects added to a session did not cause a transaction join, so were not
  committed at the end of the transaction unless the database was accessed.
  SQLAlchemy 0.4.7 or 0.5beta3 now required.

Feature changes:

* For correctness and consistency with ZODB, renamed the function 'invalidate'
  to 'mark_changed' and the status 'invalidated' to 'changed'.

0.2 (2008-06-28)
----------------

Feature changes:

* Updated to support SQLAlchemy 0.5. (0.4.6 is still supported).

0.1 (2008-05-15)
----------------

* Initial public release.
