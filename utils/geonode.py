# Author Ozgur Koca https://github.com/enseitankado
# https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc&filterUpTime=90&protocols=http&anonymityLevel=elite
import sys, json
for line in sys.stdin:
    k = json.loads(line)
    j = k["data"]
    if j["type"] == sys.argv[1] and j["anonymity"] == "high_anonymous":
        print(j["host"],":",j["port"],sep='')

