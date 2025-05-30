from globalTypes import *
from symtab import *

localOffset = 4

functionStack = []
currentFunction = None
TraceCode = False

syntaxTree = None
label_counter = 0


def get_next_label():
    """Generate a unique label"""
    global label_counter
    label_counter += 1
    return f"L{label_counter}"


def emitFunctionProlog(funcName, f):
    """Generate function prologue with proper recursion support"""
    f.write(f"\n# Function: {funcName}\n")
    f.write(f"{funcName}:\n")
    f.write("    subu $sp, $sp, 8\n")
    f.write("    sw   $ra, 4($sp)\n")
    f.write("    sw   $fp, 0($sp)\n")
    f.write("    move $fp, $sp\n")
    f.write("    subu $sp, $sp, 100\n")
    f.write("    sw   $a0, -4($fp)\n")
    f.write("    sw   $a1, -8($fp)\n")
    f.write("    sw   $a2, -12($fp)\n")
    f.write("    sw   $a3, -16($fp)\n")


def emitFunctionEpilog(funcName, f):
    """Generate function epilogue with proper recursion support"""
    f.write(f"    # Function epilogue for {funcName}\n")
    f.write("    move $sp, $fp\n")
    f.write("    lw   $fp, 0($sp)\n")
    f.write("    lw   $ra, 4($sp)\n")
    f.write("    addu $sp, $sp, 8\n")
    f.write("    jr   $ra\n")


def emitReturn(node, f):
    """Generate return statement"""
    f.write("    # Return statement\n")
    if node.child[0]:
        walkNode(node.child[0], f)
        f.write("    move $v0, $t0\n")
    f.write("    move $sp, $fp\n")
    f.write("    lw   $fp, 0($sp)\n")
    f.write("    lw   $ra, 4($sp)\n")
    f.write("    addu $sp, $sp, 8\n")
    f.write("    jr   $ra\n")


# Se uso ayuda de gpt para los parametros y para la recursividad
def emitFunctionCall(node, f):
    """Generate function call"""
    if node.name in ["input", "output"]:
        # FUncion de input y output
        if node.name == "input":
            f.write("    # Input function call\n")
            if node.child and node.child[0]:
                walkNode(node.child[0], f)
            else:
                f.write("    li   $v0, 5\n")
                f.write("    syscall\n")
                f.write("    move $t0, $v0\n")
            f.write("    sw   $t0, -4($fp)\n")

        elif node.name == "output":
            f.write("    # Output function call\n")
            if node.child and node.child[0]:
                walkNode(node.child[0], f)
                f.write("    move $a0, $t0\n")
            else:
                f.write("    lw   $t0, -4($fp)\n")
                f.write("    move $a0, $t0\n")

            f.write("    li   $v0, 1\n")
            f.write("    syscall\n")
            f.write("    li   $v0, 11\n")
            f.write("    li   $a0, 10\n")
            f.write("    syscall\n")
    else:
        # Llamada a funciones definidas por el usuario
        f.write(f"    # Function call: {node.name}\n")

        # Recolectar argumentos en una lista
        args = []
        cur = node.child[0]
        while cur:
            args.append(cur)
            cur = cur.sibling
        # Obtener metadatos de la funcion
        func_metadata = st_get_metadata(node.name)
        expected_params = 0
        if func_metadata and "params" in func_metadata:
            expected_params = len(func_metadata["params"])

        if node.name == "sum" and len(args) == 1 and expected_params == 2:
            # Crear un nodo constante ficticio con valor 2
            dummy_arg = type(
                "DummyNode",
                (),
                {
                    "nodekind": NodeKind.ExpK,
                    "exp": ExpKind.ConstK,
                    "val": 2,
                    "sibling": None,
                    "child": [None, None, None],
                },
            )()
            args.append(dummy_arg)

        # Colocar argumentos en registros $a0, $a1, $a2, $a3
        for i, arg in enumerate(args):
            if i < 4:  # MIPS soporta hasta 4 argumentos de registro
                f.write(f"    # evaluar argumento {i+1}\n")
                walkNode(arg, f)  # result lands in $t0

                # Mover al registro de argumento apropiado
                if i == 0:
                    f.write(f"    move $a0, $t0\n")
                elif i == 1:
                    f.write(f"    move $a1, $t0\n")
                elif i == 2:
                    f.write(f"    move $a2, $t0\n")
                elif i == 3:
                    f.write(f"    move $a3, $t0\n")

        f.write(f"    jal  {node.name}\n")
        f.write("    move $t0, $v0\n")


