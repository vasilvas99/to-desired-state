#!/usr/bin/env python3

import json
import sys
from collections import defaultdict
from glob import glob
from itertools import chain
from pathlib import Path


def print_help():
    print(
        f"Usage {sys.argv[0]} [PATH_TO_DESIRED_STATE-1] [PATH_TO_DESIRED_STATE-2] ... [PATH_TO_DESIRED_STATE-N]\n"
        f"Merges desired state documents in a single one ready to be posted to the kanto update manager topic."
        f"Note: Paths CAN be globs."
    )


if len(sys.argv) < 2:
    print_help()
    exit(-1)

if sys.argv[1] == "-h" or sys.argv[1] == "--help":
    print_help()
    exit(0)


expanded_globs = (glob(g) for g in sys.argv[1:])
paths = (Path(p).resolve(True) for p in chain(*expanded_globs))

paths_str = "\n".join(map(lambda p: str(p), paths))
print(f"Merging:\n{paths_str}")


def get_containers(manifest):
    for domain in manifest["payload"]["domains"]:
        if domain["id"] == "containers":
            return domain["components"]
    return Exception("No containers domain found!")


parsed_manifests = []

for p in paths:
    with open(p) as fh:
        parsed_manifests.append(json.load(fh))

parsed_manifests = parsed_manifests

domain_components = defaultdict(lambda: [])
domain_configs = defaultdict(lambda: [])

# split components and configs
for manifest in parsed_manifests:
    for domain in manifest["payload"]["domains"]:
        domain_components[domain["id"]] += domain["components"]
        try:
            domain_configs[domain["id"]] += domain["config"]
        except KeyError as _:
            print(
                f'[WARNING] Domain with id = {domain["id"]} is missing a config array in one of the partial manifests.'
            )

combined_domains = []

# produce a combined desired state manifest
for domain_id in domain_components.keys():
    combined_domains.append(
        {
            "id": domain_id,
            "config": domain_configs[domain_id],
            "components": domain_components[domain_id],
        }
    )

desired_state_msg = {"activityId": "", "payload": {"domains": combined_domains}}

print("Done.")
with open("merged_desired_state.json", "w") as fh:
    json.dump(desired_state_msg, fh, indent=2)
