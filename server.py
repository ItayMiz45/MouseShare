import socket
from win32api import GetSystemMetrics
from pynput.mouse import Listener

stop = False

listening_port = 1234
ip = "192.168.1.22"

SERVER_ADDR = (ip, listening_port)


def create_listening_socket():
    listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    listening_sock.bind((ip, listening_port))

    return listening_sock


def on_move(x, y, conn, listener):
    global stop

    x = x if x > 0 else 0
    y = y if y > 0 else 0

    try:
        conn.sendall(f"move:{x},{y}\n".encode())

    except Exception as err:
        print(f"Error {err}")
        listener.stop()
        stop = True

    else:
        if {x, y} == {0}:
            listener.stop()
            stop = True


def on_click(*args, conn):
    data = f"click:{args[0]},{args[1]},{args[2]},{args[3]}\n"
    conn.sendall(data.encode())


def on_scroll(*args, conn):
    data = f"scroll:{0},{0},{args[2]},{args[3]}\n"
    conn.sendall(data.encode())


def main():
    listening_sock = create_listening_socket()
    print("Waiting for connections")
    listening_sock.listen(1)
    conn, addr = listening_sock.accept()
    print(addr)
    conn.sendall(f"{GetSystemMetrics(0)},{GetSystemMetrics(1)}".encode())

    with Listener(on_move=lambda *args: on_move(*args, conn=conn, listener=listener),
                  on_click=lambda *args: on_click(*args, conn=conn),
                  on_scroll=lambda *args: on_scroll(*args, conn=conn)) as listener:

        listener.join()

    conn.close()


if __name__ == '__main__':
    main()
