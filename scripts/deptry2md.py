import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)
    if length(sys.argv) > 1:
        print(f"#{sys.argv[2]}")
    for i in data:
        if i == "misplaced_dev":
            i = "misplaced development"
        print(f"## {i.capitalize()} dependencies:")
        for j in data[i]:
            print(j)
    
