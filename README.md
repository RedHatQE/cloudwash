# Cloudwash

[![PyPi & Quay Releases](https://github.com/RedHatQE/cloudwash/actions/workflows/new_release.yml/badge.svg)](https://github.com/RedHatQE/cloudwash/actions/workflows/new_release.yml)
[![CodeQL](https://github.com/RedHatQE/cloudwash/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/RedHatQE/cloudwash/actions/workflows/codeql-analysis.yml)
[![Dependabot Updates](https://github.com/RedHatQE/cloudwash/actions/workflows/dependabot/dependabot-updates/badge.svg)](https://github.com/RedHatQE/cloudwash/actions/workflows/dependabot/dependabot-updates)
[![pages-build-deployment](https://github.com/RedHatQE/cloudwash/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/RedHatQE/cloudwash/actions/workflows/pages/pages-build-deployment)

## Introduction

`cloudwash` is a library written in python that can be used to monitor and remove the unused cloud resources in public and private cloud providers.

Most importantly, `cloudwash` provides the CLI command utility called '`swach`' to fire commands to cleanup the resources on cloud.

cloudwash supports following cloud providers:

| Cloud Providers  | VMs     | NICs    | DISCs   | IMAGEs  | Groups  | OCPs    | PIPs    | Stacks   |
|------------------|---------|---------|---------|---------|---------|---------|---------|----------|
| Amazon EC2       | &check; | &check; | &check; | &check; | &cross; | **DRY** | &check; | &check;  |
| Microsoft Azure  | &check; | &check; | &check; | &check; | &check; | &cross; | &check; | **NA**   |
| Google Cloud     | &check; | &cross; | &cross; | &cross; | &cross; | &cross; | &cross; | **NA**   |
| VMWare           | &check; | &check; | &check; | &cross; | &cross; | &cross; | **NA**  | **NA**   |

| Podman | Containers &check; |
|--------|--------------------|

The list of resource types Cloudwash helps to clean should be found under [settings.yaml.template](https://github.com/RedHatQE/cloudwash/blob/master/settings.yaml.template) file for individual cloud providers along with cleanup criteria.


## Guidelines for Users and Contributors:
- [Contributing](https://github.com/RedHatQE/cloudwash/blob/master/Docs/CONTRIBUTING.md)
- [User Guide](https://github.com/RedHatQE/cloudwash/blob/master/Docs/USER_GUIDE.md)
