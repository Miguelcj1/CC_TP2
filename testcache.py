import threading
import time
import random

# imported library
from cachetools import cached, TTLCache

#cache = TTLCache(maxsize=100, ttl=4)

def duplicates(lista):
    conj = set(lista)
    res = len(conj) != len(lista)
    return res

ids = set(range(1,65535))
lista = []
for i in range(1000):
    res = random.choice(tuple(ids))
    lista.append(res)
    #print(res)
b = duplicates(lista)
print(f"Are there dups? {b}")