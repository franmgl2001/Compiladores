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
