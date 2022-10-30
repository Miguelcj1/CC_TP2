import random
import time

def init_send_querry(id, flag, dom, type):
    string = ",".join((str(id), flag)) + ",0,0,0,0;" + ",".join((dom, type)) + ";"
    return string

class Query:

    def __init__(self):
        pass

