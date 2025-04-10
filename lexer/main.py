from globalTypes import *
from lexer import *

# Leer archivo y preprocesar
f = open("sample2.c-", "r")
programa = f.read()
progLong = len(programa)
posicion = 0
globales(programa, posicion, progLong)

# Obtener tokens

token, tokenString = getToken(True)
while token != TokenType.ENDFILE:
    token, tokenString = getToken(True)
