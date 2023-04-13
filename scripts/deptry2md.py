import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)
    for i in data:
        print(f"# {i.capitalize()}:")
        for j in data[i]:
            print(j)
    
