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

    if t.decl == DeclKind.FunK:
        param_list = []
        param_node = t.child[0]
        while param_node is not None:
            param_list.append(
                {
                    "name": param_node.name,
                    "type": param_node.type,
                    "is_array": param_node.decl == DeclKind.ParamArrayK,
                }
            )
            param_node = param_node.sibling

        func_metadata = {"params": param_list}
        st_insert(t.name, t.lineno, location, t.type, metadata=func_metadata)
    else:
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
        # Look up the function name
        sym = st_lookup(t.name)
        # If function not found, show error
        if sym == -1:
            typeError(t, f"Function '{t.name}' not declared")
            return

        # Get function type
        func_type = st_get_type(t.name)
        # Check if function is void
        if func_type == ExpType.Void:
            typeError(t, f"function '{t.name}' declared void")
        # Set the type of this node
        t.type = func_type

        # Get function parameters
        metadata = st_get_metadata(t.name)
        declared_params = metadata.get("params", [])

        # Get first argument
        call_arg = t.child[0]
        i = 0

        # Loop through arguments
        while call_arg != None and i < len(declared_params):
            # Check argument type
            check_expression(call_arg)
            # Get parameter info
            declared_param = declared_params[i]

            # Check if types match
            if call_arg.type != declared_param["type"]:
                # Show error for type mismatch
                typeError(
                    call_arg,
                    f"Argument {i+1} of function '{t.name}' expects type {declared_param['type'].name} but got {call_arg.type.name}",
                )
            # Move to next argument
            call_arg = call_arg.sibling
            i += 1

        # Check for too many arguments
        if call_arg != None:
            typeError(t, f"Too many arguments in call to function '{t.name}'")
        # Check for too few arguments
        elif i < len(declared_params):
            typeError(t, f"Too few arguments in call to function '{t.name}'")


def check_statement_expression(t):
    if t.stmt == StmtKind.IfK:
        cond = t.child[0]
        if cond is None:
            typeError(t, "Missing condition in if statement")
        else:
            check_expression(cond)
            if cond.type != ExpType.Integer:
                typeError(
                    cond,
                    "Condition in if statement must be an expression of type integer or bool",
                )

    elif t.stmt == StmtKind.WhileK:
        cond = t.child[0]
        if cond is None:
            typeError(t, "Missing condition in while loop")
        else:
            check_expression(cond)
            if cond.type != ExpType.Integer:
                typeError(
                    cond,
                    "Condition in while loop must be an expression of type integer or bool",
                )

    elif t.stmt == StmtKind.ReturnK:
        expr = t.child[0]
        # Some implementations allow "return;" with no expression (e.g., for void functions)
        if expr is None:
            return  # You could add function context checking here if needed
        check_expression(expr)


def check_node_integrity(t):
    if t.nodekind == NodeKind.StmtK:
        check_declaration(t)
        check_statement_expression(t)
    elif t.nodekind == NodeKind.ExpK:
        check_expression(t)


def typeCheck(syntaxTree):
    traverse(syntaxTree, lambda t: None, check_node_integrity)