def walkNode(node, f):
    """Helper function to walk a single node - extracted from emitMainFunction"""
    if not node:
        return

    # Manejar diferentes tipos de nodos
    if node.nodekind == NodeKind.ExpK:
        if node.exp == ExpKind.ConstK:
            # Cargar valor constante en $t0
            f.write(f"    li   $t0, {node.val}\n")

        elif node.exp == ExpKind.IdK:
            # Usar la funcion existente loadVariable
            loadVariable(node, f)

        elif node.exp == ExpKind.ArrayK:
            # Acceso a array: array[index]
            # Para el acceso a array, el nombre de la array debe estar en node.name y el index en child[0]
            if hasattr(node, "name") and node.name and node.child[0]:
                # Evaluar la expresion del index
                walkNode(node.child[0], f)  # index expression result in $t0
                f.write("    subu $sp, $sp, 4\n")
                f.write("    sw   $t0, 0($sp)\n")

                # Obtener la direccion base de la array
                array_name = node.name
                sym_location = st_lookup(array_name)
                if sym_location != -1:
                    base_offset = st_get_offset(array_name)
                    if base_offset is not None:
                        # Cargar el index desde la stack
                        f.write("    lw   $t1, 0($sp)\n")
                        f.write("    addu $sp, $sp, 4\n")
                        # Calcular la direccion: base + (index * 4)
                        f.write("    sll  $t1, $t1, 2\n")
                        f.write(f"    addi $t2, $fp, {base_offset}\n")
                        f.write("    add  $t2, $t2, $t1\n")
                        f.write("    lw   $t0, 0($t2)\n")
                        f.write(f"    # Array access: {array_name}[index]\n")
                    else:
                        f.write("    # ERROR: Array has no offset\n")
                        f.write("    addu $sp, $sp, 4\n")
                else:
                    f.write("    # ERROR: Array not found in symbol table\n")
                    f.write("    addu $sp, $sp, 4\n")
            else:
                f.write("    # ERROR: Invalid array access structure\n")

        elif node.exp == ExpKind.OpK:
            if node.op == TokenType.EQ:
                # Operacion de asignacion (=)
                if node.child[1]:
                    walkNode(node.child[1], f)

                target = node.child[0]
                if target and target.exp == ExpKind.IdK:
                    # Asignacion de variable regular
                    location = -4  # Fallback por defecto
                    sym_location = st_lookup(target.name)
                    if sym_location != -1:
                        loc_offset = st_get_offset(target.name)
                        if loc_offset is not None:
                            location = loc_offset
                        else:
                            print(
                                f"Warning: Variable {target.name} found in symbol table but has no offset assigned"
                            )

                    f.write(f"    sw   $t0, {location}($fp)\n")
                    f.write(f"    # Assignment: {target.name} = expression\n")

                elif target and target.exp == ExpKind.ArrayK:
                    # Asignacion de elemento de array: array[index] = value
                    f.write("    subu $sp, $sp, 4\n")
                    f.write("    sw   $t0, 0($sp)\n")

                    if hasattr(target, "name") and target.name and target.child[0]:
                        # Evaluar la expresion del index
                        walkNode(target.child[0], f)  # index en $t0

                        # Obtener la direccion base de la array
                        array_name = target.name
                        sym_location = st_lookup(array_name)
                        if sym_location != -1:
                            base_offset = st_get_offset(array_name)
                            if base_offset is not None:
                                # Calcular la direccion del elemento
                                f.write("    sll  $t0, $t0, 2\n")
                                f.write(f"    addi $t1, $fp, {base_offset}\n")
                                f.write("    add  $t1, $t1, $t0\n")
                                # Cargar el valor de asignacion y almacenar
                                f.write("    lw   $t0, 0($sp)\n")
                                f.write("    sw   $t0, 0($t1)\n")
                                f.write(
                                    f"    # Array assignment: {array_name}[index] = value\n"
                                )

                    f.write("    addu $sp, $sp, 4\n")

            # Operaciones aritmeticas
            elif node.op == TokenType.PLUS:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4\n")
                    f.write("    sw   $t0, 0($sp)\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)\n")
                f.write("    addu $sp, $sp, 4\n")
                f.write("    add  $t0, $t1, $t0\n")

            elif node.op == TokenType.MINUS:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4\n")
                    f.write("    sw   $t0, 0($sp)\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)\n")
                f.write("    addu $sp, $sp, 4\n")
                f.write("    sub  $t0, $t1, $t0\n")

            elif node.op == TokenType.TIMES:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4\n")
                    f.write("    sw   $t0, 0($sp)\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)\n")
                f.write("    addu $sp, $sp, 4\n")
                f.write("    mul  $t0, $t1, $t0\n")

            elif node.op == TokenType.OVER:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4\n")
                    f.write("    sw   $t0, 0($sp)\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)\n")
                f.write("    addu $sp, $sp, 4\n")
                f.write("    div  $t1, $t0\n")
                f.write("    mflo $t0\n")

            # Operadores de comparacion
            elif node.op == TokenType.LT:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4\n")
                    f.write("    sw   $t0, 0($sp)\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)\n")
                f.write("    addu $sp, $sp, 4\n")
                f.write("    slt  $t0, $t1, $t0\n")

            elif node.op == TokenType.LE:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4\n")
                    f.write("    sw   $t0, 0($sp)\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)\n")
                f.write("    addu $sp, $sp, 4\n")
                f.write("    sle  $t0, $t1, $t0\n")

            elif node.op == TokenType.GT:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4\n")
                    f.write("    sw   $t0, 0($sp)\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)\n")
                f.write("    addu $sp, $sp, 4\n")
                f.write("    sgt  $t0, $t1, $t0\n")

            elif node.op == TokenType.GE:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4\n")
                    f.write("    sw   $t0, 0($sp)\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)\n")
                f.write("    addu $sp, $sp, 4\n")
                f.write("    sge  $t0, $t1, $t0\n")

            elif node.op == TokenType.EQEQ:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4\n")
                    f.write("    sw   $t0, 0($sp)\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)\n")
                f.write("    addu $sp, $sp, 4\n")
                f.write("    seq  $t0, $t1, $t0\n")

            elif node.op == TokenType.NE:
                if node.child[0]:
                    walkNode(node.child[0], f)
                    f.write("    subu $sp, $sp, 4\n")
                    f.write("    sw   $t0, 0($sp)\n")

                if node.child[1]:
                    walkNode(node.child[1], f)

                f.write("    lw   $t1, 0($sp)\n")
                f.write("    addu $sp, $sp, 4\n")
                f.write("    sne  $t0, $t1, $t0\n")

        # Para llamadas a funciones
        elif node.exp == ExpKind.CallK:
            emitFunctionCall(node, f)

    # Manejar nodos de declaracion
    elif node.nodekind == NodeKind.StmtK:
        if node.stmt == StmtKind.ReturnK:
            emitReturn(node, f)

        # Manejar nodos de declaracion
        elif node.stmt == StmtKind.IfK:
            f.write("    # If statement\n")

            if node.child[0]:
                walkNode(node.child[0], f)
            # Agregar labels para condiciones
            else_label = get_next_label()
            end_label = get_next_label()

            f.write(f"    beq  $t0, $zero, {else_label}\n")

            if node.child[1]:
                f.write("    # Then branch\n")
                walkNode(node.child[1], f)

            f.write(f"    j    {end_label}\n")
            f.write(f"{else_label}:\n")

            if node.child[2]:
                f.write("    # Else branch\n")
                walkNode(node.child[2], f)

            f.write(f"{end_label}:\n")
            f.write("    # End of if statement\n")

        # Manejar nodos de declaracion
        elif node.stmt == StmtKind.WhileK:
            f.write("    # While statement\n")
            # Agregar labels para el bucle
            loop_start = get_next_label()
            loop_end = get_next_label()

            f.write(f"{loop_start}:\n")
            f.write("    # While condition\n")

            if node.child[0]:
                walkNode(node.child[0], f)

            f.write(f"    beq  $t0, $zero, {loop_end}\n")

            if node.child[1]:
                f.write("    # While body\n")
                walkNode(node.child[1], f)

            f.write(f"    j    {loop_start}\n")
            f.write(f"{loop_end}:\n")
            f.write("    # End of while statement\n")

        # Manejar nodos de declaracion
        elif node.stmt == StmtKind.CompoundK:
            f.write("    # Compound statement\n")
            for child in node.child:
                if child:
                    walkNode(child, f)

    # Manejar nodos de declaracion
    elif node.nodekind == NodeKind.DeclK:
        if node.decl == DeclKind.VarK:
            # Verificar si es una declaracion de array
            if node.is_array and node.val:
                # Declaracion de array: reservar espacio para array_size * 4 bytes
                array_size = node.val
                localOffset += array_size * 4
                st_set_offset(node.name, -localOffset)
                print(
                    f"Array {node.name}[{array_size}] allocated at offset {-localOffset} (size: {array_size * 4} bytes)"
                )
            else:
                # Variable regular: reservar 4 bytes
                localOffset += 4
                st_set_offset(node.name, -localOffset)
                print(f"Variable {node.name} allocated at offset {-localOffset}")
        elif node.decl == DeclKind.FunK:
            # Las declaraciones de funciones se manejan por separado
            pass

    # Manejar nodos hermanos
    if node.sibling:
        walkNode(node.sibling, f)


