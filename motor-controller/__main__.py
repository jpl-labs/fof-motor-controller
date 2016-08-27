"""Main module to control the fan motors in the fans of fury game."""

import time
import sys
import signal
import configparser
import config as cfg

from .web_socket_handler import WebSocketHandler

cfg = configparser.ConfigParser()
cfg.read('config.ini')


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    def sigterm_handler(signum, frame):
        print('GAME: received sigterm')
        socket.server_socket.close()
        sys.exit()

    signal.signal(signal.SIGTERM, sigterm_handler)

    # Loop for REAL forever
    print('SOCKET: Connecting to websocket server...')
    while 1:
        try:
            with WebSocketHandler(cfg) as socket:
                socket.run()
        except KeyboardInterrupt:
            print('GAME: received keyboard interrupt.')
            socket.server_socket.close()
            sys.exit()
        except:
            exception = sys.exc_info()[1]
            print(exception)
            print('SOCKET: Reconnecting...')
            time.sleep(20)

if __name__ == "__main__":
    main()
