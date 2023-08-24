# TO-DESIRED-STATE converter

Simple script that takes a Kanto Container Management and converts it to the desired state format.
The output of this should be treated as a convenient starting point and not the final desired state
(e.g. you might wish to add more containers there/remove propreties. specify other domains, etc).


# Installation

This script has a single external dependency benedict. To install it run:

```
$ pip install benedict
```

# Usage

The script takes as its first and only argument the path to the Kanto container management style manifest.

```
$ python3 to_desired_state.py --help
Usage: to_desired_state.py [PATH_TO_KANTO_MANIFEST]

Converts a Kanto Container Management-style manifest
to a desired state manifest, re-mapping the container configuration options.
Note: the resulting file should be treated as a starting point (partially filled-in template) only.
```

# Sample results

Sample results can be found in the `test_manifests` directory.