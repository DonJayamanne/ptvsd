import sys
import ptvsd
port = int(sys.argv[1])
ptvsd.attach_to_process(port)
