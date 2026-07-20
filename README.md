# Ray for AI Lab

A native Ray cluster setup for a private AI learning lab.

This repository documents the complete Fedora Ray head-node installation that was tested successfully before adding NVIDIA Jetson worker nodes.

> Cloudflare configuration is intentionally not included in this repository. It will be configured separately.

---

## Project Goal

The purpose of this lab is to learn and test:

- Distributed Python workloads
- Ray task scheduling
- Parallel machine-learning experiments
- Jetson-based edge AI workloads
- CUDA-enabled GPU tasks
- TensorRT inference
- Future Docker, K3s, and KubeRay deployment

The first implementation uses a native Python installation because it is easier to troubleshoot networking, Ray compatibility, CUDA, and Jetson hardware access before adding containers or Kubernetes.

---

## Current Architecture

```text
Fedora Server
    |
    |-- Ray Head Node
    |-- Ray Dashboard
    |
    +---- Private Local Network ---- Jetson Ray Workers
```

Current status:

```text
Fedora Ray head node: Working
Ray dashboard: Working
Ray Python task test: Passed
Jetson workers: Not connected yet
Cloudflare: Separate configuration phase
```

---

## Tested Environment

| Setting | Value |
|---|---|
| Operating system | Fedora Linux 42 Workstation |
| Fedora architecture | x86_64 |
| Fedora system Python | Python 3.13.7 |
| Ray environment Python | Python 3.12.13 |
| Ray version | 2.56.1 |
| Fedora hostname | fedora |
| Fedora LAN IP during setup | 192.168.1.181 |
| Ray head port | 6379 |
| Ray dashboard address | 127.0.0.1 |
| Ray dashboard port | 8265 |
| Fedora CPU resources detected by Ray | 8 |

> `192.168.1.181` was the Fedora address during this setup. Check the current LAN address before starting Ray because DHCP may assign a different address later.

---

## Repository Structure

```text
RayforAI-lab/
├── README.md
├── .gitignore
├── requirements.txt
└── test.py
```

The local virtual environment is not committed:

```text
.renv/
```

---

# Fedora Ray Head-Node Setup

## 1. Confirm the Fedora System

Run:

```bash
hostname
cat /etc/os-release | head
uname -m
python3 --version
ip -br -4 addr
```

Expected important values:

```text
Hostname: fedora
Architecture: x86_64
System Python: Python 3.13.x
LAN interface: 192.168.1.x
```

Do not use these addresses as the Ray head address:

```text
127.0.0.1
172.17.0.1
```

- `127.0.0.1` is the local loopback address.
- `172.17.0.1` is normally the Docker bridge address.

During the tested setup, the correct Fedora LAN address was:

```text
192.168.1.181
```

---

## 2. Install Python 3.12

Fedora 42 uses Python 3.13 as its system Python.

Python 3.12 is installed beside Python 3.13. This does not downgrade Fedora and does not replace the system Python used by Fedora or Coder.

```bash
sudo dnf install -y python3.12
```

Verify both versions:

```bash
python3 --version
python3.12 --version
```

Expected example:

```text
Python 3.13.7
Python 3.12.13
```

Do not change Fedora's system Python with commands such as:

```bash
sudo alternatives --set python ...
sudo ln -sf ... /usr/bin/python3
sudo dnf remove python3
```

---

## 3. Clone the Repository

```bash
git clone https://github.com/SethuGopalan/RayforAI-lab.git
cd RayforAI-lab
```

For the original installation, the local working folder was:

```text
/home/sethugopalan/ray-lab
```

The GitHub repository can still be named `RayforAI-lab`.

---

## 4. Create the Python 3.12 Virtual Environment

Create the environment:

```bash
python3.12 -m venv .renv
```

The `-m` option is required.

Correct:

```bash
python3.12 -m venv .renv
```

Incorrect:

```bash
python3.12 m venv .renv
```

Activate the environment:

```bash
source .renv/bin/activate
```

Do not use:

```bash
source .renv
```

because `.renv` is a directory. The activation script is inside `.renv/bin/activate`.

