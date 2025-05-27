"""
cgen.py: Code generator for Tiny C- AST to TM code
Integrates with globalTypes, symtab, parser, and main.py in this project.
"""

from globalTypes import NodeKind, StmtKind, ExpKind, TokenType
from symtab import st_lookup
import sys

# Machine registers and pointers
pc = 7  # program counter base
mp = 6  # memory pointer for temporaries
gp = 5  # global pointer for globals
ac = 0  # accumulator
ac1 = 1  # secondary accumulator
emitLoc = 0  # current TM instruction location
highEmitLoc = 0  # highest emitted location for backpatch
TraceCode = False


def emitComment(c):
    """Print a comment if tracing is enabled"""
    if TraceCode:
        print(f"* {c}")


def emitRO(op, r, s, t, c):
    """Emit a register-only TM instruction"""
    global emitLoc, highEmitLoc
    print(f"{emitLoc:3d}: {op:5s} {r},{s},{t}", end="")
    emitLoc += 1
    if TraceCode:
        print(f"\t{c}", end="")
    print()
    highEmitLoc = max(highEmitLoc, emitLoc)


def emitRM(op, r, d, s, c):
    """Emit a register-to-memory TM instruction"""
    global emitLoc, highEmitLoc
    print(f"{emitLoc:3d}: {op:5s} {r},{d}({s})", end="")
    emitLoc += 1
    if TraceCode:
        print(f"\t{c}", end="")
    print()
    highEmitLoc = max(highEmitLoc, emitLoc)


def emitRM_Abs(op, r, a, c):
    """Emit a PC-relative TM instruction given absolute address a"""
    global emitLoc, highEmitLoc, pc
    offset = a - (emitLoc + 1)
    print(f"{emitLoc:3d}: {op:5s} {r},{offset}({pc})", end="")
    emitLoc += 1
    if TraceCode:
        print(f"\t{c}", end="")
    print()
    highEmitLoc = max(highEmitLoc, emitLoc)


def emitSkip(howMany):
    """Skip howMany locations for backpatching; return current loc"""
    global emitLoc, highEmitLoc
    loc = emitLoc
    emitLoc += howMany
    highEmitLoc = max(highEmitLoc, emitLoc)
    return loc


def emitBackup(loc):
    """Back up to a previously skipped location"""
    global emitLoc, highEmitLoc
    if loc > highEmitLoc:
        emitComment("BUG in emitBackup: loc > highEmitLoc")
    emitLoc = loc


def emitRestore():
    """Restore emission loc to highest unemitted"""
    global emitLoc, highEmitLoc
    emitLoc = highEmitLoc


# Offset for temporaries on the stack
tmpOffset = 0


def genStmt(tree):
    """Generate code for a statement node"""
    if tree.stmt == StmtKind.IfK:
        emitComment("-> if")
        test, thenb, elseb = tree.child
        cGen(test)
        saved1 = emitSkip(1)
        emitComment("if: jump to else")
        cGen(thenb)
        saved2 = emitSkip(1)
        emitComment("if: jump to end")
        locThenEnd = emitSkip(0)
        emitBackup(saved1)
        emitRM_Abs("JEQ", ac, locThenEnd, "if false jump")
        emitRestore()
        cGen(elseb)
        locElseEnd = emitSkip(0)
        emitBackup(saved2)
        emitRM_Abs("LDA", pc, locElseEnd, "jmp end")
        emitRestore()
        emitComment("<- if")
    elif tree.stmt == StmtKind.WhileK:
        emitComment("-> while")
        loopStart = emitSkip(0)
        test, body = tree.child[0], tree.child[1]
        cGen(test)
        saved = emitSkip(1)
        emitComment("while: exit if false")
        cGen(body)
        emitRM_Abs("LDA", pc, loopStart, "jmp loop")
        locLoopEnd = emitSkip(0)
        emitBackup(saved)
        emitRM_Abs("JEQ", ac, locLoopEnd, "exit loop")
        emitRestore()
        emitComment("<- while")
    elif tree.stmt == StmtKind.AssignK:
        emitComment("-> assign")
        cGen(tree.child[0])
        addr = st_lookup(tree.name)
        emitRM("ST", ac, addr, gp, f"assign {tree.name}")
        emitComment("<- assign")
    elif tree.stmt == StmtKind.ReturnK:
        # placeholder: user can extend to restore fp, return value, etc.
        emitComment("-> return")
        # assume expr in child[0]
        if tree.child[0]:
            cGen(tree.child[0])
            # value in ac
        emitRO("RET", 0, 0, 0, "return")
        emitComment("<- return")
    elif tree.stmt == StmtKind.CompoundK:
        # compound: generate for each child
        for c in tree.child:
            cGen(c)
    # Note: ReadK/WriteK not in this grammar


