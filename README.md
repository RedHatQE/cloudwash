# Cloudwash

## Introduction

`cloudwash` is a library written in python that can be used to monitor and remove the unused cloud resources in public and private cloud providers.

Most importantly, `cloudwash` provides the CLI utility called '`swach`' that can be used to fire commands to cleanup the resources on cloud.

cloudwash supports following cloud providers:

| Cloud Providers  | vms    | nics    | discs     | images   | pips    | stacks   |
|------------------|--------|---------|-----------|----------|---------|----------|
| Amazon EC2       | &check;| &check; | &check;   |  &check; |  &check;|  &check; |
| Microsoft Azure  | &check;| &check; | &check;   |  &check; |  &check;|  **NA**  |
| Google Cloud     | &check;| &check; | &check;   |  &cross; |  &cross;|  **NA**  |
| VMWare           | &check;| &check; | &check;   |  &cross; |  **NA** |  **NA**  |

* RedHat Enterprize Virtualization Manager - RHEV (_Support yet To be added_)
* RedHat Openstack (_Support yet To be added_)
* OCP Clusters deplyed on Public clouds (_Support yet To be added_)

NOTE: You can use `--all` flag with all the cloud providers to clean all supported resources.

The list of resource types it helps to clean could be found under settings.yaml.template](https://github.com/RedHatQE/cloudwash/blob/master/settings.yaml.template) file for individual cloud providers along with cleanup criteria.

## Installation

User can run `cloudwash` multiple ways:
- [PiP Package Installation](#pip-package-installation)
- [Docker Image Installation](#docker-image-installation)
- [OC BuildConfig Installation](#oc-buildconfig-installation)

### PiP Package Installation

For Linux Users, Depending on the distribution you are using, you may need to install following packages
(or similar for your distribution of linux):

* libcurl-devel
* openssl-devel
* libxml2-devel
* libxml2-static
* gcc

Pycurl is a one of the dependent package of `cloudwash` that wants you to install above dependencies.
Read more about it http://pycurl.io/docs/latest/install.html

Installation:

```
$ mkdir ~/cloudwash && cd ~/cloudwash
$ pip install cloudwash
```

### Docker Image Installation

#### From Container image registry
The [container image](https://quay.io/repository/redhatqe/cloudwash) for cloudwash is available in quay. This image provides the cloudwash installed from released python package with release version tags. Latest tag always points to the latest released version tag.

#### Build from local DockerFile
This github repo contains a DockerFile, use any container building service to build from the dockerfile:

Build container from `Dockerfile.dev` that should build a container from the cloudwash github master branch giving the access to pre-released features.


### OC BuildConfig Installation
This github repo provides the ready to use BuildConfig on OCP / Kubernetes. The build config should create buildconfig to build master branch based container image. Use the image to build cloudwash pod.


## Configuration

The `cloudwash` uses the `DynaConf` configuration python module to access the data in `settings.yaml` or conf directory settings, it also allows an unique way of declaring secrets via Environment variables instead of putting in plain `settings.yaml`.

e.g: The Azure password field can be set via environment variable by exporting the environment variable

```
# export CLEANUP_PROVIDERS__AZURE__PASSWORD = myPa$$worb"
```

#### Configuration with PyPi package:

Copy/Download `settings.yaml.template` to local `~/cloudwash` directory as `settings.yaml`, update it with the cloud provider credentials and other configuration details for successful resource reporting and cleanup.


#### Configuration with cloudwash container images:

_Either_ - The docker images have `settings.yaml` added from Dockerfile. Build the container from the image, access the container and update the `settings.yaml` with real values and commit the changes to the image. Use the commited image for cleanup activity.

_Or_ - Export/Set the environment variables for all or only sensitive credentials as shown above. The dynaconf in cloudwash container should read these credentials from environment variable.


## Usage Examples


* Cleanup Help:

```
# swach --help

Usage: swach [OPTIONS] COMMAND [ARGS]...

A Cleanup Utility to remove cloud resources from cloud Providers!

Options:
-d, --dry Only show what will be removed from Providers!
--help Show this message and exit.

Commands:
azure		Cleanup Azure provider
aws			Cleanup Amazon provider
gce			Cleanup GCE provider
openstack	Cleanup OSP provider
rhev 		Cleanup RHEV provider
vmware 		Cleanup VMWare provider
```

* Cleanup Cloud Provider help:

```
# swach azure --help

Usage: swach azure [OPTIONS]

  Cleanup Azure provider

Options:
  --all             Remove all unused Resources from the provider
  --all_rg          Remove resource group only if all resources are older than SLA
  --nics            Remove only unused NICs from the provider
  --discs           Remove only unused DISCs from the provider
  --vms             Remove only unused VMs from the provider
  --pips            Remove only PiPs from the provider
  --help            Show this message and exit.

```

* Cleanup Dry Run (Monitor only mode using option `-d`):

```
# swach -d azure --all

<<<<<<< Running the cleanup script in DRY RUN mode >>>>>>>
The AZURE providers settings are initialized and validated !

=========== DRY SUMMARY ============

VMs:
	Deletable: ['test-bvhoduliam']
	Stoppable: ['foremanqe-nightly2']
DISCs:
	Deletable: ['test-bvhoduliam-osdisk']
NICs:
	Deletable: ['test-axodawttrw-nic0']
PIPs:
	Deletable: ['test-axodawttrw-pip0']
====================================
```

* Actual Cleanup Run:

```
# swach azure --all

<<<<<<< Running the cleanup script in ACTION mode >>>>>>>
The AZURE providers settings are initialized and validated !

Stopped [] and removed ['test-bvhoduliam'] VMs from Azure Cloud.
Removed following and all unused nics from Azure Cloud.
['test-axodawttrw-nic0']
Removed following and all unused discs from Azure Cloud.
['test-bvhoduliam-osdisk']
Removed following and all unused pips from Azure Cloud.
['test-axodawttrw-pip0']
```
# How to run the cloudwash setup locally


You will need a pod spec file, config map file (optional) and a secrets file. Create files locally named:

* cloudwash.testpod.yaml:
```
apiVersion: v1
kind: Pod
metadata:
  name: cloudwash-test-pod
spec:
  containers:
    - name: cloudwash
      image: quay.io/redhatqe/cloudwash
      command: ["/bin/sh"]
      args: ["-c", "sleep 5000"]
      volumeMounts:
      - name: config-volume
        mountPath: /opt/app-root/src/cloudwash/settings.yaml
        subPath: settings.yaml
      env:
        - name: CLEANUP_AZURE__AUTH__CLIENT_ID
          valueFrom:
            secretKeyRef:
              key: azure_client_id
              name: cloudwash-secret
        - name: CLEANUP_AZURE__AUTH__SECRET_ID
          valueFrom:
            secretKeyRef:
              key: azure_client_secret
              name: cloudwash-secret
        - name: CLEANUP_AZURE__AUTH__TENANT_ID
          valueFrom:
            secretKeyRef:
              key: azure_tenant_id
              name: cloudwash-secret
        - name: CLEANUP_AZURE__AUTH__SUBSCRIPTION_ID
          valueFrom:
            secretKeyRef:
              key: subscription_id
              name: cloudwash-secret
  volumes:
    - name: config-volume
      configMap:
        name: cloudwash-config
  restartPolicy: Never
```
* cloudwash.configmap.yaml
```
apiVersion: v1
kind: ConfigMap
metadata:
  name: cloudwash-config
data:
  settings.yaml: |
    AZURE:
        AUTH:
            CLIENT_ID: ""
            SECRET_ID: ""
            TENANT_ID: ""
            SUBSCRIPTION_ID: ""
            RESOURCE_GROUPS: []
            REGIONS: []
        CRITERIA:
            VM:
                DELETE_VM: ''
                SLA_MINUTES: 120
            DISC:
                UNASSIGNED: True
            NIC:
                UNASSIGNED: True
            IMAGE:
                DELETE_IMAGE: ''
                UNASSIGNED: True
            PUBLIC_IP:
                UNASSIGNED: True
            RESOURCE_GROUP:
                LOGIC: AND
                DELETE_GROUP:
                RESOURCES_SLA_MINUTES: 120
        EXCEPTIONS:
            VM:
                VM_LIST: []
                STOP_LIST: []
            GROUP:
                RG_LIST: []
            IMAGES: []
```
* cloudwash.secrets.yaml
```
apiVersion: v1
kind: Secret
metadata:
  name: cloudwash-secret
  namespace: default
type: Opaque
stringData:
  azure_client_id: "XXXXXXXX"
  azure_client_secret: "XXXXXXX"
  azure_tenant_id: "XXXXXXXXX"
  subscription_id: "XXXXXXXXX"
```

After creating the files run these commands


Note: Ensure you have minikube installed:
https://minikube.sigs.k8s.io/docs/start/

* Check minikube status
```
minikube status
```
* If the status is stopped then start it
```
minikube start
```

* Now create all yaml files in minikube cluster:
```
minikube kubectl -- create -f cloudwash.testpod.yaml
minikube kubectl -- create -f cloudwash.configmap.yaml
minikube kubectl -- create -f Cloudwash.secrets.yaml
```

* You can check already created yaml files:
```
 minikube kubectl -- get configmap
 minikube kubectl -- get pods
 minikube kubectl -- get secrets
 ```

* If required, to delete any of the yaml files:
```
 minikube kubectl -- delete pod <podname>
 minikube kubectl -- delete configmap <configmap name>
 minikube kubectl -- delete secrets <secret name>
 ```
* Verify the container is running; check the below line from the pod yaml file
```
containers:
- name: cloudwash
   image: quay.io/redhatqe/cloudwash
command: ["/bin/sh"]
args: ["-c", "sleep 5000"]
```
* Here the lines say to stop the cloud wash container for 5000 seconds so we can run the “swach” commands in the shell
After getting the container in a running state, run this command to enter the bash shell
```
minikube kubectl -- exec -it cloudwash-test-pod -- /bin/bash
```

* Where “cloudwash-test-pod” is the name of the pod we defined in the pod spec file.
Now it will prompt you with the shell command line. Run the cloudwash commands here:
```
pip install cloudwash
swach -d azure  -- all
```
