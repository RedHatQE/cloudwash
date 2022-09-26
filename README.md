# Cloudwash

## Introduction

`cloudwash` is a library written in python that can be used to monitor and remove the unused cloud resources in public and private cloud providers.

Most importantly, `cloudwash` provides the CLI utility called '`swach`' that can be used to fire commands to cleanup the resources on cloud.

cloudwash supports following cloud providers:

* Amazon EC2
* Google Cloud
* Microsoft Azure
* RedHat Enterprize Virtualization Manager - RHEV (_Support yet To be added_)
* RedHat Openstack (_Support yet To be added_)
* VMWare vCenter (_Support yet To be added_)
* OCP Clusters deplyed on Public clouds (_Support yet To be added_)

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
