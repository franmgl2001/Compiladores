# the hash table
BucketList = {}
scopes = []
scope_names = []


# Funcion para entrar a un nuevo scope
def enter_scope(name=""):
    global BucketList
    scopes.append(BucketList)
    scope_names.append(name)
    BucketList = {}


# Funcion para salir de un scope
def exit_scope():
    global BucketList
    if scopes:
        # Se elimina el ultimo scope de la lista de scopes
        BucketList = scopes.pop()
        # Se elimina el ultimo nombre de scope de la lista de nombres de scopes
        scope_names.pop()
    else:
        print("scope is empty")


# Funcion para insertar un nuevo simbolo en el scope actual
def st_insert(name, lineno, loc, type=None, is_array=False, metadata=None):
    # Si el simbolo ya existe en el scope actual, se agrega la linea de codigo a la lista de lineas de codigo
    if name in BucketList:
        BucketList[name]["linenos"].append(lineno)
    else:
        # Si el simbolo no existe en el scope actual, se crea un nuevo diccionario con los datos del simbolo
        BucketList[name] = {
            "location": loc,
            "linenos": [lineno],
            "type": type,
            "is_array": is_array,
            "metadata": metadata or {},
            "offset": None,  # Nuevo atributo offset inicializado en 0n
        }


# Funcion para buscar un simbolo en el scope actual
def st_lookup(name):
    # Si el simbolo existe en el scope actual, se retorna la ubicacion del simbolo
    if name in BucketList:
        return BucketList[name]["location"]
    # Si el simbolo no existe en el scope actual, se busca en los scopes anteriores
    for scope in reversed(scopes):
        if name in scope:
            return scope[name]["location"]
    return -1


# Funcion para buscar un simbolo en el scope actual
def st_lookup_current_scope(name):
    # Si el simbolo existe en el scope actual, se retorna la ubicacion del simbolo
    return BucketList[name]["location"] if name in BucketList else -1


# Funcion para obtener el tipo de un simbolo
def st_get_type(name):
    # Si el simbolo existe en el scope actual, se retorna el tipo del simbolo
    for scope in [BucketList] + list(reversed(scopes)):
        if name in scope:
            return scope[name]["type"]
    return None


# Funcion para obtener los metadatos de un simbolo
def st_get_metadata(name):
    # Si el simbolo existe en el scope actual, se retorna los metadatos del simbolo
    for scope in [BucketList] + list(reversed(scopes)):
        if name in scope:
            return scope[name].get("metadata", {})
    return {}


def st_get_is_array(name):
    # Si el simbolo existe en el scope actual, se retorna si es un array
    for scope in [BucketList] + list(reversed(scopes)):
        if name in scope:
            return scope[name].get("is_array", False)
    return False


# Funcion para obtener el offset de un simbolo
def st_get_offset(name):
    # Si el simbolo existe en el scope actual, se retorna el offset del simbolo
    for scope in [BucketList] + list(reversed(scopes)):
        if name in scope:
            return scope[name].get("offset", 0)
    return 0


# Funcion para establecer el offset de un simbolo
def st_set_offset(name, offset):
    # Si el simbolo existe en el scope actual, se establece el offset del simbolo
    for scope in [BucketList] + list(reversed(scopes)):
        if name in scope:
            scope[name]["offset"] = offset
            return True
    return False


# Funcion para imprimir el simbolo table
def printSymTab():
    # Funcion para imprimir la tabla de simbolos
    def print_table(table, name):
        print(f"Scope: {name}")
        print("Name            Loc  Line Nos       Type      IsArray  Offset  Metadata")
        print("-------------   ---- ------------- --------- -------- ------- --------")
        for name, entry in table.items():
            loc = entry["location"]
            lines = ", ".join(map(str, entry["linenos"]))
            typ = str(entry["type"])
            is_array = str(entry.get("is_array", False))
            offset = str(entry.get("offset", 0))
            metadata = str(entry.get("metadata", {}))
            print(
                f"{name:15}{loc:<5} {lines:<13} {typ:<9} {is_array:<8} {offset:<7} {metadata}"
            )
        print()

    # Imprimir scopes padre
    for i, scope in enumerate(scopes):
        name = scope_names[i] if i < len(scope_names) else f"scope_{i}"
        print_table(scope, name)
    # Imprimir scope actual
    print_table(BucketList, scope_names[-1] if scope_names else "global")
