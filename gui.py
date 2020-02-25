import threading
import tkinter as tk

from collections import deque
import network2 as net
import check_command as checker

# https://stackoverflow.com/questions/111155/hw-do-i-handle-the-window-close-event-in-tkinter
# https://stackoverflow.com/questions/2400262/how-to-create-a-timer-using-tkinter

host = str(input("Enter address: "))
port = 55555
name = str(input("Enter display name: "))

cc = checker.CommandChecker("command_info.txt")


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

        self.master.after(100, self.micro_update)

    def submit_command(self, event=None):
        self.control.submit_command(self.entry.get())

    def request_update(self, event=None):
        self.control.request_update()

    def close_gui(self):
        self.control.client.set_info("end", "")
        self.master.destroy()

    def micro_update(self):
        self.control.update_once()

        self.master.after(100, self.micro_update)


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

        # create command queue to store data from network and local
        self.command_queue = deque([])
        self._lock = threading.Lock()

    def add_queue(self, command):
        with self._lock:
            self.command_queue.append(command)

    def update_once(self):
        with self._lock:
            while len(self.command_queue) > 0:
                if not len(self.command_queue):
                    command = None
                else:
                    command = self.command_queue.popleft()
                self.run_command(command)

    def run_command(self, cmd):
        # cmd should be a (command, args) tuple or list
        if cmd is None:
            return None

        res = self.command(cmd[0], cmd[1])
        print(res)

    def submit_command(self, cmd):
        args = cmd.split()
        command = args.pop(0)
        operation = (command, args)

        self.add_queue(operation)
        self.client.set_info("submit", operation)

    def command(self, command, args):
        result = None

        check = cc.check_args(command, args)
        if check is not None:
            result = check
        else:
            if command == "help":
                if len(args) > 0:
                    result = cc.get_help(args[0])
                else:
                    result = cc.get_help(None)
            elif command == "line":
                result = self.line(args)
            elif command == "color":
                result = self.color(args)
            elif command == "rect" or command == "rectangle":
                result = self.rect(args)
            elif command == "circle":
                result = self.circle(args)
            elif command == "oval" or command == "ellipse":
                result = self.oval(args)
            if command == "msg" or command == "message":
                args.insert(0, self.user + ": ")
                result = self.message(args)

        # check result for updates
        if result is not None:
            self.label.set(result)
        else:
            if command != "" and command is not None:
                self.label.set("")

        if command == "msg" or command == "message":
            return None  # message is OK -> return none
        else:
            return result  # return any error messages generated

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

    def line(self, args):
        if len(args) == 5:
            color = args[4]
            self.prev_color = color  # save as default color

        elif len(args) == 4:
            color = self.prev_color
        else:
            return cc.get_help("line")

        self.objects.append(self.canvas.create_line(args[0:4], fill=color))

    def color(self, args):
        if len(args) == 1:
            self.prev_color = args[0]
        else:
            return cc.get_help("color")

    def rect(self, args):
        if len(args) == 5:
            color = args[4]
            self.prev_color = color  # save as default color

        elif len(args) == 4:
            color = self.prev_color
        else:
            return cc.get_help("rect")

        self.objects.append(self.canvas.create_rectangle(args[0:4], fill=color))

    def circle(self, args):
        if len(args) == 4:
            color = args[3]
            self.prev_color = color  # save as default color

        elif len(args) == 3:
            color = self.prev_color
        else:
            return cc.get_help("circle")

        x = int(args[0])
        y = int(args[1])
        r = int(args[2])

        self.objects.append(self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color))

    def oval(self, args):
        if len(args) == 5:
            color = args[4]
            self.prev_color = color  # save as default color

        elif len(args) == 4:
            color = self.prev_color
        else:
            return cc.get_help("oval")

        x = int(args[0])
        y = int(args[1])
        rx = int(args[2])
        ry = int(args[3])

        self.objects.append(self.canvas.create_oval(x - rx, y - ry, x + rx, y + ry, fill=color))

    def message(self, args):
        print("entered msg")
        if len(args) < 1:
            return cc.get_help("msg")

        print("calc msg from args")
        msg = ""
        for arg in args:
            if arg is args[0]:
                continue  # skip first argument
            msg += arg + " "

        return msg


root = tk.Tk()
gui = GUI(root)

root.protocol("WM_DELETE_WINDOW", gui.close_gui)

root.mainloop()
