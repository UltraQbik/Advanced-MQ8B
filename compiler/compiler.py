import json
if __name__ != '__main__':
    from compiler.exceptions import *
    INSTRUCTION_SET = json.load(open("compiler/instruction_set.json", "r"))
    PRECOMPILER = json.load(open("compiler/precompiler.json", "r"))


def compiler(filename: str, import_list: set[str] = None):
    # split to tokens
    instructions: list[list[str]] = []
    with open(filename, "r") as file:
        code = file.read()
        for code_line in code.split("\n"):
            code_line = code_line.split(";")[0].rstrip(" ")
            word = [x.strip(" ") for x in code_line.split(" ") if len(x) != 0]
            instructions.append(word)

    # precompile
    if import_list is None:
        import_list = {filename}
    instruction_list: list[list[str | int]] = []
    define: dict[str, str] = {}
    vardef: dict[str, int] = {}
    subrut: dict[str, int] = {}
    auto_counter = 0
    for idx, inst in enumerate(instructions, start=1):
        if not len(inst):
            continue

        if inst[0][0] == ".":
            i = inst[0][1:].lower()

            if i not in PRECOMPILER:
                raise CompilerError(f"Unrecognized precompiler instruction; line {idx} in module '{filename}'")
            if len(inst) - 1 not in PRECOMPILER[i]:
                raise CompilerError(f"Incorrect amount of arguments; line {idx} in module '{filename}'")

            match i:
                case "include":
                    if inst[1] in import_list:
                        raise CompilerError(f"Circular include; line {idx} in module '{filename}'")

                    try:
                        return_data = compiler(inst[1], import_list)
                    except FileNotFoundError:
                        raise CompilerError(f"Import file not found; line {idx} in module '{filename}'")

                    instruction_list += return_data["instruction_list"]
                    define.update(return_data["define_list"])
                    vardef.update(return_data["vardef_list"])
                    subrut.update(return_data["subrut_list"])
                    import_list.add(inst[1])
                case "define":
                    define[inst[1]] = inst[2]
                case "vardef":
                    if inst[2] == "auto":
                        vardef[inst[1]] = auto_counter
                        auto_counter += 1
                    else:
                        if inst[2][0] != "$":
                            raise CompilerError(f"Incorrect address; line {idx} in module '{filename}'")

                        try:
                            vardef[inst[1]] = int(inst[2][1:])
                        except ValueError:
                            raise CompilerError(f"Unable to convert number; line {idx} in module '{filename}'")
                case "subrut":
                    subrut[inst[1]] = len(instruction_list)
                case _:
                    pass
        elif (i := inst[0].upper()) in INSTRUCTION_SET:
            if (le := len(inst) - 1) not in INSTRUCTION_SET[i][1]:
                raise CompilerError(f"Incorrect amount of arguments; line {idx} in module '{filename}'")

            match i:
                case "NOP" | "CCF" | "HALT":
                    instruction_list.append(inst)
                case "LRA" | "CALL" | "JMP" | "JMPP" | "JMPZ" | "JMPN" | "JMPC":
                    instruction_list.append(inst)
                case "SRA":
                    if le == 1:
                        instruction_list.append(inst)
                    elif le == 2:
                        instruction_list.append(["LRA", inst[1]])
                        instruction_list.append(["SRA", inst[2]])
                case "RET":
                    instruction_list.append(inst)
                case "AND" | "OR" | "XOR" | "LSC" | "RSC" | "CMP" | "ADC" | "SBC":
                    if le == 1:
                        instruction_list.append(inst)
                    elif le == 2:
                        instruction_list.append(["LRA", inst[1]])
                        instruction_list.append([inst[0], inst[2]])
                    elif le == 3:
                        instruction_list.append(["LRA", inst[1]])
                        instruction_list.append([inst[0], inst[2]])
                        instruction_list.append(["SRA", inst[3]])
                case "NOT":
                    if le == 0:
                        instruction_list.append(inst)
                    elif le == 1:
                        instruction_list.append(["LRA", inst[1]])
                        instruction_list.append([inst[0]])
                    elif le == 2:
                        instruction_list.append(["LRA", inst[1]])
                        instruction_list.append([inst[0]])
                        instruction_list.append(["SRA", inst[2]])
                case "INC" | "DEC" | "ABS":
                    if le == 0:
                        instruction_list.append(inst)
                    elif le == 1:
                        instruction_list.append(["LRA", inst[1]])
                        instruction_list.append([inst[0]])
                        instruction_list.append(["SRA", inst[1]])
                case "UI" | "PPR":
                    if le == 0:
                        instruction_list.append(inst)
                    elif le == 1:
                        instruction_list.append([inst[0]])
                        instruction_list.append(["SRA", inst[1]])
                case "UO" | "RRW":
                    if le == 0:
                        instruction_list.append(inst)
                    elif le == 1:
                        instruction_list.append(["LRA", inst[1]])
                        instruction_list.append([inst[0]])
                        instruction_list.append(["SRA", inst[1]])
                case _:
                    pass
        else:
            raise CompilerError(f"Undefined instruction word '{inst[0]}'; line {idx} in module '{filename}'")

    for i, inst in enumerate(instruction_list):
        for j, token in enumerate(inst):
            if token in define:
                instruction_list[i][j] = define[token]
            elif token[1:] in define:
                instruction_list[i][j] = token[0] + define[token]

    for i, inst in enumerate(instruction_list):
        if inst[0] == "SRA":        # SRA is a very funcy instruction in MQ8B, and will not work with sign bit on
            if inst[1][0] == "$":
                inst[1] = inst[1].replace("$", "#")
        for j, token in enumerate(inst[1:]):
            match token[0]:
                case "#" | "$":
                    try:
                        instruction_list[i][j+1] = int(token[1:])
                    except ValueError:
                        raise CompilerError(f"Incorrect decimal number; line {i+1} in module '{filename}'")
                    if token[0] == "$":
                        instruction_list[i].append(1)
                    else:
                        instruction_list[i].append(0)
                case "@":
                    if (name := token[1:]) not in subrut:
                        raise CompilerError(f"Subroutine '{name}' is not defined; line {i+1} in module '{filename}'")
                    instruction_list[i][j+1] = subrut[name]
                    instruction_list[i].append(0)
                case "&":
                    if (name := token[1:]) not in vardef:
                        raise CompilerError(f"Subroutine '{name}' is not defined; line {i+1} in module '{filename}'")
                    instruction_list[i][j+1] = vardef[name]
                    instruction_list[i].append(1)
        for _ in range(3 - len(inst)):
            instruction_list[i].append(0)

    # print(instruction_list)
    # print(define)
    # print(vardef)
    # print(subrut)
    # print()

    return {
        "instruction_list": instruction_list,
        "define_list": define,
        "vardef_list": vardef,
        "subrut_list": subrut
    }
