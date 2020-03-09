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
            await request_some(writer, client_location, 10)
            client_location += 10
            if client_location > len(commands):
                client_location = len(commands)
        elif command[0] == "submit":
            await request_some(writer, client_location, 100)
            # submit after requesting
            # ensure up-to-date client
            # without repeating the submitted command
            client_location += 100
            if client_location > len(commands):
                client_location = len(commands)

            accept_submit(command[1])
            client_location += 1
            # this will skip a command if more than 100 were sent
            # this should never be an issue, hopefully.
        elif command[0] == "end":
            await dummy(None, writer)
            break
        else:
            await request_some(writer, client_location, 10)
            client_location += 10
            if client_location > len(commands):
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

async def request_some(writer, location, send_amt):
    if location < len(commands):
        writer.write(json.dumps(commands[location:location+send_amt]).encode(ENCODE))
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

def load_from_file():

    p = input("Load from file? [y/n]")
    if p == "y":
        f = input("Filename: ")
        file = open(f, "r")

        return json.loads(file.read())
    else:
        return []

commands = load_from_file()
asyncio.run(connect())
