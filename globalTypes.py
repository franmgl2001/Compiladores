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


class ExpKind(Enum):
    OpK = 0
    ConstK = 1
    IdK = 2


# Tipos de datos
class ExpType(Enum):
    Void = 0
    Integer = 1
    Boolean = 2


class StmtKind(Enum):
    IfK = 0
    AssignK = 1
    ReturnK = 2
    CompoundK = 3
    WhileK = 4


class ExpKind(Enum):
    OpK = 0
    ConstK = 1
    IdK = 2


# Máximo número de hijos por nodo (3 para el if)
MAXCHILDREN = 3


class TreeNode:
    def __init__(self):
        # MAXCHILDREN = 3 está en globalTypes
        self.child = [None] * MAXCHILDREN  # tipo treeNode
        self.sibling = None  # tipo treeNode
        self.lineno = 0  # tipo int
        self.nodekind = None  # tipo NodeKind, en globalTypes
        # en realidad los dos siguientes deberían ser uno solo (kind)
        # siendo la  union { StmtKind stmt; ExpKind exp;}
        self.stmt = None  # tipo StmtKind
        self.exp = None  # tipo ExpKind
        # en realidad los tres siguientes deberían ser uno solo (attr)
        # siendo la  union { TokenType op; int val; char * name;}
        self.op = None  # tipo TokenType
        self.val = None  # tipo int
        self.name = None  # tipo String
        # for type checking of exps
        self.type = None  # de tipo ExpType