Verify the active Python version:

```bash
python --version
```

Expected:

```text
Python 3.12.x
```

The terminal prompt may show:

```text
(.renv)
```

---

## 5. Install Ray

Upgrade pip inside the virtual environment:

```bash
python -m pip install --upgrade pip
```

Install the exact Ray version used by this project:

```bash
python -m pip install -r requirements.txt
```

The `requirements.txt` file contains:

```text
ray[default]==2.56.1
```

Verify the installation:

```bash
ray --version
```

Expected:

```text
ray, version 2.56.1
```

The `default` Ray package includes Ray Core, the dashboard, and cluster-management tools.

---

## 6. Stop Any Incomplete Ray Processes

Before starting the head node:

```bash
ray stop --force
```

A result such as this is normal when Ray is not already running:

```text
Did not find any active Ray processes.
```

---

## 7. Start Fedora as the Ray Head Node

Use the Fedora LAN address, not the loopback or Docker address.

Tested command:

```bash
ray start --head \
  --node-ip-address=192.168.1.181 \
  --port=6379 \
  --dashboard-host=127.0.0.1 \
  --dashboard-port=8265 \
  --disable-usage-stats
```

If the Fedora LAN address has changed, replace `192.168.1.181`.

Example using a shell variable:

```bash
RAY_HEAD_IP=192.168.1.181

ray start --head \
  --node-ip-address="$RAY_HEAD_IP" \
  --port=6379 \
  --dashboard-host=127.0.0.1 \
  --dashboard-port=8265 \
  --disable-usage-stats
```

### Meaning of the settings

| Setting | Purpose |
|---|---|
| `--head` | Starts this computer as the Ray head node |
| `--node-ip-address` | LAN address used by worker nodes |
| `--port=6379` | Ray head connection port |
| `--dashboard-host=127.0.0.1` | Keeps the dashboard local to Fedora |
| `--dashboard-port=8265` | Ray dashboard port |
| `--disable-usage-stats` | Disables Ray usage-statistics collection |

A successful start should include:

```text
Local node IP: 192.168.1.181
Ray runtime started.
```

Ray will also print the worker connection command:

```bash
ray start --address='192.168.1.181:6379'
```

---

## 8. Check the Ray Cluster Status

Run:

```bash
ray status
```

The tested Fedora head node showed:

```text
Active nodes: 1
Pending nodes: none
Recent failures: none
CPU resources: 8
```

The first active node is the Fedora head node.

Example resource summary:

```text
0.0/8.0 CPU
0B/6.93GiB memory
0B/2.97GiB object_store_memory
```

Exact memory values may vary.

---

## 9. Verify the Ray Dashboard

Test the local dashboard:

```bash
curl -s -o /dev/null \
  -w "Dashboard HTTP status: %{http_code}\n" \
  http://127.0.0.1:8265
```

Expected:

```text
Dashboard HTTP status: 200
```

The dashboard can also be opened in a browser running on Fedora:

```text
http://127.0.0.1:8265
```

The dashboard was intentionally bound to `127.0.0.1` so it is not directly exposed to the home network or public internet.

---

## 10. Run the Ray Cluster Test

Make sure the virtual environment is active and the Ray head node is running:

```bash
source .renv/bin/activate
python test.py
```

Expected output:

```text
Ray task executed successfully
Execution node: fedora
```

The test also prints the cluster resources.

Example:

```text
Cluster resources:
{
    'CPU': 8.0,
    'node:192.168.1.181': 1.0,
    'node:__internal_head__': 1.0
}
```

This test confirms that:

1. Python connected to the running Ray cluster.
2. Ray accepted a remote task.
3. Ray scheduled the task on Fedora.
4. Fedora executed the task.
5. Ray returned the result to the Python program.
6. The Python test disconnected without stopping the Ray cluster.

---

## 11. Test File

The repository includes `test.py`:

```python
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
```

---

## 12. Stop Ray

Stop the Ray runtime:

```bash
ray stop
```

For a forced cleanup:

```bash
ray stop --force
```

Stopping Ray does not remove:

