import threading
import time
import random

# imported library
from cachetools import cached, TTLCache
#cache = TTLCache(maxsize=100, ttl=4)


lista = [1,2,3,4,5]
r=lista.get(2)
print(r)