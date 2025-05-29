# cgen_mips.py: Code generator for C- AST to MIPS assembly
# Integrates with globalTypes, symtab, parser, and main.py in this project.

from globalTypes import *
from symtab import *

localOffset = 4

# Basic register names
regNames = {
    0: "$t0",  # accumulator
    1: "$t1",  # secondary accumulator
    5: "$gp",  # global pointer
    6: "$sp",  # stack pointer
    8: "$fp",  # frame pointer
}

# Simple tracing flag
TraceCode = False


def loadVariable(node, f):
    """Load a variable's value from its memory location into $t0"""
    if not node or node.exp != ExpKind.IdK:
        return False

    # Get the memory location for this variable
    location = -4  # Default offset if not found

    # Try to get the actual offset
    try:
        # Check if this variable exists in the symbol table
        sym_location = st_lookup(node.name)
        if sym_location != -1:
            # Get its offset
            loc_offset = st_get_offset(node.name)
            if loc_offset is not None:
                location = loc_offset
    except:
        pass

    # Load variable from stack using offset from $fp
    f.write(
        f"    lw   $t0, {location}($fp)  # load {node.name} from offset {location}\n"
    )
    return True


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


def collectGlobals(tree, globals_list):
    """Collect all global variables"""
    if not tree:
        return

    # If this is a variable declaration
    if tree.nodekind == NodeKind.DeclK and tree.decl == DeclKind.VarK:
        if tree.name and tree.name not in globals_list:
            globals_list.append(tree.name)

    # Also check for variables used in expressions
    if tree.nodekind == NodeKind.ExpK and tree.exp == ExpKind.IdK:
        if tree.name and tree.name not in globals_list:
            globals_list.append(tree.name)

    # Check assignment targets
    if (
        tree.nodekind == NodeKind.ExpK
        and tree.exp == ExpKind.OpK
        and tree.op == TokenType.EQ
    ):
        if tree.child[0] and tree.child[0].exp == ExpKind.IdK:
            if tree.child[0].name and tree.child[0].name not in globals_list:
                globals_list.append(tree.child[0].name)

    # Recurse on children and siblings
    for c in tree.child:
        collectGlobals(c, globals_list)
    collectGlobals(tree.sibling, globals_list)


