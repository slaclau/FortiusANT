import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)
    if len(sys.argv) > 1:
        print(f"# {sys.argv[2]}")
    n = 0
    print(f"{len(data)} files checked")
    for i in data:
        print(i)
