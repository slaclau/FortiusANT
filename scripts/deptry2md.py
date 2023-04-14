import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)
    if len(sys.argv) > 1:
        print(f"## {sys.argv[2]}")
    for i in data:
        if i == "misplaced_dev":
            ii = "misplaced development"
        else:
            ii = i
        if len(data[i]) > 0:
            print(f"## {ii.capitalize()} dependencies:")
            for j in data[i]:
                print(j)
    
