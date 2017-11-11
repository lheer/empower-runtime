import socket
import threading
from time import sleep


class BroadcastClient(object):
    def __init__(self, addr="255.255.255.255", port=4434):
        self._running = False
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._thread = threading.Thread(target=self.run)
        self._addr = (addr, port)

    def start(self):
        self._socket.bind(self._addr)
        self._running = True
        self._thread.start()
        print("Started broadcast client")

    def run(self):
        while (self._running):
            data, addr = self._socket.recvfrom(64)
            print("Got broadcast message {} from {}".format(data, addr))
            # TODO: Check broadcast message content (i.e. "ping")
            self._socket.sendto(b"hello", (addr[0], 4434))
            print("Sent broadcast answer")

    def stop(self):
        self._running = False
        self._thread.join()

    def close(self):
        self._socket.close()


if __name__ == "__main__":

    bc = BroadcastClient()
    bc.start()
    sleep(3)
    bc.stop()
    bc.close()
