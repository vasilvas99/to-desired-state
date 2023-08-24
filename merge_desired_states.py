#!/usr/bin/env python3

import sys
import json
from pathlib import Path

def print_help():
    print(f"Usage {sys.argv[0]} [PATH_TO_DESIRED_STATE-1] [PATH_TO_DESIRED_STATE-2] ... [PATH_TO_DESIRED_STATE-N]")

if len(sys.argv) < 2:
    print_help()
    exit(-1)
    
if sys.argv[1] == "-h" or sys.argv[1] == "--help":
    print_help()
    exit(0)
    
paths = [Path(p).resolve(True) for p in sys.argv[1:]]


def get_containers(manifest):
    for domain in  manifest["payload"]["domains"]:
        if domain["id"] == "containers":
            return domain["components"]
    return Exception("No containers domain found!")

parsed_manifests = []

for p in paths:
    with open(p) as fh:
        parsed_manifests.append(json.load(fh))

# use the first manifest as base
base = parsed_manifests[1]
parsed_manifests = parsed_manifests[1:]

for manifest in parsed_manifests:
    base_ctrs = get_containers(base)
    base_ctrs += get_containers(manifest)


with open("merged_desired_state.json", "w") as fh:
    json.dump(base, fh, indent=2)