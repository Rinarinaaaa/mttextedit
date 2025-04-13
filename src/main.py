import re
from mttext_app import MtTextEditApp
import sys


def connect_to_session(debug, offset):
    r = re.compile(r"(\d{1,3}\.){3}\d{1,3}")
    conn_ip = sys.argv[2 + offset]
    if not r.match(conn_ip):
        print("Wrong connection ip address")
        return 0
    socket = MtTextEditApp(sys.argv[3 + offset], debug=debug)
    socket.connect(conn_ip)


def host_session(debug, offset):
    file_path = sys.argv[2 + offset]
    try:
        with open(file_path, 'r') as f:
            filetext = f.read()
    except IOError:
        print("File does not exist :(")
        return
    socket = MtTextEditApp(sys.argv[3 + offset], filetext,
                           debug=debug, file_path=file_path)
    socket.run()


def main():
    offset = 0
    debug = False
    if sys.argv[1] == '-D':
        offset += 1
        debug = True
    if sys.argv[1 + offset] == '-C':
        connect_to_session(debug, offset)
    if sys.argv[1 + offset] == '-H':
        host_session(debug, offset)


if __name__ == '__main__':
    main()
