#     pydevd_attach_to_process_path = os.path.join(os.path.dirname(__file__), '_vendored', 'pydevd', 'pydevd_attach_to_process')
#     sys.path.append(pydevd_attach_to_process_path)
#     import add_code_to_python_process
#     show_debug_info_on_target_process = 0

#     pydevd_dirname = pydevd_attach_to_process_path

#     if sys.platform == 'win32':
#         setup['pythonpath'] = pydevd_dirname.replace('\\', '/')
#         setup['pythonpath2'] = os.path.join(os.path.dirname(__file__), '..').replace('\\', '/')
#         python_code = '''import sys;
# sys.path.append("%(pythonpath)s");
# sys.path.append("%(pythonpath2)s");
# import ptvsd;
# ptvsd.enable_attach(("%(host)s", %(port)s));
# '''.replace('\r\n', '').replace('\r', '').replace('\n', '')
#         python_code = '''print(9000)'''.replace('\r\n', '').replace('\r', '').replace('\n', '')
#     else:
#         setup['pythonpath'] = pydevd_dirname
#         setup['pythonpath2'] = os.path.join(os.path.dirname(__file__), '..')
#         # We have to pass it a bit differently for gdb
#         python_code = '''import sys;
# sys.path.append(\\\"%(pythonpath)s\\\");
# sys.path.append(\\\"%(pythonpath2)s\\\");
# import ptvsd;
# ptvsd.enable_attach((\\\"%(host)s\\\", %(port)s));
# '''.replace('\r\n', '').replace('\r', '').replace('\n', '')
#         python_code = '''print(9000)'''.replace('\r\n', '').replace('\r', '').replace('\n', '')

#     python_code = python_code % setup
#     add_code_to_python_process.run_python_code(
#         setup['pid'], python_code, connect_debugger_tracing=False, show_debug_info=show_debug_info_on_target_process)

# if __name__ == '__main__':
#     main(process_command_line(sys.argv[1:]))
import sys
import os


def process_command_line(argv):
    setup = {}
    setup['port'] = 5678  # Default port for PyDev remote debugger
    setup['pid'] = 0
    setup['host'] = '127.0.0.1'

    i = 0
    while i < len(argv):
        if argv[i] == '--port':
            del argv[i]
            setup['port'] = int(argv[i])
            del argv[i]

        elif argv[i] == '--pid':
            del argv[i]
            setup['pid'] = int(argv[i])
            del argv[i]

        elif argv[i] == '--host':
            del argv[i]
            setup['host'] = int(argv[i])
            del argv[i]


    if not setup['pid']:
        sys.stderr.write('Expected --pid to be passed.\n')
        sys.exit(1)
    return setup

def main(setup):
    pydevd_attach_to_process_path = os.path.join(os.path.dirname(__file__), '_vendored', 'pydevd', 'pydevd_attach_to_process')
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(pydevd_attach_to_process_path)

    import add_code_to_python_process
    show_debug_info_on_target_process = 0
    print('pydevd_dirname')
    if sys.platform == 'win32':
        setup['pythonpath'] = os.path.join(os.path.dirname(__file__), '..').replace('\\', '/')
        python_code = '''print(9000)'''.replace('\r\n', '').replace('\r', '').replace('\n', '')
        python_code = '''import sys;
sys.path.append("%(pythonpath)s");
import ptvsd;
print(ptvsd.__file__);
# attach_script.attach(("%(host)s", %(port)s));
'''.replace('\r\n', '').replace('\r', '').replace('\n', '')
    else:
        setup['pythonpath'] = os.path.join(os.path.dirname(__file__), '..')
        setup['pythonpath'] = '/Users/donjayamanne/Desktop/Development/vscode/ptvsd'
        # setup['pythonpath2'] = '/Users/donjayamanne/Desktop/Development/vscode/ptvsd/ptvsd'
        setup['pythonpath2'] = '/Users/donjayamanne/Desktop/Development/vscode/ptvsd'
        # We have to pass it a bit differently for gdb
        python_code = '''print(9000)'''.replace('\r\n', '').replace('\r', '').replace('\n', '')
        python_code = '''import sys;
sys.path.append(\\\"%(pythonpath)s\\\");
import ptvsd;
print(ptvsd.__file__);
ptvsd.enable_attach((\\\"%(host)s\\\", %(port)s));
# import that;
# import that.wow;
# that.wow.do_that();
# import ptsvd;
# print(ptvsd.__file__);
# attach_script.attach((\\\"%(host)s\\\", %(port)s));
'''.replace('\r\n', '').replace('\r', '').replace('\n', '')

    python_code = python_code % setup
    add_code_to_python_process.run_python_code(
        setup['pid'], python_code, connect_debugger_tracing=False, show_debug_info=show_debug_info_on_target_process)


if __name__ == '__main__':
    main(process_command_line(sys.argv[1:]))
