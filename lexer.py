from globalTypes import *


def globales(prog, pos, long):
    """
    Funcion que inicializa las variables globales
    """
    global programa
    global posicion
    global progLong
    global linea
    global columna
    programa = prog + "$"
    posicion = pos
    progLong = long
    linea = 1
    columna = 0


def reservedLookup(tokenString):
    """
    Funcion que verifica si el tokenString es una palabra reservada
    """
    for w in ReservedWords:
        if tokenString == w.value:
            return TokenType(tokenString)
    return TokenType.ID


def print_line(linea, programa):
    """
    Funcion que imprime la linea del programa
    """
    lines = programa.splitlines()
    print(lines[linea - 1])


def error(mensaje, linea, columna, programa):
    """
    Function que imprime el error en la linea y columna
    """
    print("Linea ", str(linea) + ":", mensaje + ":")
    print_line(linea, programa)
    print(" " * columna + "^")


def check_error_double_char(posicion, programa, except_char=None):
    """
    Funcion que verifica si el character esta en una posicion valida
    """
    if posicion + 1 < progLong and programa[posicion + 1] in (
        [
            "+",
            "-",
            "*",
            "/",
            "=",
            "!",
            "<",
            ">",
            ",",
            "(",
            ")",
            "{",
            "}",
            "[",
            "]",
        ]  # Se uso gpt para generar la lista
    ):
        if except_char and programa[posicion + 1] == except_char:
            return False
        return True
    return False


