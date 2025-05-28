from globalTypes import *
from parser import *
from lexer import *
from parser import *
from analyze import *
from symtab import BucketList, scopes, scope_names
from cgen import *


source_file = "test_files/sample2.c-"
f = open(source_file, "r")
programa = f.read()  # lee todo el archivo a compilar
progLong = len(programa)  # longitud original del programa
programa = programa + "$"  # agregar un caracter $ que represente EOF
posicion = 0  # posición del caracter actual del string
# función para pasar los valores iniciales de las variables globales
globales(programa, posicion, progLong)
AST, Error = parser(True)
if not Error:
    load_code(source_file)
    print("AST:")

    buildSymtab(AST, True)
    typeCheck(AST)
    # Access to symbol table
    symtab = {"current": BucketList, "scopes": scopes, "scope_names": scope_names}

    codeGen(AST, symtab, "output.tm", True)
