# Returns 0 if this commit's version is different from the latest PyPi version

import sys
import json

with open("json", "r") as f:
    data = json.loads(f.read())
    json_version = data["info"]["version"].strip()

with open("corels/VERSION", "r") as f:
    this_version = f.read().strip()

if json_version == this_version:
    sys.exit(1)