def getToken(imprime=False):
    """
    Funcion que obtiene el siguiente token del programa
    """
    global programa
    global posicion
    global progLong
    global linea
    global columna
    lexema = ""
    state = StateType.START  # Estado inicial

    # Inicio del ciclo que busca token
    while state != StateType.DONE:
        # Si se llega al final del programa Regresa ENDFILE
        if posicion >= progLong:
            currentToken = TokenType.ENDFILE
            state = StateType.DONE
            break

        # Si el caracter es un espacio o tabulacion, no se guarda
        save = True
        char = programa[posicion]

        # Codigo para comentar una linea.Se uso ayuda de gpt para generar el codigo
        if char == "/" and posicion + 1 < progLong and programa[posicion + 1] == "/":
            posicion += 2
            while posicion < progLong and programa[posicion] != "\n":
                posicion += 1
                columna = 0
            continue

        # # Codigo para comentar muchas linea. Se uso ayuda de gpt para generar el codigo
        if char == "/" and posicion + 1 < progLong and programa[posicion + 1] == "*":
            posicion += 2
            while posicion + 1 < progLong and not (
                programa[posicion] == "*" and programa[posicion + 1] == "/"
            ):
                posicion += 1
                if programa[posicion] == "\n":
                    linea += 1
                    columna = 0
            if posicion + 1 < progLong:
                posicion += 2
            else:
                while posicion < progLong:
                    posicion += 1
            continue

        # Si es inicio se checa que tipo de token se esta buscando
        if state == StateType.START:
            # Si es el fin del programa Regresa ENDFILE
            if char == "$":
                state = StateType.DONE
                currentToken = TokenType.ENDFILE
            # Si es un numero se busca el siguiente numero
            elif char.isdigit():
                state = StateType.INNUM
            # Si es un identificador se busca el siguiente identificador
            elif char.isalpha():
                state = StateType.INID
            # Si es un salto de linea no se guarda, pero se aumenta la linea y se reinicia la columna
            elif char == "\n":
                linea += 1
                columna = 0
                save = False
                posicion += 1
                continue
            # Si es un espacio o tabulacion, no se guarda
            elif char in " \t":
                columna += 1
                save = False
                posicion += 1
                continue
            # Si es un caracter especial se busca el siguiente caracter especial
            else:
                # Todas las condiciones continen el estado DONE y una funcion para checar errores de caracteres dobles
                state = StateType.DONE
                # Si es un +
                if char == "+":
                    currentToken = TokenType.PLUS
                    if check_error_double_char(posicion, programa):
                        currentToken = TokenType.ERROR
                        save = False
                        error(
                            "Error en la formación de un operador",
                            linea,
                            columna,
                            programa,
                        )
                        posicion += 1
                        continue
                    # Si es un -
                elif char == "-":
                    currentToken = TokenType.MINUS
                    if check_error_double_char(posicion, programa):
                        currentToken = TokenType.ERROR
                        save = False
                        error(
                            "Error en la formación de un operador",
                            linea,
                            columna,
                            programa,
                        )
                        posicion += 1
                        continue
                # Si es un *
                elif char == "*":
                    currentToken = TokenType.TIMES
                    if check_error_double_char(posicion, programa):
                        currentToken = TokenType.ERROR
                        save = False
                        error(
                            "Error en la formación de un operador",
                            linea,
                            columna,
                            programa,
                        )
                        posicion += 1
                        continue
                # Si es un /
                elif char == "/":
                    currentToken = TokenType.OVER
                    if check_error_double_char(posicion, programa):
                        currentToken = TokenType.ERROR
                        save = False
                        error(
                            "Error en la formación de un operador",
                            linea,
                            columna,
                            programa,
                        )
                        posicion += 1
                        continue
                # Si es un =
                elif char == "=":
                    # Si es un ==
                    if posicion + 1 < progLong and programa[posicion + 1] == "=":
                        lexema = "=="
                        posicion += 1
                        save = False
                        currentToken = TokenType.EQEQ
                        if check_error_double_char(posicion, programa):
                            currentToken = TokenType.ERROR
                            save = False
                            error(
                                "Error en la formación de un operador",
                                linea,
                                columna,
                                programa,
                            )
                            posicion += 1
                            continue
                    else:
                        currentToken = TokenType.EQ
                # Si es un !
                elif char == "!":
                    # Si es un !=
                    if posicion + 1 < progLong and programa[posicion + 1] == "=":
                        lexema = "!="
                        posicion += 1
                        save = False
                        currentToken = TokenType.NE
                    else:
                        if check_error_double_char(posicion, programa):
                            currentToken = TokenType.ERROR
                            save = False
                            error(
                                "Error en la formación de un operador",
                                linea,
                                columna,
                                programa,
                            )
                            posicion += 1
                            continue
                # Si es un <
                elif char == "<":
                    # Si es un <=
                    if posicion + 1 < progLong and programa[posicion + 1] == "=":
                        lexema = "<="
                        posicion += 1
                        save = False
                        currentToken = TokenType.LE
                    else:
                        currentToken = TokenType.LT
                        if check_error_double_char(posicion, programa):
                            currentToken = TokenType.ERROR
                            save = False
                            error(
                                "Error en la formación de un operador",
                                linea,
                                columna,
                                programa,
                            )
                            posicion += 1
                            continue
                # Si es un >
                elif char == ">":
                    # Si es un >=
                    if posicion + 1 < progLong and programa[posicion + 1] == "=":
                        lexema = ">="
                        posicion += 1
                        save = False
                        currentToken = TokenType.GE
                    else:
                        currentToken = TokenType.GT
                        if check_error_double_char(posicion, programa):
                            currentToken = TokenType.ERROR
                            save = False
                            error(
                                "Error en la formación de un operador",
                                linea,
                                columna,
                                programa,
                            )
                            posicion += 1
                            continue
                # Si es un ;
                elif char == ";":
                    currentToken = TokenType.SEMI
                    if check_error_double_char(posicion, programa):
                        currentToken = TokenType.ERROR
                        save = False
                        error(
                            "Error en la formación de un operador",
                            linea,
                            columna,
                            programa,
                        )
                        posicion += 1
                        continue
                # Si es un ,
                elif char == ",":
                    currentToken = TokenType.COMMA
                    if check_error_double_char(posicion, programa):
                        currentToken = TokenType.ERROR
                        save = False
                        error(
                            "Error en la formación de un operador",
                            linea,
                            columna,
                            programa,
                        )
                        posicion += 1
                        continue
                # Si es un (
                elif char == "(":
                    currentToken = TokenType.LPAREN
                    if check_error_double_char(posicion, programa, ")"):
                        currentToken = TokenType.ERROR
                        save = False
                        error(
                            "Error en la formación de un operador",
                            linea,
                            columna,
                            programa,
                        )
                        posicion += 1
                        continue
                # Si es un )
                elif char == ")":
                    currentToken = TokenType.RPAREN
                    if check_error_double_char(posicion, programa):
                        currentToken = TokenType.ERROR
                        save = False
                        error(
                            "Error en la formación de un operador",
                            linea,
                            columna,
                            programa,
                        )
                        posicion += 1
                        continue
                # Si es un {
                elif char == "{":
                    currentToken = TokenType.LBRACE
                    if check_error_double_char(posicion, programa):
                        currentToken = TokenType.ERROR
                        save = False
                        error(
                            "Error en la formación de un operador",
                            linea,
                            columna,
                            programa,
                        )
                        posicion += 1
                        continue
                # Si es un }
                elif char == "}":
                    currentToken = TokenType.RBRACE
                    if check_error_double_char(posicion, programa):
                        currentToken = TokenType.ERROR
                        save = False
                        error(
                            "Error en la formación de un operador",
                            linea,
                            columna,
                            programa,
                        )
                        posicion += 1
                        continue
                # Si es un [
                elif char == "[":
                    currentToken = TokenType.LBRACKET
                    if check_error_double_char(posicion, programa):
                        currentToken = TokenType.ERROR
                        save = False
                        error(
                            "Error en la formación de un operador",
                            linea,
                            columna,
                            programa,
                        )
                        posicion += 1
                        continue
                # Si es un ]
                elif char == "]":
                    currentToken = TokenType.RBRACKET
                    if check_error_double_char(posicion, programa):
                        currentToken = TokenType.ERROR
                        save = False
                        error(
                            "Error en la formación de un operador",
                            linea,
                            columna,
                            programa,
                        )
                        posicion += 1
                        continue
                else:
                    currentToken = TokenType.ERROR

        # Si es un numero se busca el siguiente numero
        elif state == StateType.INNUM:
            if not char.isdigit():
                # Buscar si el siguiente caracter es un numero
                if posicion < progLong and programa[posicion].isalpha():
                    error(
                        "Error en la formación de un entero", linea, columna, programa
                    )
                    save = False
                    state = StateType.DONE
                    currentToken = TokenType.ERROR
                    continue
                save = False
                state = StateType.DONE
                currentToken = TokenType.NUM
                continue

        elif state == StateType.INID:
            if not char.isalpha():
                # Buscar si el siguiente caracter es un numero
                if posicion < progLong and programa[posicion].isdigit():
                    error(
                        "Error en la formación de un identificador",
                        linea,
                        columna,
                        programa,
                    )
                    save = False
                    state = StateType.DONE
                    currentToken = TokenType.ERROR
                    continue
                save = False
                state = StateType.DONE
                currentToken = reservedLookup(lexema)
                continue

        # Si se guarda el caracter se agrega al lexema
        if save:
            lexema += char
        # Se aumenta la posicion y la columna
        posicion += 1
        columna += 1

    # Si se imprime el token se imprime el token y el lexema
    if imprime:
        print(f"({currentToken}, {lexema})")
        # Regresa el token y el lexema
    return currentToken, lexema, linea
