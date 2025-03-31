import re
import termios
from mttext_app import MtTextEditApp
import sys

original_attributes = termios.tcgetattr(sys.stdin)


def disable_echo():
    """Отключает эхо и переводит терминал в неканонический режим."""
    new_attr = termios.tcgetattr(sys.stdin)
    new_attr[3] &= ~termios.ECHO  # Отключаем эхо
    new_attr[3] &= ~termios.ICANON  # Неканонический режим (посимвольный ввод)
    termios.tcsetattr(sys.stdin, termios.TCSANOW, new_attr)


def restore_echo():
    """Восстанавливает оригинальные настройки терминала."""
    termios.tcsetattr(sys.stdin, termios.TCSANOW, original_attributes)


def connect_to_session():
    r = re.compile(r"(\d{1,3}\.){3}\d{1,3}")
    conn_ip = sys.argv[2]
    if not r.match(conn_ip):
        print("Wrong connection ip address")
        return 0
    socket = MtTextEditApp("clientName")
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
    socket = MtTextEditApp("serverName", filetext)
    socket.run()
    socket.join()


def main():
    disable_echo()
    if sys.argv[1] == '-C':
        connect_to_session()
    if sys.argv[1] == '-H':
        host_session()
    restore_echo()


if __name__ == '__main__':
    main()
