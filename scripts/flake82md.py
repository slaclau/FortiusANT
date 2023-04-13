import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)
    if len(sys.argv) > 1:
        print(f"## {sys.argv[2]}")
    for i in data:
        if len(data[i]) > 0:
            print(f"## {i.capitalize()}:")
            print(f"{len(data[i])} errors found")
            count = 0
            for line in data[i]:
                count += 1
                print(line["code"])
                if count > 100:
                    break
