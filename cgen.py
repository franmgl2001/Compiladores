# cgen_mips.py: Code generator for C- AST to MIPS assembly
# Integrates with globalTypes, symtab, parser, and main.py in this project.

from globalTypes import *
from symtab import *

localOffset = 4
# Stack for function call management
functionStack = []
currentFunction = None

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

# Label counter for generating unique labels
label_counter = 0


def get_next_label():
    """Generate a unique label"""
    global label_counter
    label_counter += 1
    return f"L{label_counter}"


def emitFunctionProlog(funcName, f):
    """Generate function prologue"""
    f.write(f"\n# Function: {funcName}\n")
    f.write(f"{funcName}:\n")
    f.write("    # Function prologue\n")
    f.write("    subu $sp, $sp, 4       # make space for old $fp\n")
    f.write("    sw   $fp, 0($sp)       # save old frame pointer\n")
    f.write("    move $fp, $sp          # set new frame pointer\n")
    f.write("    subu $sp, $sp, 100     # allocate space for locals\n")


def emitFunctionEpilog(funcName, f):
    """Generate function epilogue"""
    f.write(f"    # Function epilogue for {funcName}\n")
    f.write("    move $sp, $fp          # restore stack pointer\n")
    f.write("    lw   $fp, 0($sp)       # restore old frame pointer\n")
    f.write("    addu $sp, $sp, 4       # deallocate space for old $fp\n")
    f.write("    jr   $ra               # return to caller\n")


def emitReturn(node, f):
    """Generate return statement"""
    f.write("    # Return statement\n")
    if node.child[0]:  # Return with value
        # Evaluate the return expression
        walkNode(node.child[0], f)
        f.write("    move $v0, $t0          # move return value to $v0\n")
    f.write("    # Function epilogue (return)\n")
    f.write("    move $sp, $fp          # restore stack pointer\n")
    f.write("    lw   $fp, 0($sp)       # restore old frame pointer\n")
    f.write("    addu $sp, $sp, 4       # deallocate space for old $fp\n")
    f.write("    jr   $ra               # return to caller\n")


def emitFunctionCall(node, f):
    """Generate function call"""
    if node.name in ["input", "output"]:
        # Handle built-in functions as before
        if node.name == "input":
            f.write("    # Input function call - store expression value\n")
            if node.child and node.child[0]:
                walkNode(node.child[0], f)
            else:
                f.write("    li   $v0, 5             # syscall 5 = read integer\n")
                f.write("    syscall                 # read integer into $v0\n")
                f.write("    move $t0, $v0           # move result to $t0\n")
            f.write("    sw   $t0, -4($fp)       # store input value at -4($fp)\n")

        elif node.name == "output":
            f.write("    # Output function call - print stored value\n")
            if node.child and node.child[0]:
                walkNode(node.child[0], f)
                f.write("    move $a0, $t0           # move expression result to $a0\n")
            else:
                f.write("    lw   $t0, -4($fp)       # load stored input value\n")
                f.write("    move $a0, $t0           # move stored value to $a0\n")

            f.write("    li   $v0, 1             # syscall 1 = print integer\n")
            f.write("    syscall                 # print the integer\n")
            f.write("    li   $v0, 11            # syscall 11 = print character\n")
            f.write("    li   $a0, 10            # ASCII 10 = newline\n")
            f.write("    syscall                 # print newline\n")
    else:
        # Handle user-defined function calls
        f.write(f"    # Function call: {node.name}\n")

        # Collect all arguments - try both approaches
        args = []

        # First try: collect from child-sibling chain starting at child[0]
        arg = node.child[0]  # First argument
        while arg:
            args.append(arg)
            arg = arg.sibling  # Next sibling is next argument

        # Second try: if we didn't get enough arguments, try collecting from all children
        if len(args) < 2 and len(node.child) > 1:
            args = []
            for i, child in enumerate(node.child):
                if child:
                    args.append(child)

        arg_count = len(args)
        f.write(f"    # Pushing {arg_count} arguments\n")

        # Push arguments onto stack in forward order (first arg pushed first)
        for i, arg in enumerate(args):
            f.write(f"    # Evaluate argument {i+1}\n")
            walkNode(arg, f)
            f.write("    subu $sp, $sp, 4       # make space for argument\n")
            f.write(f"    sw   $t0, 0($sp)       # push argument {i+1}\n")

        # Call the function (jal automatically saves return address in $ra)
        f.write(f"    jal  {node.name}           # call function {node.name}\n")

        # Clean up arguments from stack
        if arg_count > 0:
            f.write(
                f"    addu $sp, $sp, {arg_count * 4}  # remove arguments from stack\n"
            )

        # Function result is in $v0, move to $t0
        f.write("    move $t0, $v0          # move function result to $t0\n")


