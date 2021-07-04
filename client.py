import socket
from win32api import GetSystemMetrics
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, Key


server_ip = "192.168.1.51"

server_port = 8228
addr = (server_ip, server_port)

stop = False

SCROLL_MULTIPLIER = 240


def create_socket_connect():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect(addr)

    return sock


def on_press(key):
    global stop

    key = str(key).replace("'", '')


    print(key)
    if key.lower() == "q":
        print("stop")
        stop = True
        listener.stop()
        exit()


def move_to(control: Controller, x, y):
    curr_pos = control.position

    dx = x - curr_pos[0]
    dy = y - curr_pos[1]

    control.move(dx, dy)


def press_or_release(control, data):
    button = data[-2].split('.')[1]

    if button.lower() == "left":
        button = Button.left

    elif button.lower() == "right":
        button = Button.right

    elif button.lower() == "middle":
        button = Button.middle

    else:
        button = Button.unknown

    if True if data[-1] == "True" else False:
        control.press(button)

    else:
        control.release(button)


i = 0


def scroll(control, data):
    global i

    x = int(data[2]) * SCROLL_MULTIPLIER
    y = int(data[3]) * SCROLL_MULTIPLIER

    print(x, y)

    control.scroll(x, y)


def main():
    global listener
    listener = Listener(on_press=on_press)
    listener.start()

    mouse = Controller()

    print("Connecting...")

    sock = create_socket_connect()

    print("Connected")

    server_screen_res = sock.recv(1024).decode().split(',')

    multiplier_x = GetSystemMetrics(0) / int(server_screen_res[0])
    multiplier_y = GetSystemMetrics(1) / int(server_screen_res[1])

    print(multiplier_x, multiplier_y)

    while True:
        try:
            data = sock.recv(1024).decode()

        except Exception as err:
            print(f"Error {err}")
            break

        if stop:
            break

        data = data.split('\n')[-2].split(':')  # last msg splitted

        if data[0] == "move":
            data = data[1].split(',')
            move_to(mouse, int(data[0]) * multiplier_x, int(data[1]) * multiplier_y)

        elif data[0] == "click":
            data = data[1].split(',')
            press_or_release(mouse, data)

        elif data[0] == "scroll":
            data = data[1].split(',')
            scroll(mouse, data)

    listener.stop()


if __name__ == '__main__':
    main()
