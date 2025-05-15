from globalTypes import *
import lexer
from lexer import *

token = None  # holds current token
tokenString = None  # holds the token string value
Error = False
# lineno = 1
SintaxTree = None
imprimeScanner = True


# Function que imprime el error de sintaxis
def syntaxError(message):

    global Error, token, tokenString, lineno
    # primero, invocamos la función de error del lexer:
    #   lexer.error(mensaje, linea, columna, programa)
    lexer.error(message, lexer.linea, lexer.columna, lexer.programa)

    Error = True

    sync = {
        TokenType.SEMI,
        TokenType.RBRACE,
        TokenType.ELSE,
        TokenType.RETURN,
        TokenType.ENDFILE,
    }
    while token not in sync:
        token, tokenString, lineno = getToken(imprimeScanner)
    if token == TokenType.SEMI:
        token, tokenString, lineno = getToken(imprimeScanner)


# Function que verifica si el token es el esperado
def match(expected):
    global token, tokenString, lineno
    if token == expected:
        token, tokenString, lineno = getToken(imprimeScanner)
    else:
        syntaxError("unexpected token -> ")
        printToken(token, tokenString)
        print("      ")


### Declarations ###


# Function que parsea el tipo de dato
def parse_type():
    if token == TokenType.INT:
        match(TokenType.INT)
        return ExpType.Integer
    elif token == TokenType.VOID:
        match(TokenType.VOID)
        return ExpType.Void
    else:
        syntaxError("unexpected token -> ")


# Function que parsea los parametros
def parse_params():
    if token == TokenType.VOID:
        match(TokenType.VOID)
        return None
    else:
        return parse_param_list()


# Function que parsea la lista de parametros
def parse_param_list():
    head = parse_param()
    p = head
    # En caso de que el parametro sea un array
    while token == TokenType.COMMA:
        match(TokenType.COMMA)
        q = parse_param()
        p.sibling = q
        p = q
    return head


# Function que parsea un parametro
def parse_param():
    typ = parse_type()
    if token != TokenType.ID:
        syntaxError("expected identifier in parameter")
        printToken(token, tokenString)
        return None
    name = tokenString
    match(TokenType.ID)
    node = newDeclNode(DeclKind.ParamK, name)
    node.type = typ
    # En caso de que el parametro sea un array
    if token == TokenType.LBRACKET:
        match(TokenType.LBRACKET)
        match(TokenType.RBRACKET)
        node.decl = DeclKind.ParamArrayK
    return node


# Function que parsea la declaracion de una funcion
def parse_fun_declaration(name, rettype):
    # we've eaten type, ID, and seen '('
    node = newDeclNode(DeclKind.FunK, name)
    node.type = rettype
    match(TokenType.LPAREN)
    # Parsea los parametros de la funcion
    node.child[0] = parse_params()
    match(TokenType.RPAREN)
    # Parsea el cuerpo de la funcion
    node.child[1] = parse_compound_stmt()
    return node


# Function que parsea la declaracion de una variable
def parse_var_declaration(name, rettype):
    node = newDeclNode(DeclKind.VarK, name)
    node.type = rettype
    # En caso de que el tipo de dato sea un array
    if token == TokenType.LBRACKET:
        match(TokenType.LBRACKET)
        if token == TokenType.NUM:
            node.val = int(tokenString)  # store array size in .val
            match(TokenType.NUM)
        match(TokenType.RBRACKET)
    match(TokenType.SEMI)
    return node


# Function que parsea la declaracion de una variable
def parse_declaration():
    # Parsea el tipo de dato
    rettype = parse_type()
    # En caso de que el token no sea un identificador
    if token != TokenType.ID:
        syntaxError("expected identifier in declaration")
        printToken(token, tokenString)
        return None
    name = tokenString
    match(TokenType.ID)
    # En caso de que el token sea un parentesis
    if token == TokenType.LPAREN:
        # Pasar a la funcion que parsea la declaracion de una funcion
        return parse_fun_declaration(name, rettype)
    # En caso de que el token no sea un parentesis
    else:
        # Pasar a la funcion que parsea la declaracion de una variable
        return parse_var_declaration(name, rettype)


### Expressions ###


# Function que parsea la expresion de una operacion
def parse_operation_exp():
    t = parse_term()
    while token in {TokenType.PLUS, TokenType.MINUS}:
        op_tok = token
        op_line = lineno  # ← grab it right now
        match(token)
        right = parse_term()
        p = newExpNode(ExpKind.OpK)
        p.lineno = op_line  # ← overwrite with the real line
        p.op = op_tok
        p.child[0] = t
        p.child[1] = right
        t = p
    return t