def walkNode(node, f):
    """Helper function to walk a single node - extracted from emitMainFunction"""
    if not node:
        return

    # Handle different node types
    if node.nodekind == NodeKind.ExpK:
        if node.exp == ExpKind.ConstK:
            # Load constant value into $t0
            f.write(f"    li   $t0, {node.val}       # load constant {node.val}\n")

        elif node.exp == ExpKind.IdK:
            # Use the existing loadVariable function
            loadVariable(node, f)

        elif node.exp == ExpKind.OpK:
            if node.op == TokenType.EQ:
                # Handle assignment operation (=)
                if node.child[1]:
                    walkNode(node.child[1], f)

                target = node.child[0]
                if target and target.exp == ExpKind.IdK:
                    location = -4
                    try:
                        sym_location = st_lookup(target.name)
                        if sym_location != -1:
                            loc_offset = st_get_offset(target.name)
                            if loc_offset is not None:
                                location = loc_offset
                    except:
                        pass

                    f.write(
                        f"    sw   $t0, {location}($fp)  # assign to {target.name} at offset {location}\n"
                    )
                    f.write(f"    # Assignment: {target.name} = expression\n")
                else:
                    f.write("    # ERROR: Invalid assignment target\n")

            elif node.op == TokenType.PLUS:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4       # make space on stack\n")
                    f.write("    sw   $t0, 0($sp)       # save left operand\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                f.write("    add  $t0, $t1, $t0     # add: $t0 = $t1 + $t0\n")

            elif node.op == TokenType.MINUS:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4       # make space on stack\n")
                    f.write("    sw   $t0, 0($sp)       # save left operand\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                f.write("    sub  $t0, $t1, $t0     # subtract: $t0 = $t1 - $t0\n")

            elif node.op == TokenType.TIMES:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4       # make space on stack\n")
                    f.write("    sw   $t0, 0($sp)       # save left operand\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                f.write("    mul  $t0, $t1, $t0     # multiply: $t0 = $t1 * $t0\n")

            elif node.op == TokenType.OVER:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4       # make space on stack\n")
                    f.write("    sw   $t0, 0($sp)       # save left operand\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                f.write("    div  $t1, $t0          # divide $t1 by $t0\n")
                f.write("    mflo $t0               # move quotient to $t0\n")

            # Comparison operators
            elif node.op == TokenType.LT:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4       # make space on stack\n")
                    f.write("    sw   $t0, 0($sp)       # save left operand\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                f.write(
                    "    slt  $t0, $t1, $t0     # set $t0 = 1 if $t1 < $t0, else 0\n"
                )

            elif node.op == TokenType.LE:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4       # make space on stack\n")
                    f.write("    sw   $t0, 0($sp)       # save left operand\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                f.write(
                    "    sle  $t0, $t1, $t0     # set $t0 = 1 if $t1 <= $t0, else 0\n"
                )

            elif node.op == TokenType.GT:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4       # make space on stack\n")
                    f.write("    sw   $t0, 0($sp)       # save left operand\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                f.write(
                    "    sgt  $t0, $t1, $t0     # set $t0 = 1 if $t1 > $t0, else 0\n"
                )

            elif node.op == TokenType.GE:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4       # make space on stack\n")
                    f.write("    sw   $t0, 0($sp)       # save left operand\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                f.write(
                    "    sge  $t0, $t1, $t0     # set $t0 = 1 if $t1 >= $t0, else 0\n"
                )

            elif node.op == TokenType.EQEQ:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4       # make space on stack\n")
                    f.write("    sw   $t0, 0($sp)       # save left operand\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                f.write(
                    "    seq  $t0, $t1, $t0     # set $t0 = 1 if $t1 == $t0, else 0\n"
                )

            elif node.op == TokenType.NE:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4       # make space on stack\n")
                    f.write("    sw   $t0, 0($sp)       # save left operand\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)       # load left operand into $t1\n")
                f.write("    addu $sp, $sp, 4       # restore stack pointer\n")
                f.write(
                    "    sne  $t0, $t1, $t0     # set $t0 = 1 if $t1 != $t0, else 0\n"
                )

        # For function calls
        elif node.exp == ExpKind.CallK:
            emitFunctionCall(node, f)

    # Handle statement nodes
    elif node.nodekind == NodeKind.StmtK:
        if node.stmt == StmtKind.ReturnK:
            emitReturn(node, f)

        elif node.stmt == StmtKind.IfK:
            f.write("    # If statement\n")

            if node.child[0]:
                walkNode(node.child[0], f)

            else_label = get_next_label()
            end_label = get_next_label()

            f.write(
                f"    beq  $t0, $zero, {else_label}  # branch to else if condition is false\n"
            )

            if node.child[1]:
                f.write("    # Then branch\n")
                walkNode(node.child[1], f)

            f.write(f"    j    {end_label}           # jump to end\n")
            f.write(f"{else_label}:\n")

            if node.child[2]:
                f.write("    # Else branch\n")
                walkNode(node.child[2], f)

            f.write(f"{end_label}:\n")
            f.write("    # End of if statement\n")

        elif node.stmt == StmtKind.WhileK:
            f.write("    # While statement\n")

            loop_start = get_next_label()
            loop_end = get_next_label()

            f.write(f"{loop_start}:\n")
            f.write("    # While condition\n")

            if node.child[0]:
                walkNode(node.child[0], f)

            f.write(
                f"    beq  $t0, $zero, {loop_end}  # exit loop if condition is false\n"
            )

            if node.child[1]:
                f.write("    # While body\n")
                walkNode(node.child[1], f)

            f.write(f"    j    {loop_start}          # jump back to condition\n")
            f.write(f"{loop_end}:\n")
            f.write("    # End of while statement\n")

        elif node.stmt == StmtKind.CompoundK:
            f.write("    # Compound statement\n")
            for child in node.child:
                if child:
                    walkNode(child, f)

    # Handle declaration nodes (but skip function declarations as they're handled separately)
    elif node.nodekind == NodeKind.DeclK:
        if node.decl == DeclKind.VarK:
            # Variable declarations are handled by allocDeclarations
            pass
        elif node.decl == DeclKind.FunK:
            # Function declarations are handled separately
            pass

    # Process sibling nodes
    if node.sibling:
        walkNode(node.sibling, f)


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


def collectAndEmitFunctions(node, f):
    """Collect and emit all function declarations except main"""
    if not node:
        return

    # Handle function declarations
    if node.nodekind == NodeKind.DeclK and node.decl == DeclKind.FunK:
        if node.name != "main":  # Don't emit main here, it's handled separately
            emitFunction(node, f)

    # Recurse on children and siblings
    for c in node.child:
        collectAndEmitFunctions(c, f)
    collectAndEmitFunctions(node.sibling, f)


def emitFunction(funcNode, f):
    """Generate code for a user-defined function"""
    if not funcNode or funcNode.name == "main":
        return

    funcName = funcNode.name

    # Generate function prologue
    emitFunctionProlog(funcName, f)

    # Copy arguments from caller's stack into parameter locations
    # Stack layout after prologue (no manual $ra saving):
    # Higher addresses: | arg1 | arg2 | old_fp | locals | ...
    #                     8($fp) 4($fp)  0($fp)   -4($fp)
    # Lower addresses:

    param = funcNode.child[0]
    arg_offset = 8  # First argument is at 8($fp)

    f.write("    # Copy arguments into parameter locations\n")
    while param:
        if param.nodekind == NodeKind.DeclK and param.decl == DeclKind.ParamK:
            # Get the parameter's local offset from symbol table
            param_location = st_get_offset(param.name)
            if param_location is not None:
                f.write(
                    f"    lw   $t0, {arg_offset}($fp)    # load argument from caller's stack\n"
                )
                f.write(
                    f"    sw   $t0, {param_location}($fp) # store into parameter {param.name}\n"
                )
                arg_offset -= 4  # Next argument at 4($fp)
        param = param.sibling

    # Process function body - child[1] is the compound statement
    if funcNode.child[1]:
        f.write(f"    # Function body for {funcName}\n")
        walkNode(funcNode.child[1], f)

    # Generate function epilogue (in case there's no explicit return)
    emitFunctionEpilog(funcNode, f)


def findMainFunction(node):
    """Find the main function declaration in the AST"""
    if not node:
        return None

    # Check if this is the main function
    if (
        node.nodekind == NodeKind.DeclK
        and node.decl == DeclKind.FunK
        and node.name == "main"
    ):
        return node

    # Recurse on children and siblings
    for c in node.child:
        result = findMainFunction(c)
        if result:
            return result

    return findMainFunction(node.sibling)


def emitMainFromDecl(mainNode, f):
    """Generate main function from its declaration node"""
    if not mainNode:
        return

    f.write("\n.text\n.globl main\nmain:\n")
    f.write("    # Set up stack frame for main\n")
    f.write("    move $fp, $sp           # frame pointer = stack pointer\n")
    f.write("    subu $sp, $sp, 100      # allocate space for locals\n")

    # Process main function body - child[1] is the compound statement
    if mainNode.child[1]:
        f.write("    # Main function body\n")
        walkNode(mainNode.child[1], f)

    # Clean up and exit program
    f.write("    # Restore stack and exit\n")
    f.write("    move $sp, $fp           # restore stack pointer\n")
    f.write("    li   $v0, 10            # exit program\n")
    f.write("    syscall\n")


def allocDeclarations(node):
    """First pass: traverse AST and process variable and parameter declarations."""
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

    # If this is a function declaration, handle its parameters as local variables
    elif node.nodekind == NodeKind.DeclK and node.decl == DeclKind.FunK:
        print(f"Processing function {node.name}")
        # Handle function parameters as local variables with negative offsets
        param = node.child[0]

        while param:
            if param.nodekind == NodeKind.DeclK and param.decl == DeclKind.ParamK:
                # Treat parameters like local variables - negative offsets
                localOffset += 4
                st_set_offset(param.name, -localOffset)
                print(f"Parameter {param.name} allocated at offset {-localOffset}")
            param = param.sibling

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

        # First, emit the main function (must be at top)
        mainFunc = findMainFunction(syntaxTree)
        if mainFunc:
            emitMainFromDecl(mainFunc, f)
        else:
            # Fallback: emit a simple main that processes the whole tree
            f.write("\n.text\n.globl main\nmain:\n")
            f.write("    # Set up stack frame for main\n")
            f.write("    move $fp, $sp           # frame pointer = stack pointer\n")
            f.write("    subu $sp, $sp, 100      # allocate space for locals\n")
            walkNode(syntaxTree, f)
            f.write("    # Restore stack and exit\n")
            f.write("    move $sp, $fp           # restore stack pointer\n")
            f.write("    li   $v0, 10            # exit program\n")
            f.write("    syscall\n")

        # Then, emit all other user-defined functions
        collectAndEmitFunctions(syntaxTree, f)

    # For debugging
    print(f"Assembly code generated to {outfname}")
    print("Using symbol table offsets for variable access")
    print("Main function emitted at top, followed by other functions")
