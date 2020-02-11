import tkinter as tk
import network2 as net

# https://stackoverflow.com/questions/111155/hw-do-i-handle-the-window-close-event-in-tkinter

host = str(input("Enter address: "))
port = 55555
name = str(input("Enter display name: "))

class GUI:

    def __init__(self, master):
        # set up GUI info and widgets
        self.master = master
        self.frame = tk.Frame(master)

        self.canvas = tk.Canvas(self.frame, width=256, height=256)

        self.instruct_str = tk.StringVar()
        self.instruct_str.set("Enter 'help' for command list")
        self.instruct = tk.Label(self.frame, textvariable=self.instruct_str)

        # data processing/controls object
        self.control = Control(self.canvas, self.instruct_str)

        # add rest of GUI info (requires control for callbacks)
        self.entry = tk.Entry(self.frame)
        self.entry.insert(0, "help")
        self.entry.bind("<Return>", self.submit_command)
        self.submit = tk.Button(self.frame, text="Submit", command=self.submit_command)
        self.request = tk.Button(self.frame, text="Update", command=self.request_update)

        self.canvas.pack(side=tk.TOP)
        self.instruct.pack(side=tk.TOP)
        self.request.pack(side=tk.RIGHT)
        self.submit.pack(side=tk.RIGHT)
        self.entry.pack(side=tk.LEFT)

        self.frame.pack()

    def submit_command(self, event=None):
        self.control.submit_command(self.entry.get())

    def request_update(self, event=None):
        self.control.request_update()

    def close_gui(self):
        self.master.destroy()
        self.control.client.set_info("end", "")

class Control:
    def __init__(self, canvas, label):
        # save ref to canvas for drawing
        self.canvas = canvas
        self.label = label
        self.user = name

        # create necessary data objects
        self.objects = []
        self.commands = []
        self.prev_color = "black"

        # create networking objects
        self.client = net.Client(self, host, port)
        self.client.client_run()

    def submit_command(self, cmd):

        # split into command and arguments
        if cmd is not None:
            args = cmd.split()
            command = args.pop(0)
        else:
            args = []
            command = ""

        # run command
        res = self.command(command, args)

        # submit new info to server
        self.submit("submit", (command, args))

        # check result for updates
        if res is not None:
            self.label.set(res)
        else:
            self.label.set("")

    def command(self, command, args):
        if command == "help":
            return self._help(args)
        elif command == "line":
            return self.line(args)
        elif command == "color":
            return self.color(args)
        elif command == "rect" or command == "rectangle":
            return self.rect(args)
        elif command == "circle":
            return self.circle(args)
        elif command == "oval" or command == "ellipse":
            return self.oval(args)
        elif command == "msg" or command == "message":
            args.insert(0, self.user + ": ")
            return self.message(args)
        else:
            return None

    def submit(self, server_command, data):
        self.client.set_info(server_command, data)

        return self.client.get_data()

    def request_update(self):
        # request/get info from server
        self.submit("request_all", None)

        while self.client.get_data() is None:
            pass

        request = self.client.get_data()
        print(request)
        # reinitialize info and draw all objects
        for operation in request:
            self.command(operation[0], operation[1])
        pass

    @staticmethod
    def _help(args):
        if len(args) >= 1:
            index = args[0]
        else:
            return "Commands: line, rect, circle, oval, color, help, msg"

        if index == "line":
            return "line x1 y1 x2 y2 [color]"
        elif index == "rect" or index == "rectangle":
            return "rect x1 y1 x2 y2 [color]"
        elif index == "circle":
            return "circle x y r [color]"
        elif index == "color":
            return "color (name, #RGB, or #RRGGBB)"
        elif index == "oval" or index == "ellipse":
            return "oval x y rx ry [color]"
        elif index == "msg" or index == "message":
            return "msg message"
        elif index == "help":
            if len(args) > 1 and args[1] == "help":
                return "Okay, don't get too crazy now."
            else:
                return "Very funny."
        elif index == "me":
            return "Sorry, I got nothing."

    def line(self, args):
        if len(args) == 5:
            color = args[4]
            self.prev_color = color  # save as default color

        elif len(args) == 4:
            color = self.prev_color
        else:
            return self._help(["line"])

        self.objects.append(self.canvas.create_line(args[0:4], fill=color))

    def color(self, args):
        if len(args) == 1:
            self.prev_color = args[0]
        else:
            return self._help("color")

    def rect(self, args):
        if len(args) == 5:
            color = args[4]
            self.prev_color = color  # save as default color

        elif len(args) == 4:
            color = self.prev_color
        else:
            return self._help(["rect"])

        self.objects.append(self.canvas.create_rectangle(args[0:4], fill=color))

    def circle(self, args):
        if len(args) == 4:
            color = args[3]
            self.prev_color = color  # save as default color

        elif len(args) == 3:
            color = self.prev_color
        else:
            return self._help(["circle"])

        x = int(args[0])
        y = int(args[1])
        r = int(args[2])

        self.objects.append(self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color))

    def oval(self, args):
        if len(args) == 5:
            color = args[4]
            self.prev_color = color  # save as default color

        elif len(args) == 4:
            color = self.prev_color
        else:
            return self._help(["oval"])

        x = int(args[0])
        y = int(args[1])
        rx = int(args[2])
        ry = int(args[3])

        self.objects.append(self.canvas.create_oval(x - rx, y - ry, x + rx, y + ry, fill=color))

    def message(self, args):
        if len(args) < 1:
            return self._help(["msg"])

        msg = ""
        for arg in args:
            if arg is args[0]:
                continue  # skip first argument
            msg += arg + " "
        self.label.set(msg)


root = tk.Tk()
gui = GUI(root)

root.protocol("WM_DELETE_WINDOW", gui.close_gui)

root.mainloop()
