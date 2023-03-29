# Author Ozgur Koca https://github.com/enseitankado
import json
import sys

# Standart girdiden JSON verisini okuyun
data = json.load(sys.stdin)

# "proto" alanındaki değerleri ekrana yazdırın
for item in data:
    if item["proto"] == sys.argv[1] and item["type"] == "elite":
        print(item["ip"],":",item["port"],sep='')