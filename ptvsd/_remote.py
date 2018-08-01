import pydevd
import time

from _pydevd_bundle.pydevd_comm import get_global_debugger

from ptvsd._util import new_hidden_thread
from ptvsd.pydevd_hooks import install
from ptvsd.socket import create_server


def _pydevd_settrace(redirect_output=None, _pydevd=pydevd, **kwargs):
    if redirect_output is not None:
        kwargs.setdefault('stdoutToServer', redirect_output)
        kwargs.setdefault('stderrToServer', redirect_output)
    # pydevd.settrace() only enables debugging of the current
    # thread and all future threads.  PyDevd is not enabled for
    # existing threads (other than the current one).  Consequently,
    # pydevd.settrace() must be called ASAP in the current thread.
    # See issue #509.
    #
    # This is tricky, however, because settrace() will block until
    # it receives a CMD_RUN message.  You can't just call it in a
    # thread to avoid blocking; doing so would prevent the current
    # thread from being debugged.
    _pydevd.settrace(**kwargs)


# TODO: Split up enable_attach() to align with module organization.
# This should including making better use of Daemon (e,g, the
# start_server() method).
# Then move at least some parts to the appropriate modules.  This module
# is focused on running the debugger.
def enable_attach(address, redirect_output=True,
                  _pydevd=pydevd, _install=install,
                  on_attach=lambda: None, **kwargs):
    host, port = address

    def wait_for_connection(daemon, host, port):
        debugger = get_global_debugger()
        while debugger is None:
            time.sleep(0.1)
            debugger = get_global_debugger()

        debugger.ready_to_run = True
        server = create_server(host, port)
        while True:
            client, _ = server.accept()
            daemon.start_session(client, 'ptvsd.Server')
            on_attach()

    daemon = _install(_pydevd,
                      address,
                      start_server=None,
                      start_client=(lambda daemon, h, port: daemon.start()),
                      singlesession=False,
                      **kwargs)

    connection_thread = new_hidden_thread('ptvsd.listen_for_connection',
                                          wait_for_connection,
                                          args=(daemon, host, port))
    connection_thread.start()

    _pydevd.settrace(host=host,
                     stdoutToServer=redirect_output,
                     stderrToServer=redirect_output,
                     port=port,
                     suspend=False)
