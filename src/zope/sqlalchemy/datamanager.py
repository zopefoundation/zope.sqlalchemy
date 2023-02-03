##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################


from weakref import WeakKeyDictionary

from pkg_resources import parse_version

import transaction as zope_transaction
from sqlalchemy import __version__ as sqlalchemy_version
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import ConcurrentModificationError
from transaction._transaction import Status as ZopeStatus
from transaction.interfaces import IDataManagerSavepoint
from transaction.interfaces import ISavepointDataManager
from zope.interface import implementer


_retryable_errors = []
try:
    import psycopg2.extensions
except ImportError:
    pass
else:
    _retryable_errors.append(
        (psycopg2.extensions.TransactionRollbackError, None))

# ORA-08177: can't serialize access for this transaction
try:
    import cx_Oracle
except ImportError:
    pass
else:
    _retryable_errors.append(
        (cx_Oracle.DatabaseError, lambda e: e.args[0].code == 8177)
    )

# 1213: Deadlock found when trying to get lock; try restarting transaction
try:
    import pymysql
except ImportError:
    pass
else:
    _retryable_errors.append(
        (pymysql.err.OperationalError, lambda e: e.args[0] == 1213)
    )

# The status of the session is stored on the connection info
STATUS_ACTIVE = "active"  # session joined to transaction, writes allowed.
STATUS_CHANGED = "changed"  # data has been written
# session joined to transaction, no writes allowed.
STATUS_READONLY = "readonly"
STATUS_INVALIDATED = STATUS_CHANGED  # BBB

NO_SAVEPOINT_SUPPORT = {"sqlite"}

_SESSION_STATE = WeakKeyDictionary()  # a mapping of session -> status
# This is thread safe because you are using scoped sessions

SA_GE_14 = parse_version(sqlalchemy_version) >= parse_version('1.4.0')


#
# The two variants of the DataManager.
#


@implementer(ISavepointDataManager)
class SessionDataManager(object):
    """Integrate a top level sqlalchemy session transaction into a

    zope transaction.

    One phase variant.
    """

    def __init__(
            self, session, status, transaction_manager, keep_session=False):
        self.transaction_manager = transaction_manager

        if SA_GE_14:
            root_transaction = session.get_transaction() or session.begin()
        else:
            # Support both SQLAlchemy 1.0 and 1.1
            # https://github.com/zopefoundation/zope.sqlalchemy/issues/15
            _iterate_parents = (
                getattr(session.transaction, "_iterate_self_and_parents", None)
                or session.transaction._iterate_parents
            )
            root_transaction = _iterate_parents()[-1]

        self.tx = root_transaction
        self.session = session
        transaction_manager.get().join(self)
        _SESSION_STATE[session] = status
        self.state = "init"
        self.keep_session = keep_session

    def _finish(self, final_state):
        assert self.tx is not None
        session = self.session
        del _SESSION_STATE[self.session]
        self.tx = self.session = None
        self.state = final_state
        # closing the session is the last thing we do. If it fails the
        # transactions don't get wedged and the error propagates
        if not self.keep_session:
            session.close()
        else:
            session.expire_all()

    def abort(self, trans):
        if self.tx is not None:  # there may have been no work to do
            self._finish("aborted")

    def tpc_begin(self, trans):
        self.session.flush()

    def commit(self, trans):
        status = _SESSION_STATE[self.session]
        if status is not STATUS_INVALIDATED:
            session = self.session
            if session.expire_on_commit:
                session.expire_all()
            self._finish("no work")

    def tpc_vote(self, trans):
        # for a one phase data manager commit last in tpc_vote
        if self.tx is not None:  # there may have been no work to do
            self.tx.commit()
            self._finish("committed")

    def tpc_finish(self, trans):
        pass

    def tpc_abort(self, trans):
        assert self.state != "committed"

    def sortKey(self):
        # Try to sort last, so that we vote last - we may commit in tpc_vote(),
        # which allows Zope to roll back its transaction if the RDBMS
        # threw a conflict error.
        return "~sqlalchemy:%d" % id(self.tx)

    @property
    def savepoint(self):
        """Savepoints are only supported when all connections support

        subtransactions.
        """

        # ATT: the following check is weak since the savepoint capability
        # of a RDBMS also depends on its version. E.g. Postgres 7.X does not
        # support savepoints but Postgres is whitelisted independent of its
        # version. Possibly additional version information should be taken
        # into account (ajung)
        if set(
            engine.url.drivername
            for engine in self.tx._connections.keys()
            if isinstance(engine, Engine)
        ).intersection(NO_SAVEPOINT_SUPPORT):
            raise AttributeError("savepoint")
        return self._savepoint

    def _savepoint(self):
        return SessionSavepoint(self.session)

    def should_retry(self, error):
        if isinstance(error, ConcurrentModificationError):
            return True
        if isinstance(error, DBAPIError):
            orig = error.orig
            for error_type, test in _retryable_errors:
                if isinstance(orig, error_type):
                    if test is None:
                        return True
                    if test(orig):
                        return True


class TwoPhaseSessionDataManager(SessionDataManager):
    """Two phase variant.
    """

    def tpc_vote(self, trans):
        if self.tx is not None:  # there may have been no work to do
            self.tx.prepare()
            self.state = "voted"

    def tpc_finish(self, trans):
        if self.tx is not None:
            self.tx.commit()
            self._finish("committed")

    def tpc_abort(self, trans):
        # we may not have voted, and been aborted already
        if self.tx is not None:
            self.tx.rollback()
            self._finish("aborted commit")

    def sortKey(self):
        # Sort normally
        return "sqlalchemy.twophase:%d" % id(self.tx)


