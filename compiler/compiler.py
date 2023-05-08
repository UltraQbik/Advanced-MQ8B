import json
if __name__ != '__main__':
    from compiler.exceptions import *
    INSTRUCTION_SET = json.load(open("compiler/instruction_set.json", "r"))
    PRECOMPILER = json.load(open("compiler/precompiler.json", "r"))


def compiler(filename, import_list=None):
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
        import_list: list[str] = [filename]
    instruction_list: list[list[str]] = []
    included_list: list[list[str]] = []
    define: list[dict[str, str]] = []
    vardef: list[dict[str, str]] = []
    subrut: list[dict[str, str]] = []
    for idx, inst in enumerate(instructions, start=1):
        if not len(inst):
            continue
        if inst[0][0] == "#":
            i = inst[0][1:].lower()
            if i not in PRECOMPILER:
                raise CompilerError(f"Unrecognized precompiler instruction; line {idx} in module '{filename}'")
            if len(inst) - 1 not in PRECOMPILER[i]:
                raise CompilerError(f"Incorrect amount of arguments; line {idx} in module '{filename}'")

            if i == "include":
                if inst[1] in import_list:
                    raise CompilerError(f"Circular include; line {idx} in module '{filename}'")
                try:
                    included_list += compiler(inst[1], import_list)["instruction_list"]
                except FileNotFoundError:
                    raise CompilerError(f"Import file not found; line {idx} in module '{filename}'")
                import_list.append(inst[1])
            elif i == "define":
                define.append({"from": inst[1], "to": inst[2]})
            elif i == "vardef":
                if inst[2][0] != "$":
                    raise CompilerError(f"Incorrect vardef pointer; line {idx} in module '{filename}'")
                try:
                    vardef.append({"name": inst[1], "pointer": inst[2]})
                except ValueError:
                    raise CompilerError(f"Incorrect vardef pointer address; line {idx} in module '{filename}'")
            elif i == "subrut":
                instruction_list.append(inst)
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
                        instruction_list.append(["ADC", inst[2]])
                    elif le == 3:
                        instruction_list.append(["LRA", inst[1]])
                        instruction_list.append(["ADC", inst[2]])
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
                case "INC" | "DEC" | "ABS" | "UI" | "UO" | "PRW" | "PRR":
                    if le == 0:
                        instruction_list.append(inst)
                    elif le == 1:
                        instruction_list.append(["LRA", inst[1]])
                        instruction_list.append([inst[0]])
                case default:
                    pass
        else:
            raise CompilerError(f"Undefined instruction word '{inst[0]}'; line {idx} in module '{filename}'")

    for i, inst in enumerate(instruction_list):
        for j, token in enumerate(inst):
            for definition in define:
                if token == definition["from"]:
                    instruction_list[i][j] = definition["to"]
                elif token[1:] == definition["from"]:
                    instruction_list[i][j] = token[0] + definition["to"]
            if j != 0:
                for var in vardef:
                    if token[0] == "&":
                        if token[1:] == var["name"]:
                            instruction_list[i][j] = var["pointer"]
    instruction_list = included_list + instruction_list

    print(instruction_list)
    print(define)
    print(vardef)
    print()

    return {
        "instruction_list": instruction_list,
        "define_list": define,
        "vardef_list": vardef
    }
