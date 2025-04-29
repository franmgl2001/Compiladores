from globalTypes import *
from parser import *
from lexer import *


f = open("test_files/sample2.c-", "r")
programa = f.read()  # lee todo el archivo a compilar
progLong = len(programa)  # longitud original del programa
programa = programa + "$"  # agregar un caracter $ que represente EOF
posicion = 0  # posición del caracter actual del string
# función para pasar los valores iniciales de las variables globales
globales(programa, posicion, progLong)
print(programa)
AST = parser(True)
