from globalTypes import *
from symtab import *


location = 0


# Funcion para mostrar un error de tipo
def typeError(t, message):
    print("Type error at line", t.lineno, ":", message)
    Error = True


# Funcion para recorrer el arbol sintactico
def traverse(t, preProc, postProc):
    if t is None:
        return
    preProc(t)
    # Recorre los hijos del nodo
    for i in range(MAXCHILDREN):
        traverse(t.child[i], preProc, postProc)
    postProc(t)
    traverse(t.sibling, preProc, postProc)


# Funcion para crear un nuevo scope para las declaraciones y sentencias compuestas
# Me ayude con chatgpt, ya que no estaba saliendo la implementacion de los scopes
def handle_scope(t):
    if t.nodekind == NodeKind.StmtK and t.stmt == StmtKind.CompoundK:
        enter_scope("compound")

        child = t.child[0]
        # Recorre los hijos del nodo
        while child is not None:
            insert_declaration(child)
            child = child.sibling
        # Una vez se han insertado las declaraciones y sentencias, se sale del scope
        exit_scope()
        return True

    return False


# Funcion para insertar una declaracion en el scope actual
def insert_declaration(t):
    global location

    if t.nodekind != NodeKind.DeclK:
        return

    if t.decl == DeclKind.VarK and t.type == ExpType.Void:
        typeError(t, f"variable '{t.name}' declared void")
        return

    if t.decl in (DeclKind.ParamK, DeclKind.ParamArrayK) and t.type == ExpType.Void:
        typeError(t, f"parameter '{t.name}' declared void")
        return

    if t.decl == DeclKind.FunK:
        # Si el simbolo ya existe en el scope actual, se muestra un error
        if st_lookup_current_scope(t.name) != -1:
            typeError(t, f"Function '{t.name}' already declared")
            return

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
        st_insert(
            t.name, t.lineno, location, t.type, is_array=False, metadata=func_metadata
        )
        location += 1

        # Se crea un nuevo scope para las declaraciones y sentencias de la funcion
        enter_scope(t.name)

        # Se insertan los parametros en el nuevo scope
        param_node = t.child[0]
        while param_node is not None:
            if st_lookup_current_scope(param_node.name) != -1:
                typeError(param_node, f"Parameter '{param_node.name}' already declared")
            else:
                st_insert(
                    param_node.name,
                    param_node.lineno,
                    location,
                    param_node.type,
                    is_array=(param_node.decl == DeclKind.ParamArrayK),
                )
                location += 1
            param_node = param_node.sibling

        # Se visita el cuerpo de la funcion
        traverse(t.child[1], insert_declaration, lambda t: None)

        exit_scope()
        return

    # Si el simbolo ya existe en el scope actual, se muestra un error
    if st_lookup_current_scope(t.name) != -1:
        typeError(t, "Variable " + t.name + " already declared")
        return
    # Se inserta el simbolo en el scope actual
    st_insert(t.name, t.lineno, location, t.type, is_array=t.is_array)
    location += 1


# Funcion para recorrer el arbol sintactico con un scope
# Me ayude con chatgpt, ya que no estaba saliendo la implementacion de los scopes
def custom_traverse(t):
    if t is None:
        return
    handled = handle_scope(t)
    if not handled:
        insert_declaration(t)
        for i in range(MAXCHILDREN):
            custom_traverse(t.child[i])
    custom_traverse(t.sibling)


# Funcion para construir la tabla de simbolos
def buildSymtab(tree, imprime):
    global location
    location = 0
    scopes.clear()
    scope_names.clear()
    BucketList.clear()

    # Custom traversal that handles scopes

    # Start traversal with custom scope-aware function
    custom_traverse(tree)

    if imprime:
        printSymTab()


# Funcion para verificar una declaracion
def check_declaration(t):
    if t.nodekind == NodeKind.DeclK:
        if t.decl == DeclKind.VarK and t.type == ExpType.Void:
            typeError(t, f"variable '{t.name}' declared void")
        if t.decl in (DeclKind.ParamK, DeclKind.ParamArrayK) and t.type == ExpType.Void:
            typeError(t, f"parameter '{t.name}' declared void")


# Funcion para verificar una expresion
def check_expression(t):
    if t.nodekind != NodeKind.ExpK:
        return

    if t.exp == ExpKind.ConstK:
        t.type = ExpType.Integer

    elif t.exp == ExpKind.IdK:
        # Se busca el simbolo en el scope actual
        sym = st_lookup_current_scope(t.name)
        if sym == -1:
            # Si el simbolo no existe en el scope actual, se muestra un error
            typeError(t, f"Variable '{t.name}' not declared")
            return
        t.type = st_get_type(t.name)
        if t.type == ExpType.Void:
            # Si el simbolo es de tipo void, se muestra un error
            typeError(t, f"variable '{t.name}' declared void")

    elif t.exp == ExpKind.CallK:
        sym = st_lookup_current_scope(t.name)
        if sym == -1:
            # Si el simbolo no existe en el scope actual, se muestra un error
            typeError(t, f"Function '{t.name}' not declared")
            return

        func_type = st_get_type(t.name)
        if func_type == ExpType.Void:
            # Si el simbolo es de tipo void, se muestra un error
            typeError(t, f"function '{t.name}' declared void")
        t.type = func_type

        # Se obtiene la informacion del simbolo en caso de funciones parametros
        metadata = st_get_metadata(t.name)
        declared_params = metadata.get("params", [])

        # Se recorre los argumentos de la llamada a la funcion
        call_arg = t.child[0]
        i = 0
        while call_arg != None and i < len(declared_params):
            # Se verifica la integridad de la expresion
            check_expression(call_arg)
            # Se obtiene el parametro declarado
            declared_param = declared_params[i]
            # Se verifica si el tipo de los argumentos es el mismo que el de los parametros
            if call_arg.type != declared_param["type"]:
                typeError(
                    call_arg,
                    f"Argument {i+1} of function '{t.name}' expects type {declared_param['type'].name} but got {call_arg.type.name}",
                )
            # Se pasa al siguiente argumento
            call_arg = call_arg.sibling
            i += 1

        # Se verifica si hay demasiados argumentos
        if call_arg != None:
            typeError(t, f"Too many arguments in call to function '{t.name}'")
        # Se verifica si hay demasiados argumentos
        elif i < len(declared_params):
            typeError(t, f"Too few arguments in call to function '{t.name}'")


# Funcion para verificar una sentencia
def check_statement_expression(t):
    # Se verifica si la sentencia es una sentencia if
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
    # Se verifica si la sentencia es una sentencia while
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
    # Se verifica si la sentencia es una sentencia return
    elif t.stmt == StmtKind.ReturnK:
        expr = t.child[0]
        if expr is None:
            return
        check_expression(expr)


# Funcion para verificar la integridad del nodo
def check_node_integrity(t):
    if t.nodekind == NodeKind.StmtK:
        check_declaration(t)
        check_statement_expression(t)
    elif t.nodekind == NodeKind.ExpK:
        check_expression(t)


def typeCheck(syntaxTree):
    traverse(syntaxTree, lambda t: None, check_node_integrity)