# Function que parsea el termino de una expresion
def parse_term():
    t = parse_factor()
    while token in {TokenType.TIMES, TokenType.OVER}:
        op_tok = token
        match(token)
        right = parse_factor()
        p = newExpNode(ExpKind.OpK)
        p.op = op_tok
        p.child[0] = t
        p.child[1] = right
        t = p
    return t


# Function que parsea la expresion y la asignacion
def parse_expression_and_assignment():
    global token, tokenString, lineno
    # En caso de que el token sea un identificador
    if token == TokenType.ID:
        name = tokenString
        saved_token, saved_string, saved_lineno = token, tokenString, lineno
        match(TokenType.ID)
        # En caso de que el token sea un igual
        if token == TokenType.EQ:
            match(TokenType.EQ)
            rhs = parse_expression()
            p = newExpNode(ExpKind.OpK)
            p.op = TokenType.EQ
            left = newExpNode(ExpKind.IdK)
            left.name = name
            p.child[0] = left
            p.child[1] = rhs
            # Consume the semicolon
            match(TokenType.SEMI)
            return p
        elif token == TokenType.LPAREN:
            # we've already eaten the ID; parse the parens & args
            call_node = parse_function_call(name)
            match(TokenType.SEMI)
            return call_node
        else:
            token, tokenString, lineno = saved_token, saved_string, saved_lineno

    result = parse_expression()
    # En caso de que el token no sea un punto y coma, parentesis, corchete o llave
    if token not in {
        TokenType.SEMI,
        TokenType.RPAREN,
        TokenType.RBRACKET,
        TokenType.RBRACE,
    }:
        syntaxError("expected expression")
        printToken(token, tokenString)
        return None
    # Consume the semicolon if this is an expression statement
    if token == TokenType.SEMI:
        match(TokenType.SEMI)
    return result


# Function que parsea la expresion
def parse_expression():
    """
    simple‐expression → additive‐expr { relop additive‐expr }
    where relop is one of <, <=, >, >=, ==, !=
    """
    t = parse_operation_exp()
    while token in {
        TokenType.LT,
        TokenType.LE,
        TokenType.GT,
        TokenType.GE,
        TokenType.EQEQ,
        TokenType.NE,
    }:
        op_tok = token
        match(op_tok)
        right = parse_operation_exp()
        p = newExpNode(ExpKind.OpK)
        p.op = op_tok
        p.child[0] = t
        p.child[1] = right
        t = p
    return t


# Function que parsea la llamada a una funcion
def parse_function_call(callee_name):
    """
    Parses a function call starting after the callee identifier.
    Expects that '(' has not yet been consumed.
    Returns an ExpK.CallK node.
    """
    global token, tokenString, lineno
    # consume '('
    match(TokenType.LPAREN)
    call_line = lineno  # ← grab the line of the "print" name
    args = []
    if token != TokenType.RPAREN:
        args.append(parse_expression())
        while token == TokenType.COMMA:
            match(TokenType.COMMA)
            args.append(parse_expression())
    match(TokenType.RPAREN)
    # build call node
    call_node = newExpNode(ExpKind.CallK)
    call_node.lineno = call_line  # ← stamp it correctly
    call_node.name = callee_name
    # attach arguments as child nodes
    for idx, arg in enumerate(args):
        call_node.child[idx] = arg
    return call_node


# Function que parsea el factor de una expresion
def parse_factor():
    global token, tokenString, lineno
    # En caso de que el token sea un identificador
    if token == TokenType.ID:
        name = tokenString
        match(TokenType.ID)
        if token == TokenType.LPAREN:
            return parse_function_call(name)
        t = newExpNode(ExpKind.IdK)
        t.name = name
        return t
    elif token == TokenType.NUM:
        val = int(tokenString)
        match(TokenType.NUM)
        t = newExpNode(ExpKind.ConstK)
        t.val = val
        return t
    elif token == TokenType.LPAREN:
        match(TokenType.LPAREN)
        t = parse_expression()
        match(TokenType.RPAREN)
        return t
    else:
        syntaxError("unexpected token -> ")
        printToken(token, tokenString)  # show the culprit
        token, tokenString, lineno = getToken(imprimeScanner)
        # skip it so parse_term can't reuse it
        return None