def genExp(tree):
    """Generate code for an expression node"""
    global tmpOffset
    if tree.exp == ExpKind.ConstK:
        emitComment("-> Const")
        emitRM("LDC", ac, tree.val, 0, f"load const {tree.val}")
        emitComment("<- Const")
    elif tree.exp == ExpKind.IdK:
        emitComment("-> Id")
        addr = st_lookup(tree.name)
        emitRM("LD", ac, addr, gp, f"load id {tree.name}")
        emitComment("<- Id")
    elif tree.exp == ExpKind.OpK:
        emitComment("-> Op")
        # Debug information
        if len(tree.child) != 2:
            print(
                f"Warning: Operation node has {len(tree.child)} children (expected 2)",
                file=sys.stderr,
            )
            if hasattr(tree, "op"):
                print(f"Operation type: {tree.op}", file=sys.stderr)
            if hasattr(tree, "lineno"):
                print(f"Line number: {tree.lineno}", file=sys.stderr)

        # Check the number of children before unpacking
        if len(tree.child) >= 2:
            left, right = tree.child[0], tree.child[1]
            cGen(left)
            emitRM("ST", ac, tmpOffset, mp, "push left")
            tmpOffset -= 1
            cGen(right)
            tmpOffset += 1
            emitRM("LD", ac1, tmpOffset, mp, "pop left")
            # arithmetic
            if tree.op == TokenType.PLUS:
                emitRO("ADD", ac, ac1, ac, "+")
            elif tree.op == TokenType.MINUS:
                emitRO("SUB", ac, ac1, ac, "-")
            elif tree.op == TokenType.TIMES:
                emitRO("MUL", ac, ac1, ac, "*")
            elif tree.op == TokenType.OVER:
                emitRO("DIV", ac, ac1, ac, "/")
            # relational
            elif tree.op == TokenType.LT:
                emitRO("SUB", ac, ac1, ac, "<")
                emitRM("JLT", ac, 2, pc, "br if true")
                emitRM("LDC", ac, 0, ac, "false")
                emitRM("LDA", pc, 1, pc, "jmp next")
                emitRM("LDC", ac, 1, ac, "true")
            elif tree.op == TokenType.EQ:
                emitRO("SUB", ac, ac1, ac, "==")
                emitRM("JEQ", ac, 2, pc, "br if true")
                emitRM("LDC", ac, 0, ac, "false")
                emitRM("LDA", pc, 1, pc, "jmp next")
                emitRM("LDC", ac, 1, ac, "true")
        else:
            emitComment("Error: Operation requires at least 2 operands")
        emitComment("<- Op")
    # Note: CallK, ArrayK not yet implemented


def cGen(tree):
    """Recursively traverse AST and generate code"""
    if tree is None:
        return
    if tree.nodekind == NodeKind.StmtK:
        genStmt(tree)
    elif tree.nodekind == NodeKind.ExpK:
        genExp(tree)
    # skip DeclK (variable and function declarations)
    cGen(tree.sibling)


def codeGen(syntaxTree, codefile, trace=False):
    """
    Generate TM code from syntaxTree, write to codefile (adds .tm if missing).
    """
    global TraceCode, emitLoc, highEmitLoc
    TraceCode = trace
    emitLoc = highEmitLoc = 0
    # choose output filename
    outfname = codefile if codefile.endswith(".tm") else f"{codefile}.tm"
    # redirect stdout
    old_stdout = sys.stdout
    sys.stdout = open(outfname, "w")
    emitComment("TINY Compilation to TM Code")
    emitComment(f"File: {outfname}")
    # standard prelude
    emitComment("Standard prelude:")
    emitRM("LD", mp, 0, ac, "load maxaddress")
    emitRM("ST", ac, 0, ac, "clear loc 0")
    emitComment("End of standard prelude.")
    # generate program body
    cGen(syntaxTree)
    emitComment("End of execution.")
    emitRO("HALT", 0, 0, 0, "")
    # restore stdout
    sys.stdout.close()
    sys.stdout = old_stdout
