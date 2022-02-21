# cloudwash

## Introduction

`cloudwash` is a library written in python that can be used to monitor and remove the unused cloud resources in public and private cloud providers.

Most importantly, `cloudwash` provides the CLI utility called '`swach`' that can be used to fire commands to cleanup the resources on cloud.

cloudwash supports following cloud providers:

* Amazon EC2
* Google Cloud
* Microsoft Azure
* RedHat Enterprize Virtualization Manager - RHEV (Provisioned)
* RedHat Openstack (Provisioned)
* VMWare vCenter (Provisioned)

The list of resources it helps to clean are:

* VMs
* Network Interfaces
* Public IPs
* Disks


## Installation

`cloudwash` can be installed via `pip` once you clone this git repository locally.
It is always a good idea to use virtualenv to install pip packages.

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
# git clone https://github.com/RedHatQE/cloudwash.git
# cd cloudwash
# pip install .
# cp settings.yaml.template settings.yaml
```


## Configuration


To use this tool one needs to copy the `settings.yaml.template` to `settings.yaml` as instructed in Installation section above.
Then, edit the `settings.yaml` and feed all the configuration needed to connect with the cloud providers as clients.

`cloudwash` uses the `DynaConf` configuration python module to access the data in `settings.yaml` and it allows an unique way of declaring secrets via Environment variables instead of putting in plain `settings.yaml`.

e.g: The Azure password field can be set via environment variable by exporting the environment variable

```
# export CLEANUP_PROVIDERS__AZURE__PASSWORD = myPa$$worb"
```

## Usage Examples


* Cleanup Help:

```
# swach --help

Usage: swach [OPTIONS] COMMAND [ARGS]...

A Cleanup Utility to remove the VMs, Discs and Nics from Providers!

Options:
-d, --dry Only show what will be removed from Providers!
--help Show this message and exit.

Commands:
azure		Cleanup Azure provider
ec2			Cleanup Amazon provider
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
  --all    Remove all unused Resources from the provider
  --nics   Remove only unused NICs from the provider
  --discs  Remove only unused DISCs from the provider
  --vms    Remove only unused VMs from the provider
  --pips   Remove only PiPs from the provider
  --help   Show this message and exit.

```

* Cleanup Dry Run (Monitor only mode):

```
# swach -d azure --all

<<<<<<< Running the cleanup script in DRY RUN mode >>>>>>>
The AZURE providers settings are initialized and validated !

=========== DRY SUMMARY ============

VMs:
	Deletable: ['test-bvhoduliam']
	Stoppable: ['foremanqe-nightly2']
DISCs:
	Deletable: ['test-axodawttrw-nic0']
NICs:
	Deletable: ['test-axodawttrw-nic0']
PIPs:
	Deletable: ['test-axodawttrw-nic0']
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
