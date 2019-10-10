# How to Kubeflow

This is a part of [Valohai](https://valohai.com/) webinar about Kubeflow and machine learning platforms.

Requirements:
* Ubuntu 18.04
* snap (should be there by default on Ubuntu)
* Python 3 with pip (if you want to run the pipeline examples)

## Local Setup on Ubuntu

```bash
# Instructions tested: 2019-10-10

# Using Kubernetes 1.14 as it is the latest version GCP on my region supports to maintain version parity.
# MicroK8s 1.14+ (they use same versioning as underlying Kubernetes) uses containerd instead of Docker 
# to  avoid clashing with the host Docker. Unfortunate but we can deal with that by changing 
# the executor.
sudo snap install microk8s --classic --channel=1.14/stable

# Also, if you are planning on using newer Kubernetes like 1.16, the current Kubeflow installer
# will not work as the manifest they generate target earlier Kubernetes version.
# This will result in errors like ''no "StatefulSet" in version "apps/v1beta2" (no in "apps/v1")'

# Enable some dependencies:
# dns: CoreDNS add-on, commonly required by other add-ons.
# storage: default Kubernetes storage class to create persistent volumes on the host.
# dashboard: Kubernetes dashboard add-on for management.
microk8s.status --wait-ready
microk8s.enable dns storage dashboard
microk8s.status --wait-ready

# Alias so that "kubectl" is used from MicroK8s.
# If you don't do this and you have another kubectl installed, Kubeflow installer may 
# target a wrong cluster.
sudo snap alias microk8s.kubectl kubectl

# Note that the following will overwrite all local kubectl settings.
microk8s.kubectl config view --raw > $HOME/.kube/config

# To make sure your networking rules are OK, use the inspect command.
microk8s.inspect
# It might instruct you to enable LAN forwarding.
sudo iptables -P FORWARD ACCEPT
# and redo to check if all is good
microk8s.inspect

# Download the latest kfctl installer version.
export OPSYS=linux
export GITHUB_RELEASE_URL="https://api.github.com/repos/kubeflow/kubeflow/releases/latest"
curl -s $GITHUB_RELEASE_URL | \
    grep browser_download | \
    grep $OPSYS | \
    cut -d '"' -f 4 | \
    xargs curl -O -L && tar -zvxf kfctl_*_${OPSYS}.tar.gz && rm kfctl_*_${OPSYS}.tar.gz

# Install the command, assuming /usr/local/bin is in PATH.
sudo install -D -t /usr/local/bin kfctl
rm kfctl

# kubeflow-anonymous namespace must be created manually as of Kubeflow 6.2
# https://github.com/kubeflow/kubeflow/issues/4090
kubectl create namespace kubeflow-anonymous

# Find the version of which the latest release is based on and use that 
# to download right Kubeflow template.
export VERSION=`curl -s $GITHUB_RELEASE_URL | grep target_commitish | cut -d '"' -f 4`
export CONFIG="https://raw.githubusercontent.com/kubeflow/kubeflow/${VERSION}/bootstrap/config/kfctl_k8s_istio.yaml"

# Install Kubeflow on your local MicroK8s cluster.
# cd /path/to/your/projects/directory
export KFAPP=kfapp
kfctl init ${KFAPP} --config=${CONFIG} -V
cd ${KFAPP}
kfctl generate all -V
kfctl apply all -V

# You can follow the warmup process by following pod status.
# It will spin up +30 pods for various services.
watch -c -n 10 kubectl -n kubeflow get pods

# CONGRATULATIONS! You have Kubeflow running.
# Before we start playing with it though, you must (currently) change your executor to something
# More information: https://github.com/kubeflow/pipelines/issues/1471
kubectl -n kubeflow edit configmap workflow-controller-configmap
# And add the following before "artifactRepository":
containerRuntimeExecutor: pns,
# Other executors (docker, kubelet, k8sapi) won't work with this setup.
# After saving the document, Kubernetes will update automatically.
```

```bash
# You can access Kubeflow web UI through:
http://127.0.0.1:31380/ 
# or IP of the virtual machine hosting Kubeflow on other setups.
```

## Next Steps

### Pipelines

You can play with Kubeflow Pipelines under "Kubernetes web UI > Pipelines".
It will contain some basic examples by the Kubeflow team.

I addition, this repository contains more hands-on sample pipelines under `pipeline-examples`.

The examples are numbered from `01` onwards in increasing complexity, each example teaching something new.
Read the Python file contents to get more information about any particular example.

Usage example:

* Run `pip install -r requirements.txt` under project root.
* Run `python 01-simple-tasks.py` under the example directory.
* This will generate `01-simple-tasks.py.zip` to the current directory.
* Upload the `01-simple-tasks.py.zip` using "Kubernetes web UI > Pipelines > Upload pipeline"
* Click the generated pipeline named `01-simple-tasks` by default.
* Click "Create run".
* Name your pipeline run e.g. `simple1`, optionally change parameters and press "Start".
* Click on created pipeline run to follow the progress.

### Notebooks

You can start a Jupyter notebook server under "Kubernetes web UI > Notebook Servers".

### Hyperparameter Tuning

You can play with hyperparameter tuning tool `katib` under "Kubernetes web UI > Katib".
