Changes
=======

1.0 (2018-01-31)
----------------

* Add support for Python 3.4 up to 3.6.

* Support SQLAlchemy 1.2.

* Drop support for Python 2.6, 3.2 and 3.3.

* Drop support for transaction < 1.6.0.

* Fix hazard that could cause SQLAlchemy session not to be committed when
  transaction is committed in rare situations. See
  https://github.com/zopefoundation/zope.sqlalchemy/pull/23


0.7.7 (2016-06-23)
------------------

* Support SQLAlchemy 1.1.

  See: https://github.com/zopefoundation/zope.sqlalchemy/issues/15

0.7.6 (2015-03-20)
------------------

* Make version check in register compatible with prereleases.

0.7.5 (2014-06-17)
------------------

* Ensure mapped objects are expired following a ``transaction.commit()`` when
  no database commit was required.

  See: https://github.com/zopefoundation/zope.sqlalchemy/issues/8

0.7.4 (2014-01-06)
------------------

* Allow ``session.commit()`` on nested transactions to facilitate integration
  of existing code that might not use ``transaction.savepoint()``.

  See: https://github.com/zopefoundation/zope.sqlalchemy/issues/1

* Add a new function zope.sqlalchemy.register(), which replaces the
  direct use of ZopeTransactionExtension to make use
  of the newer SQLAlchemy event system to establish instrumentation on
  the given Session instance/class/factory.   Requires at least
  SQLAlchemy 0.7.

  See: https://github.com/zopefoundation/zope.sqlalchemy/issues/4

* Fix `keep_session=True` doesn't work when a transaction is joined by flush
  and other manngers bug.

  See: https://github.com/zopefoundation/zope.sqlalchemy/issues/5


0.7.3 (2013-09-25)
------------------

* Prevent the ``Session`` object from getting into a "wedged" state if joining
  a transaction fails. With thread scoped sessions that are reused this can cause
  persistent errors requiring a server restart.

  See: https://github.com/zopefoundation/zope.sqlalchemy/issues/2

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