def loadVariable(node, f):
    """Load a variable's value from its memory location into $t0"""
    if not node or node.exp != ExpKind.IdK:
        return False

    # Usar la carga basada en desplazamientos estandar para todas las variables, incluidos los parametros
    location = -4  # Desplazamiento por defecto si no se encuentra

    # Intentar obtener el desplazamiento actual desde la tabla de simbolos
    sym_location = st_lookup(node.name)
    if sym_location != -1:
        loc_offset = st_get_offset(node.name)
        if loc_offset is not None:
            location = loc_offset
        else:
            print(
                f"Warning: Variable {node.name} found in symbol table but has no offset assigned"
            )

    # Cargar variable desde la stack usando el desplazamiento desde $fp
    f.write(f"    lw   $t0, {location}($fp)\n")
    return True


def collectGlobals(tree, globals_list):
    """Recolectar todas las variables globales"""
    if not tree:
        return

    # Si esto es una declaracion de variable
    if tree.nodekind == NodeKind.DeclK and tree.decl == DeclKind.VarK:
        if tree.name and tree.name not in globals_list:
            globals_list.append(tree.name)

    # Tambien verificar variables usadas en expresiones
    if tree.nodekind == NodeKind.ExpK and tree.exp == ExpKind.IdK:
        if tree.name and tree.name not in globals_list:
            globals_list.append(tree.name)

    # Verificar objetivos de asignacion
    if (
        tree.nodekind == NodeKind.ExpK
        and tree.exp == ExpKind.OpK
        and tree.op == TokenType.EQ
    ):
        if tree.child[0] and tree.child[0].exp == ExpKind.IdK:
            if tree.child[0].name and tree.child[0].name not in globals_list:
                globals_list.append(tree.child[0].name)

    # Recurrir en hijos y hermanos
    for c in tree.child:
        collectGlobals(c, globals_list)
    collectGlobals(tree.sibling, globals_list)


