# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root
# for license information.

import os
import threading
import sys

import pydevd
from _pydevd_bundle.pydevd_comm import (
    get_global_debugger,
)

from ptvsd._remote import enable_attach as ptvsd_enable_attach

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 5678

_attached = threading.Event()


def wait_for_attach(timeout=None):
    """If a remote debugger is attached, returns immediately. Otherwise,
    blocks until a remote debugger attaches to this process, or until the
    optional timeout occurs.

    Parameters
    ----------
    timeout : float, optional
        The timeout for the operation in seconds (or fractions thereof).
    """
    _attached.wait(timeout)


def enable_attach(address=(DEFAULT_HOST, DEFAULT_PORT), redirect_output=True):
    """Enables a client to attach to this process remotely to debug Python code.

    Parameters
    ----------
    address : (str, int), optional
        Specifies the interface and port on which the debugging server should
        listen for TCP connections. It is in the same format as used for
        regular sockets of the `socket.AF_INET` family, i.e. a tuple of
        ``(hostname, port)``. On client side, the server is identified by the
        Qualifier string in the usual ``'hostname:port'`` format, e.g.:
        ``'myhost.cloudapp.net:5678'``. Default is ``('0.0.0.0', 5678)``.
    redirect_output : bool, optional
        Specifies whether any output (on both `stdout` and `stderr`) produced
        by this program should be sent to the debugger. Default is ``True``.

    Notes
    -----
    This function returns immediately after setting up the debugging server,
    and does not block program execution. If you need to block until debugger
    is attached, call `ptvsd.wait_for_attach`. The debugger can be detached
    and re-attached multiple times after `enable_attach` is called.

    Only the thread on which this function is called, and any threads that are
    created after it returns, will be visible in the debugger once it is
    attached. Any threads that are already running before this function is
    called will not be visible.
    """
    if get_global_debugger() is not None:
        return
    _attached.clear()
    ptvsd_enable_attach(address, redirect_output, on_attach=_attached.set)

# TODO: Add disable_attach()?


def is_attached():
    """Returns ``True`` if debugger is attached, ``False`` otherwise."""
    return _attached.isSet()


def break_into_debugger():
    """If a remote debugger is attached, pauses execution of all threads,
    and breaks into the debugger with current thread as active.
    """
    debugger = get_global_debugger()
    if not _attached.isSet() or debugger is None:
        return

    import sys
    pydevd.settrace(
        suspend=True,
        trace_only_current_thread=True,
        patch_multiprocessing=False,
        stop_at_frame=sys._getframe().f_back)


def enable_attach_in_process(pid, address=(DEFAULT_HOST, DEFAULT_PORT)):
    """Enables a client to attach to an arbitrary process o debug Python code.

    Parameters
    ----------
    pid : int
        Process Id of Python process to be debugged.
    address : (str, int), optional
        Specifies the interface and port on which the debugging server should
        listen for TCP connections. It is in the same format as used for
        regular sockets of the `socket.AF_INET` family, i.e. a tuple of
        ``(hostname, port)``. On client side, the server is identified by the
        Qualifier string in the usual ``'hostname:port'`` format, e.g.:
        ``'myhost.cloudapp.net:5678'``. Default is ``('0.0.0.0', 5678)``.
    redirect_output : bool, optional
        Specifies whether any output (on both `stdout` and `stderr`) produced
        by this program should be sent to the debugger. Default is ``True``.

    Notes
    -----
    Only the thread on which this function is called, and any threads that are
    created after it returns, will be visible in the debugger once it is
    attached. Any threads that are already running before this function is
    called will not be visible.
    """
    pydevd_attach_to_process_path = os.path.join(os.path.dirname(pydevd.__file__), 'pydevd_attach_to_process')
    sys.path.append(pydevd_attach_to_process_path)
    import add_code_to_python_process
    host = address[0]
    port = address[1]
    if sys.platform == 'win32':
        python_path = os.path.dirname(os.path.dirname(__file__)).replace('\\', '/')
        python_code = '''import sys;
sys.path.append("{python_path}");
import ptvsd;
ptvsd.enable_attach(("{host}", {port}));
'''.replace('\r\n', '').replace('\r', '').replace('\n', '')
    else:
        python_path = os.path.dirname(os.path.dirname(__file__))
        # We have to pass it a bit differently for gdb
        python_code = '''import sys;
sys.path.append(\\\"{python_path}\\\");
print(\\\"%{python_path}\\\");
import ptvsd;
print(00000);
print(\\\"{host}\\\");
print({port});
ptvsd.enable_attach((\\\"{host}\\\", {port}));
'''.replace('\r\n', '').replace('\r', '').replace('\n', '')

    python_code = python_code.format(python_path=python_path, host=host, port=port)
    add_code_to_python_process.run_python_code(
        pid, python_code, connect_debugger_tracing=False, show_debug_info=0)

