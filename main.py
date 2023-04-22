import os
import colorama as cr
from terminal.pretty_print import *
from compiler.compiler import *


def terminal_runtime():
    user_input = input("> ")
    if not user_input:
        return

    user_input = [x for x in user_input.split(" ") if x]

    match user_input[0].lower():
        case "?":
            print(
                generate_table_str(
                    [
                        ["help", "shows you this list"],
                        ["open", "opens a code file"],
                        ["exec", "executes the opened file; exec -f [file] to pass in file directly"],
                        ["list", "lists all the instructions"]
                    ],
                    row_align=["c", "l"],
                    column_sep="-"
                )
            )
        case "open":
            if len(user_input) > 1 and os.path.isfile(user_input[1]):
                print("Success!")
            else:
                print("Fail!")
        case "exec":
            for idx, tag in enumerate(user_input):
                if tag[0] != "-":
                    continue
                if tag == "-f" and idx + 1 < len(user_input):
                    if os.path.isfile(user_input[idx + 1]):
                        print("Success!")
                    else:
                        print("Fail!")
        case "list":
            pass
        case default:
            print(f"unknown command name '{user_input[0]}'; use '?' to get the list of all commands")


def main():
    cr.init(autoreset=True)
    while True:
        terminal_runtime()


if __name__ == '__main__':
    main()
