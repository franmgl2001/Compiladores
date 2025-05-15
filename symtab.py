# the hash table
BucketList = {}


# Procedure st_insert inserts line numbers and
# memory locations into the symbol table
# loc = memory location is inserted only the
# first time, otherwise ignored
def st_insert(name, lineno, loc, type=None, is_array=False, metadata=None):
    if name in BucketList:
        BucketList[name]["linenos"].append(lineno)
    else:
        BucketList[name] = {
            "location": loc,
            "linenos": [lineno],
            "type": type,
            "is_array": is_array,
            "metadata": metadata or {},
        }


# Function st_lookup returns the memory
# location of a variable or -1 if not found
def st_lookup(name):
    if name in BucketList:
        return BucketList[name]["location"]
    return -1


def st_get_type(name):
    if name in BucketList:
        return BucketList[name]["type"]
    return None


def st_get_metadata(name):
    if name in BucketList:
        return BucketList[name].get("metadata", {})
    return {}


def printSymTab():
    print("Name            Loc  Line Nos       Type      IsArray  Metadata")
    print("-------------   ---- ------------- --------- -------- --------")
    for name, entry in BucketList.items():
        loc = entry["location"]
        lines = ", ".join(map(str, entry["linenos"]))
        typ = str(entry["type"])
        is_array = str(entry.get("is_array", False))
        metadata = str(entry.get("metadata", {}))
        print(f"{name:15}{loc:<5} {lines:<13} {typ:<9} {is_array:<8} {metadata}")
