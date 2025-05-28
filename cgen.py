# cgen_mips.py: Code generator for C- AST to MIPS assembly
# Integrates with globalTypes, symtab, parser, and main.py in this project.

from globalTypes import *
from symtab import *

localOffset = 0

# Basic register names
regNames = {
    0: "$t0",  # accumulator
    1: "$t1",  # secondary accumulator
    5: "$gp",  # global pointer
    6: "$sp",  # stack pointer
}

# Simple tracing flag
TraceCode = False


def emitInputFunction(f):
    f.write("\n# --- input() reads an integer into $v0 ---\n")
    f.write("input:\n")
    f.write("    li   $v0, 5\n")
    f.write("    syscall\n")
    f.write("    jr   $ra\n")


def emitOutputFunction(f):
    f.write("\n# --- output() takes integer in $a0 ---\n")
    f.write("output:\n")
    f.write("    li   $v0, 1\n")
    f.write("    syscall\n")
    f.write("    li   $v0, 11\n")
    f.write("    li   $a0, 10\n")
    f.write("    syscall\n")
    f.write("    jr   $ra\n")


def emitMainFunction(AST, f):
    f.write("\n.text\n.globl main\nmain:\n")

    def walk(node):
        if not node:
            return

        # first recurse into children/siblings...
        for c in node.child:
            walk(c)
        walk(node.sibling)

        # then at leaf ExpK nodes:
        if node.nodekind == NodeKind.ExpK:
            if node.name == "input":
                # call input(), result in $v0
                f.write("    jal input\n")
                f.write("    move $t0, $v0       # save into $t0\n")

            elif node.name == "output":
                # argument is in $t0 (from previous input or expression)
                f.write("    move $a0, $t0       # set up print argument\n")
                f.write("    jal output\n")

    walk(AST)

    # exit program
    f.write("    li   $v0, 10\n")
    f.write("    syscall\n")


def allocDeclarations(node):
    """Primer pase: recorre el AST y procesa solo DeclK VarK."""
    global localOffset
    if not node:
        return
    # Si es declaración de variable
    if node.nodekind == NodeKind.DeclK and node.decl == DeclKind.VarK:
        # reservamos 4 bytes más
        localOffset += 4
        # insertamos en la tabla: location = -localOffset
        st_set_offset(node.name, -localOffset)
    # recursión
    for c in node.child:
        allocDeclarations(c)
    allocDeclarations(node.sibling)


def codeGen(syntaxTree, symtab, codefile, trace=False):
    """Generate MIPS assembly code - starting with just input and output functions"""
    global TraceCode
    TraceCode = trace

    # Ensure the output file has a .s extension
    outfname = codefile if codefile.endswith(".s") else f"{codefile}.s"

    # Open the file for writing
    with open(outfname, "w") as f:
        # Write header
        f.write("# C- Compilation to MIPS Assembly\n")
        f.write(f"# File: {outfname}\n")
        f.write("# Simple implementation with input() and output() functions\n\n")

        # Text section - contains code
        f.write(".text\n")
        f.write(".globl main\n\n")

        allocDeclarations(syntaxTree)

        printSymTab()
        # Emit the built-in functions
        emitInputFunction(f)
        emitOutputFunction(f)

        # Emit a simple main function to test
        emitMainFunction(syntaxTree, f)

        # For debugging
        print(f"Assembly code generated to {outfname}")
        print("This simplified version only implements input() and output() functions.")
