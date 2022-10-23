import time
from datetime import datetime, timezone
now = timezone.utc
#now = datetime.now(timezone.utc)
print(f"{now}")

print ("\n#######\n")
ts = time.gmtime()[:6]
print (ts)
day = ts[2]
month = ts[1]
year = ts[0]
hour = ts[3]
min = ts[4]
sec = ts[5]

ret = ":".join(map(str,(day, month, year))) + "." + ":".join(map(str,(hour, min, sec)))
print(ret)