# Function que parsea la secuencia de sentencias
def stmt_sequence():
    t = statement()
    p = t
    while (
        (token != TokenType.ENDFILE)
        and (token != TokenType.ELSE)
        and (token != TokenType.RBRACE)
    ):
        q = statement()
        if q != None:
            if t == None:
                t = p = q
            else:
                p.sibling = q
                p = q
    return t


### Statements ###


# Function que parsea la sentencia if
def parse_if_stmt():
    match(TokenType.IF)
    match(TokenType.LPAREN)
    t = newStmtNode(StmtKind.IfK)
    t.child[0] = parse_expression()  # just the condition
    match(TokenType.RPAREN)
    t.child[1] = parse_compound_stmt()  # require a { … } then-branch
    if token == TokenType.ELSE:
        match(TokenType.ELSE)
        t.child[2] = parse_compound_stmt()  # likewise for else
    return t


def parse_while_stmt():
    match(TokenType.WHILE)
    t = newStmtNode(StmtKind.WhileK)
    t.child[0] = parse_expression_and_assignment()
    match(TokenType.LBRACE)
    t.child[1] = stmt_sequence()
    match(TokenType.RBRACE)
    return t


# Function que parsea la sentencia return
def parse_return_stmt():
    t = newStmtNode(StmtKind.ReturnK)
    match(TokenType.RETURN)
    # En caso de que el token no sea un punto y coma
    if token != TokenType.SEMI:
        t.child[0] = parse_expression()
    match(TokenType.SEMI)
    return t


# Function que parsea la sentencia compuesta
def parse_compound_stmt():
    t = newStmtNode(StmtKind.CompoundK)
    match(TokenType.LBRACE)
    t.child[0] = stmt_sequence()
    match(TokenType.RBRACE)
    return t


# Function que parsea la sentencia
def statement():
    global token, tokenString, lineno
    # En caso de que el token sea un entero o void
    t = None
    if token == TokenType.INT or token == TokenType.VOID:
        t = parse_declaration()
    elif token == TokenType.ID:
        t = parse_expression_and_assignment()
    elif token == TokenType.LBRACE:
        t = parse_compound_stmt()
    elif token == TokenType.IF:
        t = parse_if_stmt()
    elif token == TokenType.SEMI:
        match(TokenType.SEMI)
        return None
    # Iteration
    elif token == TokenType.WHILE:
        t = parse_while_stmt()
    elif token == TokenType.RETURN:
        t = parse_return_stmt()
    else:
        syntaxError("unexpected token -> ")
        printToken(token, tokenString)
        token, tokenString, lineno = getToken()
    return t


# Function que crea un nodo de sentencia
def newStmtNode(kind):
    t = TreeNode()
    if t == None:
        print("Out of memory error at line " + lineno)
    else:
        t.nodekind = NodeKind.StmtK
        t.stmt = kind
        t.lineno = lineno
    return t


# Function que crea un nodo de expresion
def newExpNode(kind):
    t = TreeNode()
    if t == None:
        print("Out of memory error at line " + lineno)
    else:
        t.nodekind = NodeKind.ExpK
        t.exp = kind
        t.lineno = lineno
        t.type = ExpType.Integer
    return t


# Function que crea un nodo de declaracion
def newDeclNode(decl_type, name):
    t = TreeNode()
    if t == None:
        print("Out of memory error at line " + lineno)
    else:
        t.nodekind = NodeKind.DeclK
        t.decl = decl_type
        t.name = name
        t.lineno = lineno
    return t


# Procedure printToken prints a token
def printToken(token, tokenString):
    """
    Imprime en pantalla el token y, cuando procede, su lexema.
    """
    # Conjunto de palabras reservadas
    reserved = {
        TokenType.IF,
        TokenType.ELSE,
        TokenType.INT,
        TokenType.RETURN,
        TokenType.VOID,
        TokenType.WHILE,
    }

    # 1) Palabras reservadas
    if token in reserved:
        print(f"reserved word: {tokenString}")

    # 2) Operadores de dos caracteres
    elif token in {TokenType.EQEQ, TokenType.NE, TokenType.LE, TokenType.GE}:
        print(token.value)  # '==', '!=', '<=', '>='

    # 3) Operadores y delimitadores de un carácter
    elif token in {
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.TIMES,
        TokenType.OVER,
        TokenType.LT,
        TokenType.GT,
        TokenType.EQ,
        TokenType.SEMI,
        TokenType.COMMA,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.LBRACKET,
        TokenType.RBRACKET,
    }:
        print(
            token.value
        )  # '+', '-', '*', '/', '<', '>', '=', ';', ',', '(', ')', '{', '}', '[', ']'

    # 4) Número
    elif token == TokenType.NUM:
        print(f"NUM, val= {tokenString}")

    # 5) Identificador
    elif token == TokenType.ID:
        print(f"ID, name= {tokenString}")

    # 6) Fin de archivo
    elif token == TokenType.ENDFILE:
        print("EOF")

    # 7) Error léxico
    elif token == TokenType.ERROR:
        print(f"ERROR: {tokenString}")

    # 8) Por si acaso aparece algo inesperado
    else:
        print(f"Unknown token: {token}")


