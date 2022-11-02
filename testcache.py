import threading
import time

# imported library
from cachetools import cached, TTLCache

#cache = TTLCache(maxsize=100, ttl=4)

def delete_after(cache, key, ttl):
    time.sleep(ttl)
    del cache[key]

key = 1
cache = {key: "ola"}
print(cache[key])

threading.Thread(target=delete_after,args=(cache, key, 3)).start()

print(cache[key])

time.sleep(4)

try:
    print(cache[key])
except Exception as exc:
    print(f"O valor correspondente a {key} não foi encontrado!")

