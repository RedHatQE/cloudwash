# User Guide for Cloudwash

Welcome to the world of **Cloudwash**! This guide will help you understand how to use the `cloudwash` tool to monitor and remove unused cloud resources in public and private cloud providers.


## Installation

User can run `cloudwash` multiple ways:
- [PiP Package Installation](#pip-package-installation)
- [Docker Image Installation](#docker-image-installation)
- [Local Minikube Installation](#local-minikube-installation)
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


### Local Minikube Installation
[How to run the cloudwash setup locally using Minikube](https://github.com/RedHatQE/cloudwash/blob/master/Docs/Run_cloudwash_locally.md)

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

  A Cleanup Utility to remove the VMs, Discs and Nics from Providers!

Options:
  --version  Get installed version of cloudwash in system
  -d, --dry  Only show what will be removed from Providers!
  --help     Show this message and exit.

Commands:
  aws        Cleanup Amazon provider
  azure      Cleanup Azure provider
  gce        Cleanup GCE provider
  openstack  Cleanup OSP provider
  podman     Cleanup Podman provider
  rhev       Cleanup RHEV provider
  vmware     Cleanup VMWare provider
```

* Cleanup Cloud Provider help:
```
# swach azure --help
```

* Cleanup Dry Run (Monitor only mode using option `-d`):
E.g:
```shell
# swach -d azure --vms --discs --nics
```

* Actual Cleanup Run:

E.g:
```shell
# swach azure --vms --discs --nics
```

Note: The `--all` flag can be used with all the cloud providers to clean all supported resources.
