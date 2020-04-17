import sys
import os
import pathlib

def idiom(kind):
    if kind == "push D":
        return """
        @SP
        A=M
        M=D
        @SP // sp++
        M=M+1
        """
    elif kind == "pop 13":
        return """
        @SP // sp--
        AM=M-1
        D=M
        @13
        M=D
        """
    elif kind == "pop D":
        return """
        @SP // sp--
        AM=M-1
        D=M
        """
    elif kind == "pop A":
        return """
        @SP // sp--
        AM=M-1
        A=M
        """

cnt = 0
def getId():
    global cnt
    cnt+=1
    return cnt

def main(_path):
    path = pathlib.Path(_path)
    module_name = path.with_suffix("").name
    with open(path.with_suffix(".asm"), 'w') as target:
        def write(txt, to_file = False):
            if to_file:
                target.write(txt + "\n")
            else:
                print(txt)
        print = lambda l: write(l, True)
        with open(path, 'r') as file:
            lines = file.readlines()
            for l in lines:
                print(f"// @{path} {l.strip()}")
                tokens = l.strip().split(" ")
                command = tokens[0]
                if command in ["pop", "push"]:
                    [_, segment, offset] = tokens
                    PREDEFINED = ["local", "argument", 'this', 'that']
                    segindex = PREDEFINED.index(segment) if segment in PREDEFINED else -1
                    if segment == "constant":
                        assert command == "push"
                        print(striplines(f"""
                        @{offset}
                        D=A
                        {idiom('push D')}
                        """))
                    elif segindex >= 0:
                        SEG = ["LCL", 'ARG', 'THIS', 'THAT'][segindex]
                        if command == 'pop':
                            print(striplines(f"""
                            {idiom('pop 13')}
                            @{offset}
                            D=A
                            @{SEG}
                            D=D+M // D = SEGMENT_BASE + OFFSET
                            @14 // general purpose register (13-15)
                            M=D
                            @13
                            D=M 
                            @14
                            A=M
                            M=D
                            """))
                        else:
                            print(striplines(f"""
                            @{offset}
                            D=A
                            @{SEG}
                            A=D+M // r0 = SEGMENT_BASE + OFFSET
                            D=M
                            {idiom('push D')}
                            """))
                    elif segment in ['temp','pointer','static']:
                        if segment == 'static':
                            addr = f'{module_name}.{offset}'
                        else:
                            base = 5 if segment == 'temp' else 3
                            addr = base + int(offset)
                        if command == 'pop':
                            print(striplines(f"""
                            {idiom('pop D')}
                            @{addr}
                            M=D
                            """))
                        else:
                            print(striplines(f"""
                            @{addr}
                            D=M
                            {idiom('push D')}
                            """))
                elif command == "add":
                    print(striplines(f"""
                    {idiom('pop D')}
                    @SP
                    AM=M-1
                    M=M+D
                    @SP
                    M=M+1
                    """))
                elif command == "sub":
                    print(striplines(f"""
                    {idiom('pop D')}
                    @SP
                    AM=M-1
                    M=M-D
                    @SP
                    M=M+1
                    """))
                elif command in ["eq", "gt", 'lt']:
                    jmp = 'JEQ' if command == 'eq' else ('JGT' if command == 'gt' else 'JLT')
                    id = getId()
                    print(striplines(f"""
                    {idiom('pop D')}
                    {idiom('pop A')}
                    D=A-D
                    @PUSHONE{id}
                    D;{jmp}
                    D=0 // if not GT
                    {idiom('push D')}
                    @END{id}
                    0;JMP
                    (PUSHONE{id}) // if gt
                    D=-1
                    {idiom('push D')}
                    (END{id})
                    """))
                elif command in ['and', 'or']:
                    op = '&' if command == 'and' else '|'
                    print(striplines(f"""
                    {idiom('pop D')}
                    {idiom('pop A')}
                    D=A{op}D
                    {idiom('push D')}
                    """))
                elif command in ['not', 'neg']:
                    op = '!' if command == 'not' else '-'
                    print(striplines(f"""
                    {idiom('pop D')}
                    D={op}D
                    {idiom('push D')}
                    """))



        



def striplines(s):
    return "\n".join([l.strip() for l in s.splitlines() if l.strip() != ""])

if __name__ == "__main__":
    main(sys.argv[1])