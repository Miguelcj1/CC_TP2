import threading
import time
import random

# imported library
from cachetools import cached, TTLCache
#cache = TTLCache(maxsize=100, ttl=4)


cache = [[]]
cache[1][2] = 2
print(cache)