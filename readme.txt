This is a client-server test in Python using asyncio and tkinter.

The program allows you to "cooperatively draw" using commands. Messages can also be sent to other users using the message command.

To use:
server.py is the server. You need to run the server to be able to connect.
gui.py is the application. This is the user's client program.

To connect, someone run server.py and give out the ip. Then, clients on the same network can connect with that IP when prompted.
Note: the game will try to auto-sync to the server, but if you feel something is behind you can request an update using the Update button.

Available commands include:

help [cmd] - gives arguments for a given command
line x y x2 y2 [color] - draws a line.
rect x1 y1 x2 y2 [color] - draws a rectangle.
circle x y r [color] - draws a circle.
oval x y rx ry [color] - draws an oval.
color (name, #RGB, or #RRGGBB) - changes current color. Can use names or rgb formats.
msg message - sends a message that displays underneath the image. Username is displayed on other clients.