# Function que imprime el arbol de sintaxis
def printTree(tree):
    global indentno
    indentno += 2  # INDENT
    while tree != None:
        printSpaces()
        if tree.nodekind == NodeKind.StmtK:
            if tree.stmt == StmtKind.IfK:
                print(tree.lineno, "If", tree.type, tree.nodekind, tree.stmt)
            elif tree.stmt == StmtKind.ReturnK:
                print(tree.lineno, "Return", tree.type)
            elif tree.stmt == StmtKind.WhileK:
                print(tree.lineno, "While", tree.type)
            elif tree.stmt == StmtKind.CompoundK:
                print(tree.lineno, "Compound", tree.type)
            elif tree.stmt == StmtKind.AssignK:
                print(tree.lineno, "Assign", tree.type)
            elif tree.stmt == StmtKind.ForK:
                print(tree.lineno, "For", tree.type)
            elif tree.stmt == StmtKind.ExpressionK:
                print(tree.lineno, "Expression", tree.type)
            else:
                print(tree.lineno, "Unknown StmtNode kind")
        elif tree.nodekind == NodeKind.ExpK:
            if tree.exp == ExpKind.OpK:
                print(
                    tree.lineno,
                    "Op: ",
                    end="",
                )
                printToken(tree.op, " ")
            elif tree.exp == ExpKind.ConstK:
                print(tree.lineno, "Const: ", tree.val, tree.type)
            elif tree.exp == ExpKind.IdK:
                print(tree.lineno, "Id: ", tree.name, tree.type)
            elif tree.exp == ExpKind.CallK:
                print(tree.lineno, "Call: ", tree.name, tree.type)
            elif tree.exp == ExpKind.ArrayK:
                print(tree.lineno, "Array: ", tree.name, tree.type)
            elif tree.exp == ExpKind.AssignK:
                print(tree.lineno, "Assign: ", tree.name, tree.type)
            else:
                print(tree.lineno, "Unknown ExpNode kind")
        elif tree.nodekind == NodeKind.DeclK:
            if tree.decl == DeclKind.VarK:
                print(
                    tree.lineno, "Var dec: ", "Type: ", tree.type, ", Name: ", tree.name
                )
            elif tree.decl == DeclKind.FunK:
                print(
                    tree.lineno, "Fun dec: ", "Type: ", tree.type, ", Name: ", tree.name
                )
            elif tree.decl == DeclKind.ParamK:
                print(tree.lineno, "Param: ", tree.name)
            elif tree.decl == DeclKind.ParamArrayK:
                print(tree.lineno, "Param Array: ", tree.name)
            elif tree.decl == DeclKind.ArrayK:
                print(
                    tree.lineno,
                    "Array dec: ",
                    "Type: ",
                    tree.type,
                    ", Name: ",
                    tree.name,
                )
            else:
                print(tree.lineno, "Unknown DeclNode kind")
        else:
            print(tree.lineno, "Unknown node kind")
        for i in range(MAXCHILDREN):
            if (
                tree.nodekind == NodeKind.StmtK
                and tree.stmt == StmtKind.IfK
                and i == 2
                and tree.child[2] is not None
            ):
                printSpaces()
                print(tree.child[2].lineno, "Else")
            printTree(tree.child[i])
        tree = tree.sibling
    indentno -= 2  #


# Variable indentno es usada por printTree para almacenar el numero actual de espacios para indentar
indentno = 0


# printSpaces imprime espacios para indentar
def printSpaces():
    print(" " * indentno, end="")


# Function main del parser
def parser(imprime=True):
    global token, tokenString, lineno
    token, tokenString, lineno = getToken(imprimeScanner)

    t = stmt_sequence()
    if token != TokenType.ENDFILE:
        syntaxError("Code ends before file\n")
    if imprime:
        printTree(t)
    return t, Error
