import json
from fortius_ant import __version__

schema = {
    "schemaVersion": 1,
    "label": "Version",
    "message": __version__,
    "color": "blue"
}

response = json.dumps(schema)
print(response)