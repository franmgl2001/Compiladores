from globalTypes import *
from symtab import *


location = 0


def typeError(t, message):
    print("Type error at line", t.lineno, ":", message)
    Error = True


def traverse(t, preProc, postProc):
    if t is not None:
        preProc(t)
        for i in range(MAXCHILDREN):
            traverse(t.child[i], preProc, postProc)
        postProc(t)
        traverse(t.sibling, preProc, postProc)


def insert_declaration(t):
    global location

    if t.nodekind != NodeKind.DeclK:
        return
    # Checar que la
    if t.decl == DeclKind.VarK and t.type == ExpType.Void:
        typeError(t, f"variable '{t.name}' declared void")
        return

    if t.decl in (DeclKind.ParamK, DeclKind.ParamArrayK) and t.type == ExpType.Void:
        typeError(t, f"parameter '{t.name}' declared void")
        return

    if st_lookup(t.name) != -1:
        typeError(t, "Variable " + t.name + " already declared")
        return
    st_insert(t.name, t.lineno, location, t.type)
    location += 1


def buildSymtab(tree, imprime):
    global location
    location = 0
    traverse(tree, insert_declaration, lambda t: None)
    if imprime:
        printSymTab()


def check_declaration(t):
    if t.nodekind == NodeKind.DeclK:
        if t.decl == DeclKind.VarK and t.type == ExpType.Void:
            typeError(t, f"variable '{t.name}' declared void")
        if t.decl in (DeclKind.ParamK, DeclKind.ParamArrayK) and t.type == ExpType.Void:
            typeError(t, f"parameter '{t.name}' declared void")


def check_expression(t):
    if t.nodekind != NodeKind.ExpK:
        return

    if t.exp == ExpKind.ConstK:
        t.type = ExpType.Integer

    elif t.exp == ExpKind.IdK:
        sym = st_lookup(t.name)
        if sym == -1:
            typeError(t, f"Variable '{t.name}' not declared")
            return
        t.type = st_get_type(t.name)
        if t.type == ExpType.Void:
            typeError(t, f"variable '{t.name}' declared void")

    elif t.exp == ExpKind.CallK:
        sym = st_lookup(t.name)
        if sym == -1:
            typeError(t, f"Function '{t.name}' not declared")
            return
        t.type = st_get_type(t.name)
        if t.type == ExpType.Void:
            typeError(t, f"function '{t.name}' declared void")


def check_node_integrity(t):
    if t.nodekind == NodeKind.StmtK:
        check_declaration(t)
    elif t.nodekind == NodeKind.ExpK:
        check_expression(t)


def typeCheck(syntaxTree):
    traverse(syntaxTree, lambda t: None, check_node_integrity)
