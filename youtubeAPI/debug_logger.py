DEBUG_MODE=True
def logger(*string):
    global DEBUG_MODE
    if DEBUG_MODE:
        if len(string) > 1:
            print("%s" % (string,))
        else:
            print(*string)

def debug_mode(onoff):
    global DEBUG_MODE
    if onoff is True:
        DEBUG_MODE = True
    if onoff is False:
        DEBUG_MODE = False