# Author Ozgur Koca https://github.com/enseitankado
import sys, json
for line in sys.stdin:
    j = json.loads(line)
    if j["type"] == sys.argv[1] and j["anonymity"] == "high_anonymous":
        print(j["host"],":",j["port"],sep='')

