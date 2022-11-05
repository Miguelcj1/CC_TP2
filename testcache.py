import threading
import time
import random

# imported library
from cachetools import cached, TTLCache

#cache = TTLCache(maxsize=100, ttl=4)

l1 = "ola"
l2 = ""

res = ",".join((l1,l2))
print(res)