import asyncio
import json
import socket  # to get host name
import check_command as checker

HOST = socket.gethostname()
PORT = 55555
ADDRESS = (HOST, PORT)
ENCODE = 'ascii'

commands = []
null_command = None
cc = checker.CommandChecker("command_info.txt")

async def client_handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    client_location = 0

    while True:
        # confirm communication
        server_command = await reader.read(1024)
        command = json.loads(server_command,encoding=ENCODE)
        print(command)

        if command is None:
            await request_some(writer, client_location)
            client_location = len(commands)
        elif command[0] == "request_all":
            await request_all(writer)
            client_location = len(commands)
        elif command[0] == "submit":
            await request_some(writer, client_location)
            accept_submit(command[1])
            # submit after requesting
            # ensure up-to-date client
            # without repeating the submitted command
            client_location = len(commands)
        elif command[0] == "end":
            await dummy(None, writer)
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
    result = cc.check_args(data[0], data[1])
    print(result)

    # result is None = no errors, OK to add
    if result is None:
        commands.append(data)

async def connect():
    server = await asyncio.start_server(client_handle, HOST, PORT)

    print("Serving on: " + str(HOST) + " at " + socket.gethostbyname(HOST) + ", " + str(PORT))
    async with server:
        await server.serve_forever()

asyncio.run(connect())
