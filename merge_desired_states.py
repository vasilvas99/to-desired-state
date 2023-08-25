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

parsed_manifests = parsed_manifests

all_ctrs = []

for manifest in parsed_manifests:
    all_ctrs += get_containers(manifest)

# use the first manifest as base
for domain in  parsed_manifests[1]["payload"]["domains"]:
    if domain["id"] == "containers":
        domain["components"] = all_ctrs


with open("merged_desired_state.json", "w") as fh:
    json.dump(parsed_manifests[1], fh, indent=2)