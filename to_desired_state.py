#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from benedict import benedict

desired_state_jsons = r"""
{
    "activityId": "",
    "payload": {
        "domains": [
            {
                "id": "containers",
                "config": [],
                "components": [
                    {
                        "id": "",
                        "version": "",
                        "config": []
                    }
                ]
            }
        ]
    }
}
"""
desired_state_manifest = json.loads(desired_state_jsons)


def print_help():
    print(f"Usage: {sys.argv[0]} [PATH_TO_KANTO_MANIFEST]\n")
    print("Converts a Kanto Container Management-style manifest")
    print(
        "to a desired state manifest, re-mapping the container configuration options."
    )
    print(
        "Note: the resulting file should be treated as a starting point (partially filled-in template) only."
    )


if len(sys.argv) != 2:
    print_help()
    exit(-1)

if sys.argv[1] == "-h" or sys.argv[1] == "--help":
    print_help()
    exit(0)

manifest_file = Path(sys.argv[1])

with open(manifest_file.resolve(True)) as fh:
    manifest_dict = benedict(json.load(fh))


def add_key_value(config, k, v):
    config.append({"key": k, "value": v})


def add_key_value_opt(config, k, v):
    # catching all Falsy values can be error prone so only deal with those specific cases
    if (v is not None) and (v != []) and (v != {}):
        add_key_value(config, k, v)
        return


# parse the env array from the manifest
def add_env_vars(config, env_list):
    if not env_list:
        return
    for env_var in env_list:
        add_key_value_opt(config, k="env", v=env_var)


def add_cmd(config, cmd_list):
    if not cmd_list:
        return
    for cmd in cmd_list:
        add_key_value_opt(config, k="cmd", v=cmd)


def flatten_mount_point(mount):
    source = mount["source"]
    dest = mount["destination"]
    propagation_mode = mount.get("propagation_mode")

    if propagation_mode:
        return f"{source}:{dest}:{propagation_mode}"
    else:
        return f"{source}:{dest}"


def add_mounts(config, mounts_list):
    if not mounts_list:
        return
    for mount in mounts_list:
        add_key_value_opt(config, "mount", flatten_mount_point(mount))


def flatten_port(port):
    # defaults are from kanto docs
    proto = port.get("proto", "tcp")
    container_port = port["container_port"]
    host_ip = port.get("host_ip", "0.0.0.0")
    host_port = port["host_port"]
    host_port_end = port.get("host_port_end", host_port)

    return f"{host_ip}:{container_port}:{host_port}-{host_port_end}/{proto}"


def add_ports(config, ports_list):
    if not ports_list:
        return
    for port in ports_list:
        add_key_value_opt(config, "port", flatten_port(port))


def flatten_device(device):
    path_on_host = device["path_on_host"]
    path_in_container = device["path_in_container"]
    cgroup_permissions = device.get("cgroup_permissions", "rwm")
    privileged = device.get("privileged", False)  # ? missing in desired state

    return f"{path_on_host}:{path_in_container}:{cgroup_permissions}"


def add_devices(config, devices_list):
    if not devices_list:
        return
    for device in devices_list:
        add_key_value_opt(config, "device", flatten_device(device))


def add_extra_hosts(config, hosts_list):
    if not hosts_list:
        return
    for extra_hosts_entry in hosts_list:
        add_key_value_opt(config, "host", extra_hosts_entry)


desired_state_config = []

add_key_value(desired_state_config, k="image", v=manifest_dict["image"]["name"])

add_mounts(desired_state_config, manifest_dict.get(["mount_points"]))

add_env_vars(desired_state_config, manifest_dict.get(["config", "env"]))
add_cmd(desired_state_config, manifest_dict.get(["config", "cmd"]))

add_key_value_opt(
    desired_state_config,
    k="privileged",
    v=manifest_dict.get(["host_config", "privileged"]),
)
add_key_value_opt(
    desired_state_config,
    k="network",
    v=manifest_dict.get(["host_config", "network_mode"]),
)
add_ports(desired_state_config, manifest_dict.get(["host_config", "port_mappings"]))
add_devices(desired_state_config, manifest_dict.get(["host_config", "devices"]))
add_extra_hosts(desired_state_config, manifest_dict.get(["host_config", "extra_hosts"]))
add_key_value_opt(
    desired_state_config,
    k="restartPolicy",
    v=manifest_dict.get(["host_config", "restart_policy", "type"]),
)
add_key_value_opt(
    desired_state_config,
    k="restartMaxRetries",
    v=manifest_dict.get(["host_config", "restart_policy", "maximum_retry_count"]),
)
add_key_value_opt(
    desired_state_config,
    k="restartTimeout",
    v=manifest_dict.get(["host_config", "restart_policy", "retry_timeout"]),
)

add_key_value_opt(
    desired_state_config,
    k="logDriver",
    v=manifest_dict.get(["host_config", "log_config", "driver_config", "type"]),
)
add_key_value_opt(
    desired_state_config,
    k="logMaxFiles",
    v=manifest_dict.get(["host_config", "log_config", "driver_config", "max_files"]),
)
add_key_value_opt(
    desired_state_config,
    k="logMaxSize",
    v=manifest_dict.get(["host_config", "log_config", "driver_config", "max_size"]),
)
add_key_value_opt(
    desired_state_config,
    k="logMode",
    v=manifest_dict.get(["host_config", "log_config", "mode_config", "mode"]),
)
add_key_value_opt(
    desired_state_config,
    k="memory",
    v=manifest_dict.get(["host_config", "resources", "memory"]),
)
add_key_value_opt(
    desired_state_config,
    k="memorySwap",
    v=manifest_dict.get(["host_config", "resources", "memory_reservation"]),
)
add_key_value_opt(
    desired_state_config,
    k="memoryReservation",
    v=manifest_dict.get(["host_config", "resources", "memory_swap"]),
)

add_key_value_opt(
    desired_state_config, k="terminal", v=manifest_dict.get(["io_config", "tty"])
)

add_key_value_opt(
    desired_state_config,
    k="interactive",
    v=manifest_dict.get(["io_config", "open_stdin"]),
)


name = manifest_dict["container_name"]
image_ref = manifest_dict["image"]["name"]
image_ref_split = image_ref.rsplit(":", maxsplit=1)

if len(image_ref_split) == 1:
    version = "latest"  # use latest as default version
else:
    version = image_ref_split[-1]

desired_state_manifest["payload"]["domains"][0]["components"][0]["id"] = name
desired_state_manifest["payload"]["domains"][0]["components"][0]["version"] = version
desired_state_manifest["payload"]["domains"][0]["components"][0][
    "config"
] = desired_state_config

output_file_name = f"{manifest_file.stem}_desired_state{manifest_file.suffix}"

with open(manifest_file.parent / output_file_name, "w") as f:
    json.dump(desired_state_manifest, f, indent=2)

print(f"Saved as {manifest_file.parent/output_file_name}.")
print("WARNING: This is file should be used as a starting template only!")
