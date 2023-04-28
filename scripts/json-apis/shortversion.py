import json
from fortius_ant import __shortversion__

schema = {
    "schemaVersion": 1,
    "label": "Version",
    "message": __shortversion__,
    "color": "blue"
}

response = json.dumps(schema)
print(response)