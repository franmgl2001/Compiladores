from globalTypes import *
from symtab import *


location = 0
current_function = None  # Track current function for return type checking
source_lines = []  # Global variable to store source code lines


# Funcion para cargar el código fuente
def load_code(filename):
    global source_lines
    with open(filename, "r") as file:
        source_lines = file.readlines()


# Funcion para mostrar un error de tipo
def typeError(t, message):
    global source_lines
    line_number = t.lineno
    print(f"Línea {line_number}: Error en el tipo: {message}")
    if 0 <= line_number - 1 < len(source_lines):
        print(source_lines[line_number - 2].rstrip())
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
    global location, current_function

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

        # Guardar el contexto de la funcion anterior
        prev_function = current_function
        # Establecer la funcion actual
        current_function = t

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
        # Salir de la funcion
        current_function = prev_function
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
    global location, current_function
    location = 0
    current_function = None
    scopes.clear()
    scope_names.clear()
    BucketList.clear()

    # Register built-in functions before traversing the AST
    register_builtin_functions()

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

        # Verificar que no se está usando un array sin el operador de índice
        is_array = st_get_is_array(t.name)
        if is_array:
            typeError(
                t,
                f"Array variable '{t.name}' must be accessed with an index (e.g., {t.name}[0])",
            )

    elif t.exp == ExpKind.ArrayK:
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

        # Verificar que la variable es un array
        is_array = st_get_is_array(t.name)
        if not is_array:
            typeError(
                t, f"Non-array variable '{t.name}' cannot be accessed with an index"
            )

        # Verificar que el indice sea de tipo entero
        if t.child[0]:
            check_expression(t.child[0])
            if t.child[0].type != ExpType.Integer:
                typeError(t.child[0], f"Array index must be an integer expression")

    elif t.exp == ExpKind.OpK:
        # Procesar los lados izquierdo y derecho de la operacion
        if t.child[0]:
            check_expression(t.child[0])
        if t.child[1]:
            check_expression(t.child[1])

        # Checar si es una asignacion
        if t.op == TokenType.EQ:
            # Check if left side is an array access or identifier
            left = t.child[0]
            if left and left.exp == ExpKind.IdK:
                # Check if trying to assign directly to an array
                is_array = st_get_is_array(left.name)
                if is_array:
                    typeError(
                        left,
                        f"Array variable '{left.name}' must be accessed with an index for assignment",
                    )

        # Establecer el tipo de resultado
        if t.child[0] and t.child[1]:
            # Por ahora, asumir que el tipo de resultado es el mismo que los operandos si coinciden
            if t.child[0].type == t.child[1].type:
                t.type = t.child[0].type
            else:
                # Type mismatch
                typeError(t, f"Type mismatch in operation")

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
    global current_function

    # Save the previous function context
    prev_function = current_function

    # If this is a function declaration, update current function
    if t.nodekind == NodeKind.DeclK and t.decl == DeclKind.FunK:
        current_function = t

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
                    "Error en el tipo de la expresión: se esperaba tipo Integer en la condición if",
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

        # Se verifica si estamos dentro de una funcion
        if current_function is None and t.nodekind == NodeKind.StmtK:
            return

        # Se obtiene el tipo de retorno de la funcion
        func_return_type = current_function.type

        if expr is None:
            # Se verifica si la funcion es de tipo void
            if func_return_type != ExpType.Void:
                typeError(
                    t,
                    f"Function '{current_function.name}' must return a value of type {func_return_type.name}",
                )
            return

        # Se verifica la integridad de la expresion
        check_expression(expr)

        # Se verifica si el tipo de la expresion es el mismo que el de la funcion
        if expr.type != func_return_type:
            typeError(
                t,
                f"Function '{current_function.name}' must return type {func_return_type.name}, but got {expr.type.name}",
            )

    for i in range(MAXCHILDREN):
        child = t.child[i]
        if child:
            check_statement_expression(child)

    if t.nodekind == NodeKind.DeclK and t.decl == DeclKind.FunK:
        current_function = prev_function


# Funcion para verificar la integridad del nodo
def check_node_integrity(t):
    if t.nodekind == NodeKind.StmtK:
        check_statement_expression(t)
    elif t.nodekind == NodeKind.ExpK:
        check_expression(t)
    elif t.nodekind == NodeKind.DeclK:
        if t.decl == DeclKind.FunK:
            # Procesar declaraciones de funciones
            global current_function
            prev_function = current_function
            current_function = t

            # Verificar el cuerpo de la funcion
            if t.child[1]:
                check_statement_expression(t.child[1])

            # Restaurar el contexto de la funcion anterior
            current_function = prev_function


def typeCheck(syntaxTree):
    global current_function
    current_function = None
    traverse(syntaxTree, lambda t: None, check_node_integrity)


# Function to register built-in functions in the symbol table
def register_builtin_functions():
    global location

    # Register input() function - takes no parameters and returns an integer
    input_params = [{"name": "value", "type": ExpType.Integer, "is_array": False}]
    input_metadata = {"params": input_params}
    st_insert(
        "input", 0, location, ExpType.Integer, is_array=False, metadata=input_metadata
    )
    location += 1

    # Register output() function - takes an integer parameter and returns void

    output_params = []
    output_metadata = {"params": output_params}
    st_insert(
        "output", 0, location, ExpType.Void, is_array=False, metadata=output_metadata
    )
    location += 1
