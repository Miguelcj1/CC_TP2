import threading
import time
import random

# imported library
from cachetools import cached, TTLCache
#cache = TTLCache(maxsize=100, ttl=4)

fp = open("var/dns/test.log")
info = "ola"+"\n"
fp.write(info, end = "")
print("oi")
fp.close()