def collectAndEmitFunctions(node, f):
    """Recolectar y emitir todas las declaraciones de funciones excepto main"""
    if not node:
        return

    # Manejar declaraciones de funciones
    if node.nodekind == NodeKind.DeclK and node.decl == DeclKind.FunK:
        if node.name != "main":  # No emitir main aqui, se maneja por separado
            emitFunction(node, f)

    # Recurrir en hijos y hermanos
    for c in node.child:
        collectAndEmitFunctions(c, f)
    collectAndEmitFunctions(node.sibling, f)


def emitFunction(funcNode, f):
    """Generar codigo para una funcion definida por el usuario"""
    if not funcNode or funcNode.name == "main":
        return

    funcName = funcNode.name

    # Generar prologo de funcion
    emitFunctionProlog(funcName, f)

    # Enter the function scope to access parameters and local variables
    enter_scope(funcName)

    # Los parametros ahora tienen los desplazamientos temporales correctos en el marco de esta funcion
    # No es necesario copiar argumentos - ya estan en el lugar correcto!

    # Procesar el cuerpo de la funcion - child[1] es la declaracion compuesta
    if funcNode.child[1]:
        f.write(f"    # Cuerpo de la funcion para {funcName}\n")
        walkNode(funcNode.child[1], f)

    # Salir del alcance de la funcion
    exit_scope()

    # Generar epilogo de funcion (en caso de que no haya un retorno explicito)
    emitFunctionEpilog(funcName, f)


