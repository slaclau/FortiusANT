import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)
    if len(sys.argv) > 1:
        print(f"# {sys.argv[2]}")
    n = 0
    for i in data:
        n += len(data[i])
    print(f"{len(data)} files checked, {n} issues found")
    for i in data:
        if len(data[i]) > 0:
            print(f"## {i.capitalize()}:")
            print(f"{len(data[i])} issues found")
            count = 0
            for line in data[i]:
                count += 1
                print(f'{line["code"]} :{line["line_number"]}:{line["column_number"]}: {line["text"]}')
                print("python```")
                print(line["physical_line"].strip())
                print("```")
                if count > 100:
                    print(f"Truncated at {count} errors")
                    break
