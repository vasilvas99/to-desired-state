# To-desired-state-converter

Simple script that takes a Kanto Container Management and converts it to the desired state format.
The output of this should be treated as a convenient starting point and not the final desired state
(e.g. you might wish to add more containers there/remove propreties. specify other domains, etc).


## Installation

This script has a single external dependency benedict. To install it run:

```
$ pip install python-benedict
```

## Usage

The script takes as its first and only argument the path to the Kanto container management style manifest.

```
$ python3 to_desired_state.py --help
Usage: to_desired_state.py [PATH_TO_KANTO_MANIFEST]

Converts a Kanto Container Management-style manifest
to a desired state manifest, re-mapping the container configuration options.
Note: the resulting file should be treated as a starting point (partially filled-in template) only.
```

# Merge desired state documents

Because the containers desired state can be quite verbose and copying from the generated json files can be cumborsome the `merge_desired_states.py` takes a list 
of `[NAME]_desired_state.json` files and merges them in a single desired state document.

## Usage

```shell
$ ./merge_desired_states.py --help
Usage ./merge_desired_states.py [PATH_TO_DESIRED_STATE-1] [PATH_TO_DESIRED_STATE-2] ... [PATH_TO_DESIRED_STATE-N]

Merges desired state documents in a single one ready to be posted to the kanto update manager topic.
Note: Paths CAN be globs.
```

To merge over an entire directory (called `desired_states` for example) you can use a glob:

```shell
$ ./merge_desired_states.py desired_states/*.json
```
