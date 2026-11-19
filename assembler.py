#!/usr/bin/env python3
"""Two-pass Hack assembler for Nand to Tetris.

Usage:
    python assembler.py input.asm [output.hack]

For this student's K=3 (K mod 3 == 0), the assembler also writes symbols.txt
containing every predefined symbol, label, and variable with its RAM/ROM address.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path

DEST = {
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "DM": "011",
    "A": "100",
    "AM": "101",
    "MA": "101",
    "AD": "110",
    "DA": "110",
    "AMD": "111",
    "ADM": "111",
    "MAD": "111",
    "MDA": "111",
    "DAM": "111",
    "DMA": "111",
} 
JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}
COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "M": "1110000",
    "!D": "0001101", "!A": "0110001", "!M": "1110001",
    "-D": "0001111", "-A": "0110011", "-M": "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "D+M": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000",
    "D|A": "0010101", "D|M": "1010101",
}
PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    **{f"R{i}": i for i in range(16)},
    "SCREEN": 16384, "KBD": 24576,
}

class AssemblerError(Exception):
    pass

def clean_lines(source: str):
    """Yield (original_line_number, cleaned_instruction) pairs."""
    for line_no, raw in enumerate(source.splitlines(), start=1):
        code = raw.split("//", 1)[0].strip()
        if code:
            yield line_no, re.sub(r"\s+", "", code)

def valid_symbol(symbol: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z_.$:][A-Za-z0-9_.$:]*", symbol))

def assemble(source: str):
    lines = list(clean_lines(source))
    symbols = dict(PREDEFINED)
    instructions = []
    rom_address = 0

    # Pass 1: collect labels.
    for line_no, command in lines:
        if command.startswith("(") and command.endswith(")"):
            label = command[1:-1]
            if not valid_symbol(label):
                raise AssemblerError(f"Line {line_no}: invalid label '{command}'")
            if label in symbols:
                raise AssemblerError(f"Line {line_no}: duplicate or reserved label '{label}'")
            symbols[label] = rom_address
        else:
            if command.startswith("(") or command.endswith(")"):
                raise AssemblerError(f"Line {line_no}: malformed label '{command}'")
            instructions.append((line_no, command))
            rom_address += 1

    # Pass 2: translate instructions; allocate variables from RAM[16].
    next_variable = 16
    machine = []
    for line_no, command in instructions:
        if command.startswith("@"):
            token = command[1:]
            if not token:
                raise AssemblerError(f"Line {line_no}: missing A-instruction value")
            if token.isdigit():
                value = int(token)
                if not 0 <= value <= 32767:
                    raise AssemblerError(f"Line {line_no}: A-instruction value must be 0..32767")
            else:
                if not valid_symbol(token):
                    raise AssemblerError(f"Line {line_no}: invalid symbol '{token}'")
                if token not in symbols:
                    symbols[token] = next_variable
                    next_variable += 1
                value = symbols[token]
            machine.append(f"{value:016b}")
            continue

        if command.count("=") > 1 or command.count(";") > 1:
            raise AssemblerError(f"Line {line_no}: malformed C-instruction '{command}'")
        if "=" in command:
            dest, remainder = command.split("=", 1)
        else:
            dest, remainder = "", command
        if ";" in remainder:
            comp, jump = remainder.split(";", 1)
        else:
            comp, jump = remainder, ""
        if dest not in DEST:
            raise AssemblerError(f"Line {line_no}: invalid destination '{dest}'")
        if comp not in COMP:
            raise AssemblerError(f"Line {line_no}: invalid computation '{comp}'")
        if jump not in JUMP:
            raise AssemblerError(f"Line {line_no}: invalid jump '{jump}'")
        machine.append("111" + COMP[comp] + DEST[dest] + JUMP[jump])

    return machine, symbols

def main():
    parser = argparse.ArgumentParser(description="Assemble Hack .asm into 16-bit .hack machine code.")
    parser.add_argument("input", type=Path, help="input .asm file")
    parser.add_argument("output", nargs="?", type=Path, help="output .hack file")
    args = parser.parse_args()
    output = args.output or args.input.with_suffix(".hack")
    try:
        source = args.input.read_text(encoding="utf-8")
        machine, symbols = assemble(source)
    except (OSError, AssemblerError) as exc:
        raise SystemExit(str(exc))
    output.write_text("\n".join(machine) + "\n", encoding="utf-8")
    # K=3, and 3 mod 3 = 0: save labels and variables with their addresses.
    symbol_lines = ["# Symbol table: predefined symbols, labels, and variables"]
    for name, address in sorted(symbols.items(), key=lambda item: (item[1], item[0])):
        symbol_lines.append(f"{name}\t{address}")
    (Path.cwd() / "symbols.txt").write_text("\n".join(symbol_lines) + "\n", encoding="utf-8")
    print(f"Assembled {len(machine)} instructions -> {output}")
    print(f"Wrote {len(symbols)} symbols -> {Path.cwd() / 'symbols.txt'}")

if __name__ == "__main__":
    main()
