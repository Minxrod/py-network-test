import tkinter as tk

class GUI:

    def __init__(self, master):
        self.frame = tk.Frame(master)

        self.canvas = tk.Canvas(self.frame, width=256, height=256)

        self.instruct_str = tk.StringVar()
        self.instruct_str.set("Enter 'help' for command list")
        self.instruct = tk.Label(self.frame, textvariable=self.instruct_str)

        self.entry = tk.Entry(self.frame)
        self.entry.insert(0, "help")
        self.entry.bind("<Return>", self.run)
        self.submit = tk.Button(self.frame, text="Submit", command=self.run)

        self.canvas.pack(side=tk.TOP)
        self.instruct.pack(side=tk.TOP)
        self.submit.pack(side=tk.RIGHT)
        self.entry.pack(side=tk.LEFT)

        self.ctr = Control(self.canvas)

        self.frame.pack()

    def run(self, event=None):
        cmd = self.entry.get()

        res = self.ctr.run(cmd)

        if res is not None:
            self.instruct_str.set(res)
        else:
            self.instruct_str.set("")

class Control:

    def __init__(self, canvas):
        self.objects = []
        self.commands = []
        self.canvas = canvas

        self.prev_color = "black"

    def run(self, command):
        args = command.split()
        command = args[0]
        args.remove(command)

        self.commands.append((command, args))
        print(self.commands)

        if command == "help":
            return Control._help(args)
        elif command == "line":
            return self.line(args)
        elif command == "color":
            return self.color(args)
        elif command == "rect":
            return self.rect(args)
        elif command == "circle":
            return self.circle(args)
        elif command == "oval":
            return self.oval(args)

    @staticmethod
    def _help(args):
        if len(args) >= 1:
            index = args[0]
        else:
            return "Commands: line, rect, circle, oval, color, help"

        if index == "line":
            return "line x1 y1 x2 y2 [color]"
        elif index == "rect":
            return "rect x1 y1 x2 y2 [color]"
        elif index == "circle":
            return "circle x y r [color]"
        elif index == "color":
            return "color (name, #RGB, or #RRGGBB)"
        elif index == "oval":
            return "oval x y rx ry [color]"
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
            return Control._help(["line"])

        self.objects.append(self.canvas.create_line(args[0:4], fill=color))

    def color(self, args):
        if len(args) == 1:
            self.prev_color = args[0]
        else:
            return Control._help("color")

    def rect(self, args):
        if len(args) == 5:
            color = args[4]
            self.prev_color = color  # save as default color

        elif len(args) == 4:
            color = self.prev_color
        else:
            return Control._help(["rect"])

        self.objects.append(self.canvas.create_rectangle(args[0:4], fill=color))

    def circle(self, args):
        if len(args) == 4:
            color = args[3]
            self.prev_color = color  # save as default color

        elif len(args) == 3:
            color = self.prev_color
        else:
            return Control._help(["circle"])

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
            return Control._help(["oval"])

        x = int(args[0])
        y = int(args[1])
        rx = int(args[2])
        ry = int(args[3])

        self.objects.append(self.canvas.create_oval(x - rx, y - ry, x + rx, y + ry, fill=color))


root = tk.Tk()

gui = GUI(root)

root.mainloop()
