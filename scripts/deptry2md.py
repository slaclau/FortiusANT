import json

with open(sys.argv[1]) as f:
    data = json.load(f)
    for i in data:
        print(i)
    
