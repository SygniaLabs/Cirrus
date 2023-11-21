# Cirrus - Assistant

## Overview<hr>

The Cirrus Assistant is a command-line tool that provides scalable access to a Google Cloud
environment. Based on the Google project [create-service-account](https://github.com/google/create-service-account),
Cirrus Assistant automates all steps required for obtaining a service account key file with the required permissions and
access for evidence acquisition. The generated service account key can then be used to programmatically access
data in Google Cloud. This script has been designed for seamless integration with
the [Cirrus Collector](../Collectors/README.md).
Cirrus Assistance has to be executed in [Google Cloud Shell](https://shell.cloud.google.com/) after authenticating as a
super admin.

## Capabilities<hr>

### Setup Mode

Setup mode automates all steps required to obtain a service account key with relevant IAM role bindings or
OAuth access scopes. The service account key can be used with Cirrus Collector to collect forensic artifacts. The
following steps are accomplished by Assistant during setup:

1. Create a project in GCP under the organization resource
2. Enable APIs in the project
3. Create a service account in the project
4. Depending on targeted service(s), assign access:
    1. If targeting Google Workspace or Cloud Identity, assign OAuth access scopes via domain-wide delegation
    2. If targeting GCP, perform IAM role bindings against targeted resource(s)
5. Authorize the service account
6. Create, download, and shred service account key file

### Cleanup Mode

Cleanup mode automates the steps to remove all traces of activity during setup and evidence collection. The
following steps are accomplished by Assistant during cleanup:

1. Remove IAM role bindings
2. Delete project(s) generated from setup

## Usage<hr>

### Prerequisites

Cirrus Assistant has been designed for ease of use. Simply download the script file, authenticate to an appropriately
privileged domain-managed user account, upload the script to Google Cloud Shell, and execute. There is no need
to install anything, as all dependencies are handled by the Google Cloud Shell.

### Installation & Quick Start

1. Download `cirrus_assistant.py`
2. Change the variable `PROJECT_NAME` at top of script or leave default. The variable should contain letters and/or
   numbers and should be no longer than 10 characters. <br>This name indicates the name of the new isolated project that
   the script will work from.
3. Authenticate domain-managed user account with appropriate privileges
   to [Google Cloud Shell](https://shell.cloud.google.com/)
    1. If preparing environment for collection in Google Workspace or Cloud Identity, ensure user
       has [Super Admin](https://support.google.com/a/answer/2405986?product_name=UnuFlow&hl=en&visit_id=638131556073661136-2263220696&rd=1&src=supportwidget0&hl=en)
       privileges and [IAM role](https://cloud.google.com/iam/docs/understanding-roles) with
       the `resourcemanager.projects.create` permission at the organization-level in GCP
    2. If preparing environment for collection in GCP, ensure user has an IAM role with
       the `resourcemanager.projects.create` permission at the organization-level and
       the `resourcemanager.{resource}.setIamPolicy` permission against resource(s) targeted for collection (
       where `resource` is either `projects`, `folders`, or `organizations`)
4. Create a folder within the user home directory in Cloud Shell
5. Upload `cirrus_assistant.py` to folder in Cloud Shell via option provided from three vertical dots in right corner
6. Specify mode (`setup`/`cleanup`), service (`gw`/`gcp`/`all`), associated flags, and execute script

### Environment Setup

```
usage: cirrus.py setup [-h] [--service SERVICE] [--project-id PROJECT_ID] [--folder-id FOLDER_ID] [--organization-id ORGANIZATION_ID]
optional arguments:
  -h, --help            show this help message and exit
  --service SERVICE     specify a Google Cloud service to prepare for evidence collection: [gcp, gw, all]
  --project-id PROJECT_ID
                        in comma-delimited format (no spaces), specify project ID(s) for role binding assignment
  --folder-id FOLDER_ID
                        in comma-delimited format (no spaces), specify folder ID(s) for role binding assignment
  --organization-id ORGANIZATION_ID
                        specify organization ID for role binding assignment
```

To prepare the environment for artifact collection *only* in Google Workspace or Cloud Identity:

```
python3 cirrus_assistant.py setup --service gw
```

The script can specify access to the entire organization, multiple projects and folders, or selected resources.
To prepare the environment for artifact collection *only* in GCP against three projects and two folders:

```
python3 cirrus_assistant.py setup --service gcp --project-id PID1,PID2,PID3 --folder-id FID1,FID2
```

To prepare the environment for artifact collection in both Google Workspace or Cloud Identity, and GCP at the
organization-level:

```
python3 cirrus_assistant.py setup --service all --organization-id OID
```

### Environment Cleanup

```
usage: cirrus_assistant.py cleanup [-h] [--service SERVICE]

optional arguments:
  -h, --help            show this help message and exit
  --service SERVICE     specify a Google Cloud service for removal of artifacts resulting from setup functionality: [gcp, gw, all]
```

To remove all traces of activity that occurred during setup for Google Workspace or Cloud Identity:

```
python3 cirrus_assistant.py cleanup --service gw
```

To remove all traces of activity that occurred during setup for GCP:

```
python3 cirrus_assistant.py cleanup --service gcp
```

To remove all traces of activity during occurred during setup for both Google Workspace or Cloud Identity and GCP:

```
python3 cirrus_assistant.py cleanup --service all
```