##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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

__version__ = '0.5dev'

from datamanager import ZopeTransactionExtension, mark_changed
invalidate = mark_changed

_SESSIONS = {}

def Session():
    """Find the default session factory, execute and return the session"""
    return _SESSIONS['']()

def set_session(session_factory, name=''):
    _SESSIONS[name] = session_factory

def named_session(name):
    return _SESSIONS[name]()

def clear_sessions():
    global _SESSIONS
    _SESSIONS = {}

def install_sessions(sessions):
    global _SESSIONS
    _SESSIONS = sessions
