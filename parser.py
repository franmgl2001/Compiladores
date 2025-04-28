from globalTypes import *
from lexer import *

token = None  # holds current token
tokenString = None  # holds the token string value
Error = False
# lineno = 1
SintaxTree = None
imprimeScanner = False


def syntaxError(message):
    global Error
    print(">>> Syntax error at line " + str(lineno) + ": " + message, end="")
    Error = True


def match(expected):
    global token, tokenString, lineno
    if token == expected:
        token, tokenString, lineno = getToken(imprimeScanner)
        # print("TOKEN:", token, lineno)
    else:
        syntaxError("unexpected token -> ")
        printToken(token, tokenString)
        print("      ")


def parse_operation_exp():
    t = parse_term()
    while token in {TokenType.PLUS, TokenType.MINUS}:
        op_tok = token
        match(token)
        right = parse_term()
        p = newExpNode(ExpKind.OpK)
        p.op = op_tok
        p.child[0] = t
        p.child[1] = right
        t = p
    return t


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


def parse_simple_expression():
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


def parse_factor():
    if token == TokenType.ID:
        name = tokenString
        match(TokenType.ID)
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
        t = parse_operation_exp()
        match(TokenType.RPAREN)
        return t
    else:
        print("Factor error")
        syntaxError("unexpected token -> ")


def stmt_sequence():
    print("stmt_sequence")
    t = statement()
    p = t
    while (
        (token != TokenType.ENDFILE)
        and (token != TokenType.ELSE)
        and (token != TokenType.RBRACE)
    ):
        print("stmt_sequence while", token)
        match(TokenType.SEMI)
        q = statement()
        if q != None:
            if t == None:
                t = p = q
            else:  # now p cannot be NULL either
                p.sibling = q
                p = q
    return t


def parse_if_stmt():
    match(TokenType.IF)
    t = newStmtNode(StmtKind.IfK)
    t.child[0] = parse_simple_expression()
    match(TokenType.LBRACE)
    t.child[1] = stmt_sequence()
    match(TokenType.RBRACE)
    return t


def parse_while_stmt():
    match(TokenType.WHILE)
    t = newStmtNode(StmtKind.WhileK)
    t.child[0] = parse_simple_expression()
    match(TokenType.LBRACE)
    t.child[1] = stmt_sequence()
    match(TokenType.RBRACE)
    return t


def parse_return_stmt():
    t = newStmtNode(StmtKind.ReturnK)
    match(TokenType.RETURN)
    t.child[0] = parse_simple_expression()
    return t


def parse_compound_stmt():
    t = newStmtNode(StmtKind.CompoundK)
    match(TokenType.LBRACE)
    t.child[0] = stmt_sequence()
    match(TokenType.RBRACE)
    return t


def statement():
    global token, tokenString, lineno
    # print("STATEMENT: ", token, lineno)
    t = None
    if token == TokenType.IF:
        t = parse_if_stmt()
    elif token == TokenType.RETURN:
        t = parse_return_stmt()
    elif token == TokenType.LBRACE:
        t = parse_compound_stmt()
    elif token == TokenType.WHILE:
        t = parse_while_stmt()
    else:
        syntaxError("unexpected token -> ")
        printToken(token, tokenString)
        token, tokenString, lineno = getToken()
    return t


def newStmtNode(kind):
    t = TreeNode()
    if t == None:
        print("Out of memory error at line " + lineno)
    else:
        # for i in range(MAXCHILDREN):
        #    t.child[i] = None
        # t.sibling = None
        t.nodekind = NodeKind.StmtK
        t.stmt = kind
        t.lineno = lineno
    return t


def newExpNode(kind):
    t = TreeNode()
    if t == None:
        print("Out of memory error at line " + lineno)
    else:
        # for i in range(MAXCHILDREN):
        #    t.child[i] = None
        # t.sibling = None
        t.nodekind = NodeKind.ExpK
        t.exp = kind
        t.lineno = lineno
        t.type = ExpType.Void
    return t


# Procedure printToken prints a token
# and its lexeme to the listing file
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


def printTree(tree):
    global indentno
    indentno += 2  # INDENT
    while tree != None:
        printSpaces()
        if tree.nodekind == NodeKind.StmtK:
            if tree.stmt == StmtKind.IfK:
                print(tree.lineno, "If")
            elif tree.stmt == StmtKind.ReturnK:
                print(tree.lineno, "Return")
            elif tree.stmt == StmtKind.WhileK:
                print(tree.lineno, "While")
            elif tree.stmt == StmtKind.CompoundK:
                print(tree.lineno, "Compound")
            else:
                print(tree.lineno, "Unknown ExpNode kind")
        elif tree.nodekind == NodeKind.ExpK:
            if tree.exp == ExpKind.OpK:
                print(tree.lineno, "Op: ", end="")
                printToken(tree.op, " ")
            elif tree.exp == ExpKind.ConstK:
                print(tree.lineno, "Const: ", tree.val)
            elif tree.exp == ExpKind.IdK:
                print(tree.lineno, "Id: ", tree.name)
            else:
                print(tree.lineno, "Unknown ExpNode kind")
        else:
            print(tree.lineno, "Unknown node kind")
        for i in range(MAXCHILDREN):
            printTree(tree.child[i])
        tree = tree.sibling
    indentno -= 2  # UNINDENT


# Variable indentno is used by printTree to
# store current number of spaces to indent
indentno = 0


# printSpaces indents by printing spaces */
def printSpaces():
    print(" " * indentno, end="")


def parser(imprime=True):
    global token, tokenString, lineno
    token, tokenString, lineno = getToken(imprimeScanner)
    t = stmt_sequence()
    if token != TokenType.ENDFILE:
        syntaxError("Code ends before file\n")
    if imprime:
        printTree(t)
    return t, Error
