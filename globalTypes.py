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


### Sintaxis de los nodos
class NodeKind(Enum):
    StmtK = 0
    ExpK = 1
    DeclK = 2


# Tipos de declaraciones
class DeclKind(Enum):
    VarK = 0
    FunK = 1
    ParamK = 2
    ParamArrayK = 3


# Tipos de datos
class ExpType(Enum):
    Void = 0
    Integer = 1


# Tipos de sentencias
class StmtKind(Enum):
    IfK = 0
    AssignK = 1
    ReturnK = 2
    CompoundK = 3
    WhileK = 4


# Tipos de expresiones
class ExpKind(Enum):
    OpK = 0
    ConstK = 1
    IdK = 2
    CallK = 3


# Máximo número de hijos por nodo
MAXCHILDREN = 3


# Nodo de árbol
class TreeNode:
    def __init__(self):
        self.child = [None] * MAXCHILDREN
        self.sibling = None
        self.lineno = 0
        self.nodekind = None
        self.stmt = None
        self.exp = None
        self.decl = None
        self.op = None
        self.val = None
        self.name = None
        self.type = None
        self.is_array = False
