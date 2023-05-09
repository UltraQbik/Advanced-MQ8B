import os
import copy
import colorama as cr
from terminal.pretty_print import *
from compiler.compiler import *
from compiler.exceptions import *


class Shell:
    def __init__(self):
        self.opened_file: str | None = None
        self.compiled_file: dict | None = None
        self.source_code: str | None = None

    def ask_input(self):
        user_input = input("> ")
        if not user_input:
            return

        user_input = [x for x in user_input.split(" ") if x]
        match user_input[0].lower():
            case "?" | "help":
                print(
                    generate_table_str(
                        [
                            ["? / help", "shows you this list"],
                            ["open", "opens a code file"],
                            ["comp", "compiles the file"],
                            ["exec", "executes the opened file [WIP]"],
                            ["list", "lists all the instructions"],
                            ["exit", "exits"]
                        ],
                        row_align=["c", "l"],
                        row_sizes=[14, -1],
                        column_sep="-"
                    )
                )
            case "open":
                if len(user_input) > 1 and os.path.isfile(user_input[1]):
                    self.opened_file = user_input[1]
                    with open(self.opened_file, "r") as file:
                        self.source_code = file.read()
                    print("Success!")
                else:
                    print("Fail!")
            case "compile" | "comp":
                if self.opened_file is None:
                    print("no file is opened")
                    return
                self.compiled_file = compiler(self.opened_file)
            case "execute" | "exec":
                pass
            case "list":
                if self.opened_file is None:
                    print("no file is opened")
                    return
                if self.compiled_file is None:
                    if input("this file isn't compiled yet. Do you want to compile? (y/n): ").lower() == "y":
                        self.compiled_file = compiler(self.opened_file)
                    else:
                        print(cr.Fore.YELLOW + self.source_code)
                        return
                if input("show compiled version? (y/n): ").lower() == "y":
                    temp = copy.copy(self.compiled_file["instruction_list"])
                    for idx, i in enumerate(temp):
                        temp[idx] = [i[0], f"${i[1]}" if i[2] else f"#{i[1]}"]
                    print(
                        cr.Fore.YELLOW +
                        generate_table_str(
                            rows=temp,
                            row_align=["l", "l"],
                            row_sizes=[6, 8]
                        )
                    )
                else:
                    print(cr.Fore.YELLOW + self.source_code)
            case "exit":
                exit(0)
            case "cls" | "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
            case _:
                print(f"unknown command name '{user_input[0]}'; use '?' to get the list of all commands")

    def run(self):
        while True:
            try:
                self.ask_input()
            except CompilerError as e:
                print(cr.Fore.RED + str(e))


def main():
    cr.init(autoreset=True)
    app = Shell()
    app.run()


if __name__ == '__main__':
    main()
