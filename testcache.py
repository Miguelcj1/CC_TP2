import threading
import time

# imported library
from cachetools import cached, TTLCache

#cache = TTLCache(maxsize=100, ttl=4)

arr = []

final = " ".join(arr)
print(final)