def emitMainFunction(AST, f):
    """Generate main function with stack-based variable access"""
    f.write("\n.text\n.globl main\nmain:\n")

    # Set up stack frame for main
    f.write("    # Set up stack frame\n")
    f.write("    move $fp, $sp           # frame pointer = stack pointer\n")
    f.write("    subu $sp, $sp, 100      # allocate space for locals\n")

    def walk(node):
        if not node:
            return

        # Handle different node types
        if node.nodekind == NodeKind.ExpK:
            if node.exp == ExpKind.ConstK:
                # Load constant value into $t0
                f.write(f"    li   $t0, {node.val}       # load constant {node.val}\n")

            elif node.exp == ExpKind.IdK:
                # Use the new loadVariable function
                loadVariable(node, f)

            elif node.exp == ExpKind.OpK:
                if node.op == TokenType.EQ:
                    # Handle assignment operation (=)
                    # First evaluate the right side expression
                    if node.child[1]:
                        walk(node.child[1])  # This puts the result in $t0

                    # Get target variable (left child)
                    target = node.child[0]
                    if target and target.exp == ExpKind.IdK:
                        # Get the memory location for this variable
                        location = -4  # Default offset if not found

                        # Try to get the actual offset
                        try:
                            # Check if this variable exists in the symbol table
                            sym_location = st_lookup(target.name)
                            if sym_location != -1:
                                # Get its offset
                                loc_offset = st_get_offset(target.name)
                                if loc_offset is not None:
                                    location = loc_offset
                        except:
                            pass

                        # Store value to stack using offset from $fp
                        f.write(
                            f"    sw   $t0, {location}($fp)  # assign to {target.name} at offset {location}\n"
                        )
                        f.write(f"    # Assignment: {target.name} = expression\n")
                    else:
                        f.write("    # ERROR: Invalid assignment target\n")

                elif node.op == TokenType.PLUS:
                    # Handle addition operation (+)
                    # Evaluate left operand first
                    if node.child[0]:
                        walk(node.child[0])  # Result in $t0
                        f.write("    subu $sp, $sp, 4       # make space on stack\n")
                        f.write("    sw   $t0, 0($sp)       # save left operand\n")

                    # Evaluate right operand
                    if node.child[1]:
                        walk(node.child[1])  # Result in $t0

                    # Load left operand and add
                    f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                    f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                    f.write("    add  $t0, $t1, $t0     # add: $t0 = $t1 + $t0\n")

                elif node.op == TokenType.MINUS:
                    # Handle subtraction operation (-)
                    # Evaluate left operand first
                    if node.child[0]:
                        walk(node.child[0])  # Result in $t0
                        f.write("    subu $sp, $sp, 4       # make space on stack\n")
                        f.write("    sw   $t0, 0($sp)       # save left operand\n")

                    # Evaluate right operand
                    if node.child[1]:
                        walk(node.child[1])  # Result in $t0

                    # Load left operand and subtract
                    f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                    f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                    f.write("    sub  $t0, $t1, $t0     # subtract: $t0 = $t1 - $t0\n")

                elif node.op == TokenType.TIMES:
                    # Handle multiplication operation (*)
                    # Evaluate left operand first
                    if node.child[0]:
                        walk(node.child[0])  # Result in $t0
                        f.write("    subu $sp, $sp, 4       # make space on stack\n")
                        f.write("    sw   $t0, 0($sp)       # save left operand\n")

                    # Evaluate right operand
                    if node.child[1]:
                        walk(node.child[1])  # Result in $t0

                    # Load left operand and multiply
                    f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                    f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                    f.write("    mul  $t0, $t1, $t0     # multiply: $t0 = $t1 * $t0\n")

                elif node.op == TokenType.OVER:
                    # Handle division operation (/)
                    # Evaluate left operand first
                    if node.child[0]:
                        walk(node.child[0])  # Result in $t0
                        f.write("    subu $sp, $sp, 4       # make space on stack\n")
                        f.write("    sw   $t0, 0($sp)       # save left operand\n")

                    # Evaluate right operand
                    if node.child[1]:
                        walk(node.child[1])  # Result in $t0

                    # Load left operand and divide
                    f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                    f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                    f.write("    div  $t1, $t0          # divide $t1 by $t0\n")
                    f.write("    mflo $t0               # move quotient to $t0\n")

            # For function calls
            elif node.exp == ExpKind.CallK:
                if node.name == "input":
                    # Input function: evaluate expression and store it at a fixed location
                    f.write("    # Input function call - store expression value\n")
                    if node.child and node.child[0]:
                        # Evaluate the argument expression - result will be in $t0
                        walk(node.child[0])
                    else:
                        # If no argument, read from user
                        f.write(
                            "    li   $v0, 5             # syscall 5 = read integer\n"
                        )
                        f.write("    syscall                 # read integer into $v0\n")
                        f.write("    move $t0, $v0           # move result to $t0\n")

                    # Store the value at a fixed memory location (e.g., -4($fp))
                    f.write(
                        "    sw   $t0, -4($fp)       # store input value at -4($fp)\n"
                    )

                elif node.name == "output":
                    # Output function: print the stored value
                    f.write("    # Output function call - print stored value\n")
                    if node.child and node.child[0]:
                        # If there's an argument, evaluate and print it directly
                        walk(node.child[0])
                        f.write(
                            "    move $a0, $t0           # move expression result to $a0\n"
                        )
                    else:
                        # If no argument, print the stored value from input
                        f.write(
                            "    lw   $t0, -4($fp)       # load stored input value\n"
                        )
                        f.write(
                            "    move $a0, $t0           # move stored value to $a0\n"
                        )

                    # Print the value
                    f.write("    li   $v0, 1             # syscall 1 = print integer\n")
                    f.write("    syscall                 # print the integer\n")
                    f.write(
                        "    li   $v0, 11            # syscall 11 = print character\n"
                    )
                    f.write("    li   $a0, 10            # ASCII 10 = newline\n")
                    f.write("    syscall                 # print newline\n")

        # Process children and siblings for non-expression nodes
        if node.nodekind != NodeKind.ExpK or node.exp not in [ExpKind.OpK]:
            for c in node.child:
                walk(c)
        walk(node.sibling)

    # Process the AST
    walk(AST)

    # Clean up and exit program
    f.write("    # Restore stack and exit\n")
    f.write("    move $sp, $fp           # restore stack pointer\n")
    f.write("    li   $v0, 10            # exit program\n")
    f.write("    syscall\n")


def allocDeclarations(node):
    """First pass: traverse AST and process variable declarations only."""
    global localOffset
    if not node:
        return
    # If this is a variable declaration
    if node.nodekind == NodeKind.DeclK and node.decl == DeclKind.VarK:
        # Reserve 4 more bytes
        localOffset += 4
        # Insert in table: location = -localOffset (negative offset from frame pointer)
        st_set_offset(node.name, -localOffset)
        print(f"Variable {node.name} allocated at offset {-localOffset}")
    # Recursion
    for c in node.child:
        allocDeclarations(c)
    allocDeclarations(node.sibling)


def codeGen(syntaxTree, symtab, codefile, trace=False):
    """Generate MIPS assembly code with proper symbol table usage"""
    global TraceCode
    TraceCode = trace

    # Ensure the output file has a .s extension
    outfname = codefile if codefile.endswith(".s") else f"{codefile}.s"

    # Open the file for writing
    with open(outfname, "w") as f:
        # Write header
        f.write("# C- Compilation to MIPS Assembly\n")
        f.write(f"# File: {outfname}\n")
        f.write("# Using symbol table offsets for variable access\n\n")

        # Process variable declarations to set up offsets
        allocDeclarations(syntaxTree)

        # Print symbol table for debugging
        if trace:
            printSymTab()

        # Emit the built-in functions
        # emitInputFunction(f)
        # emitOutputFunction(f)

        # Emit main function with proper variable handling
        emitMainFunction(syntaxTree, f)

    # For debugging
    print(f"Assembly code generated to {outfname}")
    print("Using symbol table offsets for variable access")
