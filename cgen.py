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

        # first recurse into children/siblings...
        for c in node.child:
            walk(c)
        walk(node.sibling)

        # then at leaf ExpK nodes:
        if node.nodekind == NodeKind.ExpK:
            if node.exp == ExpKind.ConstK:
                # Load constant value into $t0
                f.write(f"    li   $t0, {node.val}       # load constant {node.val}\n")

            elif node.exp == ExpKind.IdK:
                # Use the new loadVariable function
                loadVariable(node, f)

            elif node.exp == ExpKind.OpK and node.op == TokenType.EQ:
                # Handle assignment operation (=)
                # Right side expression already evaluated and result is in $t0

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

            # For function calls
            elif node.exp == ExpKind.CallK:
                if node.name == "input":
                    # Get input and save directly to -4($fp)
                    # Get the argument value from the child node
                    if node.child and len(node.child) > 0:
                        arg_node = node.child[0]
                        if arg_node.exp == ExpKind.ConstK:
                            f.write(
                                f"    li   $t0, {arg_node.val}         # load the constant {arg_node.val} into a temp reg\n"
                            )
                            f.write(
                                "    sw   $t0, -4($fp)   # save it to stack slot at fp–4\n"
                            )

                elif node.name == "output":
                    # Print value directly from -4($fp)
                    f.write("    lw   $a0, -4($fp)   # load it back into $a0\n")
                    f.write("    li   $v0, 1         # syscall 1 = print integer\n")
                    f.write("    syscall\n")

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
