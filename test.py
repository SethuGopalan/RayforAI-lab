"""
Basic test for the Ray cluster.

This script connects to the running Ray cluster,
submits one remote task, and prints the machine
that executed the task.
"""

import socket

import ray


# Connect to the Ray cluster already running on Fedora
ray.init(address="auto")


@ray.remote
def test_ray_cluster():
    """Return the hostname of the machine executing the task."""

    return {
        "status": "Ray task executed successfully",
        "hostname": socket.gethostname(),
    }


# Submit the remote task and wait for its result
result = ray.get(test_ray_cluster.remote())

# Display the test results
print(result["status"])
print(f"Execution node: {result['hostname']}")

# Display the resources registered with the Ray cluster
print("\nCluster resources:")
print(ray.cluster_resources())

# Disconnect this script without stopping the Ray cluster
ray.shutdown()
