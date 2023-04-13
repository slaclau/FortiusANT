import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)
    if len(sys.argv) > 1:
        print(f"## {sys.argv[2]}")
    count = 0;
    for i in data:
        count += 1
        if len(data[i]) > 0:
            print(f"## {i.capitalize()}:")
            print(f"{len(data[i]} errors found")