@implementer(IDataManagerSavepoint)
class SessionSavepoint:
    def __init__(self, session):
        self.session = session
        self.transaction = session.begin_nested()

    def rollback(self):
        # no need to check validity, sqlalchemy should raise an exception.
        self.transaction.rollback()


def join_transaction(
    session,
    initial_state=STATUS_ACTIVE,
    transaction_manager=zope_transaction.manager,
    keep_session=False,
):
    """Join a session to a transaction using the appropriate datamanager.

    It is safe to call this multiple times, if the session is already joined
    then it just returns.

    `initial_state` is either STATUS_ACTIVE, STATUS_INVALIDATED or
    STATUS_READONLY

    If using the default initial status of STATUS_ACTIVE, you must ensure that
    mark_changed(session) is called when data is written to the database.

    The ZopeTransactionEvents can be used to ensure that this is
    called automatically after session write operations.
    """
    if _SESSION_STATE.get(session, None) is None:
        if session.twophase:
            DataManager = TwoPhaseSessionDataManager
        else:
            DataManager = SessionDataManager
        DataManager(
            session, initial_state, transaction_manager,
            keep_session=keep_session
        )


def mark_changed(
    session, transaction_manager=zope_transaction.manager, keep_session=False
):
    """Mark a session as needing to be committed.
    """
    assert (
        _SESSION_STATE.get(session, None) is not STATUS_READONLY
    ), "Session already registered as read only"
    join_transaction(session, STATUS_CHANGED,
                     transaction_manager, keep_session)
    _SESSION_STATE[session] = STATUS_CHANGED


class ZopeTransactionEvents(object):
    """Record that a flush has occurred on a session's connection. This allows
    the DataManager to rollback rather than commit on read only transactions.
    """

    def __init__(
        self,
        initial_state=STATUS_ACTIVE,
        transaction_manager=zope_transaction.manager,
        keep_session=False,
    ):
        if initial_state == "invalidated":
            initial_state = STATUS_CHANGED  # BBB
        self.initial_state = initial_state
        self.transaction_manager = transaction_manager
        self.keep_session = keep_session

    def after_begin(self, session, transaction, connection):
        join_transaction(
            session, self.initial_state, self.transaction_manager,
            self.keep_session
        )

    def after_attach(self, session, instance):
        join_transaction(
            session, self.initial_state, self.transaction_manager,
            self.keep_session
        )

    def after_flush(self, session, flush_context):
        mark_changed(session, self.transaction_manager, self.keep_session)

    def after_bulk_update(self, update_context):
        mark_changed(update_context.session,
                     self.transaction_manager, self.keep_session)

    def after_bulk_delete(self, delete_context):
        mark_changed(delete_context.session,
                     self.transaction_manager, self.keep_session)

    def before_commit(self, session):
        in_nested_transaction = (
            session.in_nested_transaction()
            if SA_GE_14
            # support sqlalchemy 1.3 and below
            else session.transaction.nested
        )
        assert (
            in_nested_transaction
            or self.transaction_manager.get().status == ZopeStatus.COMMITTING
        ), "Transaction must be committed using the transaction manager"

    def do_orm_execute(self, execute_state):
        dml = any((execute_state.is_update, execute_state.is_insert,
                   execute_state.is_delete))
        if execute_state.is_orm_statement and dml:
            mark_changed(execute_state.session, self.transaction_manager,
                         self.keep_session)

    def mark_changed(self, session):
        """Developer interface to `mark_changed` that preserves the extension's
        active configuration.
        """
        mark_changed(session, self.transaction_manager, self.keep_session)

    def join_transaction(self, session):
        """Developer interface to `join_transaction` that preserves the
        extension's active configuration.
        """
        join_transaction(
            session, self.initial_state, self.transaction_manager,
            self.keep_session
        )


def register(
    session,
    initial_state=STATUS_ACTIVE,
    transaction_manager=zope_transaction.manager,
    keep_session=False,
):
    """Register ZopeTransaction listener events on the
    given Session or Session factory/class.

    This function requires at least SQLAlchemy 0.7 and makes use
    of the newer sqlalchemy.event package in order to register event listeners
    on the given Session.

    The session argument here may be a Session class or subclass, a
    sessionmaker or scoped_session instance, or a specific Session instance.
    Event listening will be specific to the scope of the type of argument
    passed, including specificity to its subclass as well as its identity.

    It returns the instance of ZopeTransactionEvents those methods where used
    to register the event listeners.

    """
    from sqlalchemy import event

    ext = ZopeTransactionEvents(
        initial_state=initial_state,
        transaction_manager=transaction_manager,
        keep_session=keep_session,
    )

    event.listen(session, "after_begin", ext.after_begin)
    event.listen(session, "after_attach", ext.after_attach)
    event.listen(session, "after_flush", ext.after_flush)
    event.listen(session, "after_bulk_update", ext.after_bulk_update)
    event.listen(session, "after_bulk_delete", ext.after_bulk_delete)
    event.listen(session, "before_commit", ext.before_commit)

    if SA_GE_14:
        event.listen(session, "do_orm_execute", ext.do_orm_execute)

    return ext
