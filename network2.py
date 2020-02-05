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
# look for <dchp?>/searching for host server(s)


HOST = "127.0.0.1"
PORT = 55555
ADDRESS = (HOST, PORT)
ENCODE = 'ascii'

class Client:

    def __init__(self):
        self.reader = None
        self.writer = None

        self.recv_data = None

        self.flag = None
        self.send_queue = deque([])
        # self.send_command = ""  # instruction for server to use
        # self.send_info = ""  # data (may not be required)
        self._lock = threading.Lock()

    def set_info(self, command=None, info=None):
        with self._lock:
            self.send_queue.append((command, info))
            self.flag = "update"

    async def send(self, item):
        self.writer.write(convert_to_str(item))
        await self.writer.drain()

    async def recv(self):
        data = await self.reader.read(1024)
        return convert_to_list(data)

    async def main(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(HOST, PORT)
        except ConnectionRefusedError:
            print("Error connecting...")
            exit(1)

        while True:
            if not len(self.send_queue):
                await asyncio.sleep(1)

            with self._lock:
                if len(self.send_queue):
                    command_info = self.send_queue.popleft()
                else:
                    command_info = ("", "")

                # send_command = command_info[0]
                # send_info = command_info[1]
                await self.send(command_info)

                data = await self.recv()
                print(data)

                if command_info[0] == "request_all":
                    self.recv_data = data
                if command_info[0] == "end":
                    break

        self.writer.close()
        await self.writer.wait_closed()

    def get_data(self):
        with self._lock:
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