- Python 3.12
- The `.renv` virtual environment
- Installed packages
- Repository files

---

## 13. Restart Ray Later

Return to the project:

```bash
cd ~/ray-lab
```

Activate the environment:

```bash
source .renv/bin/activate
```

Check the current Fedora LAN address:

```bash
ip -br -4 addr
```

Start Ray again:

```bash
ray start --head \
  --node-ip-address=192.168.1.181 \
  --port=6379 \
  --dashboard-host=127.0.0.1 \
  --dashboard-port=8265 \
  --disable-usage-stats
```

Check the status:

```bash
ray status
```

Run the test:

```bash
python test.py
```

---

# Future Jetson Worker Setup

The first Jetson worker will be connected only after confirming:

```bash
hostname
uname -m
python3 --version
ip -br -4 addr
ping -c 4 192.168.1.181
```

Expected Jetson architecture:

```text
aarch64
```

The worker should use:

- A compatible Python version
- Ray 2.56.1
- Its own Python virtual environment
- The same private LAN as Fedora

The future worker connection command is:

```bash
ray start --address='192.168.1.181:6379'
```

After connecting a Jetson, run this on Fedora:

```bash
ray status
```

The cluster should then show two active nodes:

```text
Fedora head node
Jetson worker node
```

The first worker test will run a CPU task on the Jetson before testing CUDA or TensorRT.

---

# Why CUDA and TensorRT Are Separate

Ray does not provide GPU acceleration by itself.

```text
Ray       -> schedules and distributes tasks
CUDA      -> allows supported code to use NVIDIA GPUs
TensorRT  -> optimizes trained neural-network models for inference
```

The planned implementation order is:

```text
1. Fedora Ray head node
2. First Jetson Ray worker
3. CPU task on Jetson
4. CUDA verification
5. GPU task
6. TensorRT inference test
7. Additional Jetson workers
8. Docker
9. K3s and KubeRay
```

---

# Git Setup

The repository is initialized with:

```bash
git init
git branch -M main
```

Add the project files:

```bash
git add README.md .gitignore requirements.txt test.py
```

Review before committing:

```bash
git status
```

The `.renv` directory must not appear as a tracked file.

Commit:

```bash
git commit -m "Document Ray head installation and cluster test"
```

Connect the GitHub repository:

```bash
git remote add origin https://github.com/SethuGopalan/RayforAI-lab.git
```

Push:

```bash
git push -u origin main
```

---

# `.gitignore`

The repository uses:

```gitignore
# Python virtual environments
.renv/
.venv/
venv/

# Python cache
__pycache__/
*.py[cod]

# Ray-generated files
.ray/
ray_results/

# Environment variables and secrets
.env

# Editor files
.vscode/
.idea/

# Operating-system files
.DS_Store
```

---

# Security Notes

- Do not expose Ray port `6379` publicly.
- Do not expose Ray Client port `10001` publicly.
- Do not configure router port forwarding for Ray.
- Jetson worker connections should stay on the private LAN.
- Keep the Ray dashboard bound to `127.0.0.1`.
- Do not commit tokens, passwords, `.env` files, private keys, or Cloudflare credentials.
- Cloudflare dashboard access will be configured separately from this repository.

---

# Completed Milestone

The following setup has been completed and tested:

- Fedora 42 confirmed
- Fedora x86_64 architecture confirmed
- Python 3.12.13 installed beside Python 3.13.7
- `.renv` virtual environment created
- Ray 2.56.1 installed
- Fedora started as the Ray head node
- Ray registered 8 CPU resources
- Ray dashboard returned HTTP status 200
- `test.py` connected to the cluster
- Remote task executed successfully on `fedora`
- Cluster resources returned successfully
- Git repository initialized on branch `main`
- `.renv` excluded through `.gitignore`

---

# Next Milestone

1. Commit and push this repository to GitHub.
2. Configure `ray.terrafoxai.com` separately through Cloudflare.
3. Connect the first Jetson worker.
4. Run a task specifically on the Jetson.
5. Verify CUDA and GPU resources.
6. Add the remaining Jetson workers.
