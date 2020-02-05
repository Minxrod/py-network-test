import asyncio
import json

HOST = "127.0.0.1"
PORT = 55555
ADDRESS = (HOST, PORT)
ENCODE = 'ascii'

commands = []

async def client_handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while True:
        # confirm communication
        server_command = await reader.read(1024)
        command = json.loads(server_command,encoding=ENCODE)
        print(command)

        if command[0] == "request_all":
            await request_all(writer)
        elif command[0] == "submit":
            accept_submit(command[1])
            await dummy(command, writer)
        else:
            await dummy(command, writer)

    writer.close()

async def dummy(msg, writer):
    """
    Dummy write to preserve send-receive loop

    :param msg: string
    :param writer: asyncio.StreamWriter
    :return:
    """
    writer.write(json.dumps(msg).encode(ENCODE))
    await writer.drain()

async def request_all(writer):
    writer.write(json.dumps(commands).encode(ENCODE))
    await writer.drain()

def accept_submit(data):
    commands.append(data)

async def connect():
    server = await asyncio.start_server(client_handle, HOST, PORT)

    async with server:
        await server.serve_forever()

asyncio.run(connect())