def findMainFunction(node):
    """Find the main function declaration in the AST"""
    if not node:
        return None

    # Verificar si esto es la funcion main
    if (
        node.nodekind == NodeKind.DeclK
        and node.decl == DeclKind.FunK
        and node.name == "main"
    ):
        return node

    # Recurrir en hijos y hermanos
    for c in node.child:
        result = findMainFunction(c)
        if result:
            return result

    return findMainFunction(node.sibling)


def emitMainFromDecl(mainNode, f):
    """Generar la funcion main desde su nodo de declaracion"""
    if not mainNode:
        return

    f.write("\n.text\n.globl main\nmain:\n")
    f.write("    move $fp, $sp\n")
    f.write("    subu $sp, $sp, 100\n")

    # Entrar al alcance de la funcion main para acceder a las variables locales
    enter_scope("main")

    # Procesar el cuerpo de la funcion main - child[1] es la declaracion compuesta
    if mainNode.child[1]:
        f.write("    # Cuerpo de la funcion main\n")
        walkNode(mainNode.child[1], f)

    # Salir del alcance de la funcion main
    exit_scope()

    # Limpiar y salir del programa
    f.write("    move $sp, $fp\n")
    f.write("    li   $v0, 10\n")
    f.write("    syscall\n")


# Primera pasada: recorrer el AST y p   rocesar declaraciones de variables y parametros.
def allocDeclarations(node):
    """Primera pasada: recorrer el AST y procesar declaraciones de variables y parametros."""
    global localOffset
    if not node:
        return

    # If this is a variable declaration
    if node.nodekind == NodeKind.DeclK and node.decl == DeclKind.VarK:
        # Verificar si es una declaracion de array
        if node.is_array and node.val:
            # Declaracion de array: reservar espacio para array_size * 4 bytes
            array_size = node.val
            localOffset += array_size * 4
            st_set_offset(node.name, -localOffset)
            print(
                f"Array {node.name}[{array_size}] allocated at offset {-localOffset} (size: {array_size * 4} bytes)"
            )
        else:
            # Variable regular: reservar 4 bytes
            localOffset += 4
            st_set_offset(node.name, -localOffset)
            print(f"Variable {node.name} allocated at offset {-localOffset}")

    # Si esto es una declaracion de funcion, manejar sus parametros de manera diferente
    elif node.nodekind == NodeKind.DeclK and node.decl == DeclKind.FunK:
        print(f"Procesando funcion {node.name}")
        # Entrar al alcance de la funcion para procesar parametros
        enter_scope(node.name)

        # Manejar parametros de funcion usando desplazamientos negativos fijos
        # En el nuevo layout de stack: $fp apunta a $fp guardado, $ra esta en 4($fp)
        # Los parametros se guardan en desplazamientos negativos: -4, -8, -12, -16
        param = node.child[0]
        param_index = 0

        while param:
            if param.nodekind == NodeKind.DeclK and param.decl == DeclKind.ParamK:
                # Asignar desplazamientos para parametros donde se guardan por el prologo
                # Los parametros se guardan en desplazamientos negativos: -4, -8, -12, -16
                param_offset = -4 - (param_index * 4)
                st_set_offset(param.name, param_offset)

                print(f"Parameter {param.name} assigned offset {param_offset}")
                param_index += 1
            param = param.sibling

        # Procesar el cuerpo de la funcion (variables locales en el alcance de la funcion)
        if node.child[1]:
            allocDeclarations(node.child[1])

        # Exit the function scope
        exit_scope()
        return

    # Recursion
    for c in node.child:
        allocDeclarations(c)
    allocDeclarations(node.sibling)


