import re
import itertools

# https://www.regular-expressions.info/
# color list for validity check from here:
# https://stackoverflow.com/questions/4969543/colour-chart-for-tkinter-and-tix

# default info file
FILE = "command_info.txt"

REGEXP_NUM = "[0-9]*\\.?[0-9]*"
REGEXP_COLOR = "^#[0-9A-Fa-f]{3}([0-9A-Fa-f]{3})?$"
REGEXP_FILE = "^\\w+$"  # just name, no extension

class CommandChecker:

    def __init__(self, info_file=FILE):
        self.commands = []
        self.args = []

        file = open(info_file, "r")

        for line in file:
            line = line.rstrip()
            if line[0] != ':':
                chunks = line.split(" ")

                command = chunks[0]  # first item on line is command
                arguments = chunks[1:]  # all remaining items
            else:
                # data line for other stuff
                chunks = line.split(" ", 1)

                command = chunks[0]
                arguments = chunks[1:]

            self.commands.append(command)
            self.args.append(arguments)

        file.close()
        # print(self.commands)
        # print(self.args)

    def check_args(self, cmd, args):
        """
        Checks validity of a given command + arguments

        :param cmd: command string
        :param args: list of arguments
        :return: None if everything is valid, error string if error is found
        """

        # print(cmd, self.commands)
        if cmd not in self.commands:
            return "Unknown command"

        check_against = self.args[self.commands.index(cmd)]

        args_cont = None
        # print(args)
        for check, against in itertools.zip_longest(args, check_against):
            # print(check, against)

            if against is None:
                if args_cont is None:
                    return "Extra argument(s) given"
                else:
                    against = args_cont
            else:
                if against[1] == '*':
                    args_cont = against

            if check is not None:
                # the argument exists, is it valid?
                if against[0] == 'x':
                    new_against = self.args[self.commands.index(':' + against[2:])][0]  # don't be a list
                    # print(check, new_against)
                    # print(new_against.index("'"+check+"'"))
                    if "'" + check + "'" in new_against:
                        pass  # is a valid command if in
                    else:
                        # this is a special case, since ":color" needs extra options
                        if against[2:] == "color":
                            if re.match(REGEXP_COLOR, check) is not None:
                                pass
                            else:
                                return "Invalid argument for: " + against[2:]
                        else:
                            return "Invalid argument for: " + against[2:]
                elif against[0] == 'n':
                    if re.match(REGEXP_NUM, check) is not None:
                        pass  # is a valid number
                    else:
                        return "Invalid argument for: " + against[2:]
                elif against[0] == 't':
                    pass
                else:
                    return "Unknown error..."
            else:
                # if the argument doesn't exist, is it required?
                if against[1] == '?':
                    pass  # okay, because optional argument
                elif against[1] == ':':
                    return "Missing argument for: " + against[2:]
                else:
                    return "Missing argument for: " + against[2:]

        # print(check_against)
        return None

    def get_help(self, cmd):
        if cmd not in self.commands:
            return "cmd [page 1+] for command list"

        return cmd + str(self.args[self.commands.index(cmd)])

    def get_cmd(self, index):
        index = int(index) - 1
        if index * 5 < len(self.commands):
            cmds = str(self.commands[index*5:index*5+5])
            if cmds != "[]":
                return cmds
            else:
                return "Error: invalid page"

        return "Error: invalid page"

    def check_file(self, filename):
        if re.match(REGEXP_FILE, filename) is not None:
            return True
        else:
            return False

# Some tests...
#
# cc = CommandChecker()
# print(cc.check_args("line", ["5", "5", "50", "50", "red"]))
# print(cc.check_args("line", ["3", "6.9", "55.", ".2"]))
# print(cc.check_args("help", ["help"]))
# print(cc.check_args("msg", ["HELLO", "FIRELD"]))
# print(cc.check_args("color", ["#550ddd"]))
