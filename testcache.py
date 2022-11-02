# imported library
from cachetools import cached, TTLCache
import time

cache = TTLCache(maxsize=100, ttl=4)

cache[1] = 1
time.sleep(1)
cache[2] = 2
time.sleep(3)


print(cache[2])

time.sleep(5)

print(cache[1])
print(cache[2])