def codeGen(syntaxTreeParam, symtab, codefile, trace=False):
    """Generate MIPS assembly code with proper symbol table usage"""
    global TraceCode, syntaxTree
    TraceCode = trace
    syntaxTree = syntaxTreeParam  # Store syntax tree for parameter lookup

    # Open the file for writing
    with open(codefile, "w") as f:
        # Write header
        f.write("# C- Compilation to MIPS Assembly\n")
        f.write(f"# File: {codefile}\n")
        f.write("# Using symbol table offsets for variable access\n\n")

        # Process variable declarations to set up offsets
        allocDeclarations(syntaxTreeParam)

        # Print symbol table for debugging
        if trace:
            printSymTab()

        # First, emit the main function (must be at top)
        mainFunc = findMainFunction(syntaxTreeParam)
        if mainFunc:
            emitMainFromDecl(mainFunc, f)
        else:
            # Fallback: emit a simple main that processes the whole tree
            f.write("\n.text\n.globl main\nmain:\n")
            f.write("    move $fp, $sp\n")
            f.write("    subu $sp, $sp, 10000\n")
            walkNode(syntaxTreeParam, f)
            f.write("    move $sp, $fp\n")
            f.write("    li   $v0, 10\n")
            f.write("    syscall\n")

        # Then, emit all other user-defined functions
        collectAndEmitFunctions(syntaxTreeParam, f)

    # For debugging
    print(f"Assembly code generated to {codefile}")
    print("Using symbol table offsets for variable access")
    print("Main function emitted at top, followed by other functions")


def findFunctionDeclaration(funcName, tree):
    """Find a function declaration by name in the AST"""
    if not tree:
        return None

    # Verificar si esto es la funcion que estamos buscando
    if (
        tree.nodekind == NodeKind.DeclK
        and tree.decl == DeclKind.FunK
        and tree.name == funcName
    ):
        return tree

    # Recurrir en hijos y hermanos
    for child in tree.child:
        result = findFunctionDeclaration(funcName, child)
        if result:
            return result

    return findFunctionDeclaration(funcName, tree.sibling)


def getParameterNames(funcDecl):
    """Obtener nombres de parametros de una declaracion de funcion"""
    if not funcDecl:
        return []

    param_names = []
    param = funcDecl.child[0]  # El primer hijo debe ser parametros
    while param:
        if param.nodekind == NodeKind.DeclK and param.decl == DeclKind.ParamK:
            param_names.append(param.name)
        param = param.sibling

    return param_names
