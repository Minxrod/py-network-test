import asyncio
import json
import socket  # to get host name

HOST = socket.gethostname()
PORT = 55555
ADDRESS = (HOST, PORT)
ENCODE = 'ascii'

commands = []
null_command = [("", [""])]

async def client_handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    client_location = 0

    while True:
        # confirm communication
        server_command = await reader.read(1024)
        command = json.loads(server_command,encoding=ENCODE)
        print(command)

        if command[0] == "request_all":
            await request_all(writer)
            client_location = len(commands)
        elif command[0] == "submit":
            accept_submit(command[1])
            await dummy(command, writer)
            client_location = len(commands)
        elif command[0] == "end":
            await dummy(command, writer)
            break
        else:
            await request_some(writer, client_location)
            client_location = len(commands)

    writer.close()
    print("Client disconnected.")

async def dummy(msg, writer):
    """
    Dummy write to preserve send-receive loop

    :param msg: string
    :param writer: asyncio.StreamWriter
    """
    writer.write(json.dumps(msg).encode(ENCODE))
    await writer.drain()

async def request_all(writer):
    writer.write(json.dumps(commands).encode(ENCODE))
    await writer.drain()

async def request_some(writer, location):
    if location < len(commands):
        writer.write(json.dumps(commands[location:]).encode(ENCODE))
        await writer.drain()
    else:
        await dummy(null_command, writer)

def accept_submit(data):
    commands.append(data)

async def connect():
    server = await asyncio.start_server(client_handle, HOST, PORT)

    print("Serving on: " + str(HOST) + " at " + socket.gethostbyname(HOST) + ", " + str(PORT))
    async with server:
        await server.serve_forever()

asyncio.run(connect())
