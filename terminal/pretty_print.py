def generate_table_list(rows: list[list[str]], row_names: list[str] | None = None,
                        row_sizes: list[int] | None = None, row_align: list[str] | None = None) -> list[list[str]]:
    if row_sizes is None:
        row_sizes = [len(x) for x in rows[0]]
        for row in rows:
            row_sizes = [max(x, len(y)) for x, y in zip(row_sizes, row)]
        row_sizes = [x + 2 for x in row_sizes]

    if row_align is None:
        row_align = ["^" for _ in rows[0]]
    else:
        for idx, align in enumerate(row_align):
            if align not in "^<>":
                if align == "c" or align == "center":
                    row_align[idx] = "^"
                elif align == "l" or align == "left":
                    row_align[idx] = "<"
                elif align == "r" or align == "right":
                    row_align[idx] = ">"
                else:
                    raise TypeError

    result = [[f"{x: ^{y}}" for x, y in zip(row_names, row_sizes)]] if row_names is not None else []
    for idx, row in enumerate(rows, start=1):
        result.append([])
        for i, (text, size, align) in enumerate(zip(row, row_sizes, row_align), start=1):
            s = " " if align != "^" else ""
            s += f"{text: {align}{size - 1 if align != '^' else size}}"
            result[-1].append(s)

    return result


def generate_table_str(rows: list[list[str]], row_names: list[str] | None = None,
                       row_sizes: list[int] | None = None, row_align: list[str] | None = None,
                       column_sep="|", end="\n"):
    table = generate_table_list(rows=rows, row_names=row_names, row_sizes=row_sizes, row_align=row_align)
    result = ""
    for idx, row in enumerate(table, start=1):
        result += column_sep.join(row)
        result += end if idx != len(table) else ""

    return result


if __name__ == '__main__':
    def test():
        print("#### Simple table ####")
        print(generate_table_str(
            [
                ["1", "good", "very", "nice"],
                ["2", "yes", "5", "4"],
                ["3", "yesnt", "4", "2"],
                ["4", "no", "0", "6"]
            ],
            row_names=["#", "command", "operand1", "operand2"],
            row_sizes=[3, 12, 20, 20],
            row_align=["c", "l", "l", "l"]
        ))

    test()
