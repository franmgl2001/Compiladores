from enum import Enum


# Tipos de tokens
class TokenType(Enum):
    ENDFILE = 1
    ERROR = 2
    # Palabras reservadas
    IF = "if"
    ELSE = "else"
    INT = "int"
    RETURN = "return"
    VOID = "void"
    WHILE = "while"
    # Tokens de varios caracteres
    ID = 3
    NUM = 4
    # Caracteres especiales
    PLUS = "+"
    MINUS = "-"
    TIMES = "*"
    OVER = "/"
    EQ = "="
    EQEQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    SEMI = ";"
    COMMA = ","
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"


# Tipos de estados
class StateType(Enum):
    START = 0
    INASSIGN = 1
    INCOMMENT = 2
    INNUM = 3
    INID = 4
    DONE = 5


# Palabras reservadas
class ReservedWords(Enum):
    IF = "if"
    ELSE = "else"
    INT = "int"
    RETURN = "return"
    VOID = "void"
    WHILE = "while"
