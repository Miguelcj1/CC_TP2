import threading
import time

# imported library
from cachetools import cached, TTLCache

#cache = TTLCache(maxsize=100, ttl=4)

bef = time.time()
time.sleep(5)
now = time.time()

print(now-bef)