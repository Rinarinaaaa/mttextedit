import re
from duplex_websocket import DuplexWebsocket
import sys


def connect_to_session():
    r = re.compile(r"(\d{1,3}\.){3}\d{1,3}")
    conn_ip = sys.argv[2]
    if not r.match(conn_ip):
        print("Wrong connection ip address")
        return 0
    socket = DuplexWebsocket("clientName", daemon=True)
    socket.connect(conn_ip)
    socket.join()


def host_session():
    file_path = sys.argv[2]
    try:
        with open(file_path, 'r') as f:
            filetext = f.read()
            pass
    except IOError as e:
        print("File does not exist :(")
        return
    socket = DuplexWebsocket("serverName", filetext, daemon=True)
    socket.run()
    socket.join()


def main():
    if sys.argv[1] == '-C':
        connect_to_session()
    if sys.argv[1] == '-H':
        host_session()


if __name__ == '__main__':
    main()
