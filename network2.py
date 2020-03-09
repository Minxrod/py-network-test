# import gui
import asyncio
import threading
import json
from collections import deque

# https://www.blog.pythonlibrary.org/2016/07/26/python-3-an-intro-to-asyncio/
# https://docs.python.org/3/library/asyncio-stream.html
# https://edux.pjwstk.edu.pl/mat/268/lec/lect8/lecture8.html
# https://docs.python.org/3.8/library/json.html
# https://realpython.com/intro-to-python-threading

ENCODE = 'ascii'
null_command = None

class Client:

    def __init__(self, control, host, port):
        self.host = host
        self.port = port

        self.control = control
        self.reader = None
        self.writer = None

        self.recv_data = None

        self.send_queue = deque([])
        # self.send_command = ""  # instruction for server to use
        # self.send_info = ""  # data (may not be required)
        self._send_lock = threading.Lock()
        self._recv_lock = threading.Lock()

    def set_info(self, command=None, info=None):
        with self._send_lock:
            self.send_queue.append((command, info))

    def set_command(self, command=None):
        with self._send_lock:
            self.send_queue.append(command)

    async def send(self, item):
        self.writer.write(convert_to_str(item))
        await self.writer.drain()

    async def recv(self):
        data = await self.reader.read(8192)
        # if self.reader.
        return convert_to_list(data)

    async def main(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        except ConnectionRefusedError:
            print("Error connecting...")
            exit(1)

        while True:
            with self._send_lock:
                if not len(self.send_queue):
                    await asyncio.sleep(0.1)
                    command_info = None
                else:
                    command_info = self.send_queue.popleft()

            await self.send(command_info)

            data = await self.recv()
            print("Recv: " + str(data))

            if data is not None:
                for command in data:
                    print("Cmd: " + str(command))
                    self.control.add_queue(command)

            if command_info is not None:
                if command_info[0] == "end":
                    break

        self.writer.close()
        await self.writer.wait_closed()
        print("Disconnected from server.")

    def get_data(self):
        with self._recv_lock:
            return self.recv_data

    def client_run(self):
        net_thread = threading.Thread(target=self.client)
        net_thread.start()

    def client(self):
        asyncio.run(self.main())

def convert_to_str(data: list):
    return json.dumps(data).encode(ENCODE)

def convert_to_list(data: str):
    return json.loads(data, encoding=ENCODE)
