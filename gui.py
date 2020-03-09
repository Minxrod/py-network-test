import threading
import json
import tkinter as tk
from collections import deque

import PIL.Image
import PIL.ImageDraw

import check_command as checker
import network2 as net
import tkdialog

# https://stackoverflow.com/questions/111155/hw-do-i-handle-the-window-close-event-in-tkinter
# https://stackoverflow.com/questions/2400262/how-to-create-a-timer-using-tkinter
# https://stackoverflow.com/questions/9886274/how-can-i-convert-canvas-content-to-an-image
# https://effbot.org/tkinterbook/tkinter-dialog-windows.htm

host = None
port = 55555
name = None

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
        self.control = None

        # add rest of GUI info (requires control for callbacks)
        self.entry = tk.Entry(self.frame)
        self.entry.insert(0, "help")
        self.entry.bind("<Return>", self.submit_command)
        self.submit = tk.Button(self.frame, text="Submit", command=self.submit_command)
        self.request = tk.Button(self.frame, text="Save Image", command=self.save_image)

        self.canvas.pack(side=tk.TOP)
        self.instruct.pack(side=tk.TOP)
        self.request.pack(side=tk.RIGHT)
        self.submit.pack(side=tk.RIGHT)
        self.entry.pack(side=tk.LEFT)

        self.frame.pack()

        self.dialog = InitDialog(self.master)

        self.control = Control(self.canvas, self.instruct_str)
        self.master.after(100, self.micro_update)

    def submit_command(self, event=None):
        self.control.submit_command(self.entry.get())

    # using this solution
    def save_image(self, event=None):
        self.dialog = SaveDialog(self.master)
        filename = self.dialog.result[0]
        extension = self.dialog.result[1]

        print(self.dialog.result)
        if extension == ".txt":
            self.control.save_cmds(filename + extension)
        elif extension == ".png":
            self.control.save_image.save(filename + extension)

    def close_gui(self):
        self.control.client.set_info("end", "")
        self.master.destroy()

    def micro_update(self):
        self.control.update_once()

        self.master.after(100, self.micro_update)


class InitDialog(tkdialog.Dialog):
    def __init__(self, parent, title=None):
        self.BUTTON_OK = "Connect"
        self.BUTTON_CANCEL = "Quit"

        super().__init__(parent, title)

    def body(self, master):
        dialog = tk.Frame(master)
        self.host_label = tk.Label(dialog, text="Host IP:")
        self.user_label = tk.Label(dialog, text="Username:")
        self.host_entry = tk.Entry(dialog)
        self.user_entry = tk.Entry(dialog)

        self.host_label.grid(row=0, column=0)
        self.user_label.grid(row=1, column=0)
        self.host_entry.grid(row=0, column=1)
        self.user_entry.grid(row=1, column=1)

        dialog.pack()
        return self.host_entry

    def apply(self):
        global host, name

        host = self.host_entry.get()
        name = self.user_entry.get()

        self.result = host, name


class SaveDialog(tkdialog.Dialog):
    def __init__(self, parent, title=None):
        self.BUTTON_OK = "Save as png"
        self.BUTTON_OK2 = "Save as txt"
        self.BUTTON_CANCEL = "Cancel"

        super().__init__(parent, title)

    def buttonbox(self):
        box = tk.Frame(self)

        w = tk.Button(box, text=self.BUTTON_OK, width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text=self.BUTTON_OK2, width=10, command=self.ok2)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text=self.BUTTON_CANCEL, width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Shift-Return>", self.ok2)
        self.bind("<Escape>", self.cancel)

        box.pack()

        return box

    def ok2(self, event=None):
        self.result = ".txt"
        self.ok(event)

    def body(self, master):
        dialog = tk.Frame(master)
        self.file_label = tk.Label(dialog, text="Filename: ")
        self.file_entry = tk.Entry(dialog)

        self.file_label.grid(row=0, column=0)
        self.file_entry.grid(row=0, column=1)

        dialog.pack()
        return self.file_entry

    def apply(self):
        pass

    def validate(self):
        filename = self.file_entry.get()

        if cc.check_file(filename):
            if self.result != '.txt':
                self.result = filename, ".png"
            else:
                self.result = filename, ".txt"

            return 1
        else:
            return 0


class Control:
    def __init__(self, canvas, label):
        # save ref to canvas for drawing
        self.canvas = canvas
        self.label = label
        self.user = name

        # create second canvas to mirror info for saving
        self.save_image = PIL.Image.new("RGB", (256, 256), (255, 255, 255))
        self.save_canvas = PIL.ImageDraw.Draw(self.save_image)

        # create necessary data objects
        self.objects = []  # this doesn't really do anything
        self.commands = []
        self.prev_color = "black"

        # create networking objects
        self.client = net.Client(self, host, port)
        self.client.client_run()

        # create command queue to store data from network and local
        self.command_queue = deque([])
        self._lock = threading.Lock()

    # https://www.pythonforbeginners.com/files/reading-and-writing-files-in-python
    def save_cmds(self, filename):
        file = open(filename, "w")

        file.write(json.dumps(self.commands))

        file.close()

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

        self.commands.append(cmd)
        self.command(cmd[0], cmd[1])

    def submit_command(self, cmd):
        args = cmd.split()
        command = args.pop(0)
        operation = (command, args)

        self.add_queue(operation)
        if cc.check_args(command, args) is None:
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
            elif command == "cmd" or command == "command":
                if len(args) > 0:
                    result = cc.get_cmd(args[0])
                else:
                    result = cc.get_cmd(0)
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

    def line(self, args):
        if len(args) == 5:
            color = args[4]
            self.prev_color = color  # save as default color

        elif len(args) == 4:
            color = self.prev_color
        else:
            return cc.get_help("line")

        self.objects.append(self.canvas.create_line(args[0:4], fill=color))
        t_args = [int(args[0]), int(args[1]), int(args[2]), int(args[3])]
        self.save_canvas.line(t_args, fill=color)

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
        t_args = [int(args[0]), int(args[1]), int(args[2]), int(args[3])]
        self.save_canvas.rectangle(t_args, fill=color, outline="")

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

        t_args = [x - r, y - r, x + r, y + r]
        self.objects.append(self.canvas.create_oval(t_args, fill=color, outline=""))
        self.save_canvas.ellipse(t_args, color)

    # https://stackoverflow.com/questions/37582572/remove-the-outline-of-an-oval-in-tkinter
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

        t_args = [x - rx, y - ry, x + rx, y + ry]
        self.objects.append(self.canvas.create_oval(t_args, fill=color, outline=""))
        self.save_canvas.ellipse(t_args, color)
        # because thinking is hard, i had to search how to draw an 'oval' -> ellipse
        # https://stackoverflow.com/questions/4789894/python-pil-how-to-draw-an-ellipse-in-the-middle-of-an-image

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
