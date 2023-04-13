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
            print("The following code(s) occurred in this file")
            codes = set(d["code"] for d in data[i])
            codeCount = {}
            codeText = {}
            for line in data[i]:
                codeCount[line['code']] = codeCount.get(line['code'], 0) + 1
                codeText[line['code']] = line['text']
            for code in codes:
                print(f"| {codeCount[code]} | {code} | {codeText[code]} |")
            count = 0
            for line in data[i]:
                count += 1
                print(f'{line["code"]} :{line["line_number"]}:{line["column_number"]}: {line["text"]}')
                print("```python")
                print(line["physical_line"].strip())
                print("```")
                if count > 100:
                    print(f"Truncated at {count} errors")
                    break
