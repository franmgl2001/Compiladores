# the hash table
BucketList = {}


# Procedure st_insert inserts line numbers and
# memory locations into the symbol table
# loc = memory location is inserted only the
# first time, otherwise ignored
def st_insert(name, lineno, loc, type=None):
    if name in BucketList:
        BucketList[name].append(lineno)
    else:
        if type is not None:
            BucketList[name] = [loc, lineno, type]
        else:
            BucketList[name] = [loc, lineno]


# Function st_lookup returns the memory
# location of a variable or -1 if not found
def st_lookup(name):
    if name in BucketList:
        return BucketList[name][0]
    else:
        return -1


# Function to get the type of a variable
def st_get_type(name):
    if name in BucketList and len(BucketList[name]) > 2:
        return BucketList[name][2]
    else:
        return None


def printSymTab():
    print("Variable Name  Location   Line Numbers   Type")
    print("-------------  --------   ------------   ----")
    for name in BucketList:
        print(f"{name:15}{BucketList[name][0]:8d}", end="")
        for i in range(len(BucketList[name]) - 1):
            if i == len(BucketList[name]) - 2 and len(BucketList[name]) > 2:
                print(f"   {BucketList[name][i+1]}", end="")
            else:
                print(f"{BucketList[name][i+1]:4d}", end="")
        print()
