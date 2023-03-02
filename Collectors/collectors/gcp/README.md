# Cirrus - Google Cloud Platform Collector

## Capabilities<hr>
Cirrus Google Cloud Platform (GCP) Collector is a command-line tool written in Python that utilizes REST APIs 
to collect forensic artifacts from GCP for incident response, threat hunting, and increasing security posture. The script
collections log and configuration data:

1. **Logs:** historical GCP logging data generated via the Cloud Logging service
2. **Configurations:** current GCP configuration data (resource hierarchy map, role bindings, and service account info) via the Cloud Asset Inventory service

Visit Sygnia's incident response in Google Cloud [blog](https://blog.sygnia.co/incident-response-in-google-cloud-forensic-artifacts) to learn more about the forensic artifacts!

### Log Collection

The GCP Collector provides the ability to collect logging data generated by the Cloud Logging service. 
The script allows users to collect preconfigured (includes the `all_logs` option) or custom logs against any 
number of specified resources at the same time. The script currently supports collection of the following 
preconfigured logs:

| **Log Source**                | **Script Specification** |
|-------------------------------|--------------------------|
| All available logs*           | all_logs                 |
| Admin Activity logs           | admin_activity           |
| Data Access logs              | data_access              |
| Policy Denied logs            | policy_denied            |
| Access Transparency logs      | access_transparency      |
| System Event logs             | system_event             |
| VPC Flow logs                 | vpc_flow                 |
| Compute Engine Component logs | gce_data                 |
| DNS logs                      | dns                      |
| Firewall Rules logs           | fw_rules                 |
| HTTP/S Load Balancer logs     | load_balancer            |
| Google Kubernetes Engine logs | k8s                      |
| Cloud SQL                     | cloud_sql                |

**Note*: the `all_logs` option will collect **any** log contained within the resource, including the preconfigured logs. 
Use the `--custom-logs` flag for greater precision when collecting logs not on the preconfigured list.

To gather specific logs not in the preconfigured list, the `--custom-logs` flag can be used. 
If a GCP environment contains a custom log (`projects/test-wrg-12345/logs/custom_app_audit`) you 
wish to collect, specify all characters after the `logs/` section (e.g., `--custom-logs custom_app_audit`). 
The custom log option can be used in conjunction with preconfigured logs.

### Configuration Collection
The GCP Collector provides the ability to collect a point-in-time snapshot of GCP asset(s) configuration. The 
script allows users to collect preconfigured configurations against any number of a single resource tier 
(i.e., project(s) or folder(s) or organization). The script currently supports the following configurations:

| **Configuration**                                                                                           | **Script Specification** |
|-------------------------------------------------------------------------------------------------------------|--------------------------|
| Mapping of resource hierarchy <br/>*(only available when targeting folder(s) or the organization resource)* | gcp_map                  |
| Mapping of all role bindings                                                                                | rb_map                   |
| Mapping of service accounts information                                                                     | sa_details               |
| Mapping of service account keys                                                                             | sa_key_details           |
| All configurations (all 4)                                                                                  | all_configs              |


## Usage<hr>

### Prerequisites
To execute the script, we need to have a service account key that has been authorized with the appropriate IAM roles 
at the correct resource levels. If you plan to collect forensic artifacts across the entire domain, you will need the 
appropriate IAM roles at the organizational level. APIs also need to be enabled in the service account parent project.
We recommend using the [Cirrus Assistant](../../../Assistant/README.md) script to facilitate access to a Google Cloud environment, however the 
required roles and APIs can be found in Appendix A in case manual setup is desired.

### Main Parser

```
usage: cirrus.py gcp [-h] [--key-file KEY_FILE] [--output OUTPUT] [--log-file LOG_FILE] logs, configurations ...

Google Cloud Platform forensics collection tool

optional arguments:
  -h, --help            show this help message and exit
  --key-file KEY_FILE   string path to service account JSON key file
  --output OUTPUT       output folder (default is folder "output"
  --log-file LOG_FILE   output log file path; default filename: [{DEFAULT_OUTPUT_FOLDER}]

modules:
  logs, configurations
    logs                collect historical GCP logging data
    configurations      collect current GCP configuration data
```

#### Log Collection Parser

```
usage: cirrus.py gcp [...] logs [-h] [--logs LOGS] [--project-id PROJECT_ID] [--folder-id FOLDER_ID] [--organization-id ORGANIZATION_ID] [--start-time START_TIME] [--end-time END_TIME] [--preview] 
[--custom-logs CUSTOM_LOGS]

optional arguments:
  -h, --help            show this help message and exit
  --logs LOGS           in comma-delimited format (no spaces), specify logs to collect (enter "all_logs" for all logs): ['admin_activity', 'data_access', 'policy_denied', 'access_transparency
', 'system_event', 'vpc_flow', 'gce_data', 'dns', 'fw_rules', 'load_balancer', 'k8s', 'cloud_sql', 'all_logs']
  --project-id PROJECT_ID
                        in comma-delimited format (no spaces), specify project ID(s) for log collection
  --folder-id FOLDER_ID
                        in comma-delimited format (no spaces), specify folder ID(s) for log collection
  --organization-id ORGANIZATION_ID
                        in comma-delimited format (no spaces), specify organization ID for log collection
  --start-time START_TIME
                        specify collection start date (RFC3339 format)
  --end-time END_TIME   specify collection end date (RFC3339 format)
  --preview             preview logs contained within specified resource ID(s)
  --custom-logs CUSTOM_LOGS
                        in comma-delimited format (no spaces), specify custom log(s) for collection
```

Example of collecting one week of Admin Activity and Data Access logs in one project:
```
./cirrus.py gcp --key-file creds.json logs --project-id PID1 --logs admin_activity,data_access --start-time 2022-10-01T00:00:00Z --end-time 2022-10-08T00:00:00Z
```

Example of collecting one month of all logs in two projects, two folders, and in the organization resource:
```
./cirrus.py gcp --key-file creds.json logs --project-id PID1,PID2 --folder-id FID1,FID2 --organization-id OID --logs all_logs --start-time 2022-10-01T00:00:00Z --end-time 2022-11-01T00:00:00Z
```

Example of collecting one day of two custom logs in a single project:
```
./cirrus.py gcp --key-file creds.json logs --project-id PID1 --custom-log custom_app6_retro,custom_app7_pixel --start-time 2022-06-19T00:00:00Z --end-time 2022-06-20T00:00:00Z
```

Example of collecting one day of both preconfigured logs and a single custom log across three projects:
```
./cirrus.py gcp --key-file creds.json logs --project-id PID1,PID2,PID3 --logs admin_activity,load_balancer --custom-log custom_app9_audit --start-time 2022-11-18T00:00:00Z --end-time 2022-11-19T00:00:00Z
```

#### Log Preview 
The GCP Collector provides the ability to view the available logs contained in a project, folder, or organization 
resource. This feature is available with the `--preview` flag via CLI arguments. Comma delimit resource ID's to 
gather log previews against multiple resources at the same time. Example [log preview output](./example_log_preview_output.png).

- Presents log names in their [original format](https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry), 
highlighting the resource ID where the log was generated and specific log identifier
- Can help determine the level of volume in a given resource, which may affect specific logs 
collected during initial triage
- Places recorded data into the `output/` folder with the `log_preview` file name
- File includes the timestamp, targeted resource, a list of returned logs, and equivalent list in table format 
- Previewed data includes *all* available logs gathered within the resource over its lifetime; if you plan on 
collecting logs within a specific time frame, some logs may not be available

Example of previewing available logs in one project:
```
./cirrus.py gcp --key-file creds.json logs --project-id PID1 --preview
```

Example of previewing available logs in multiple projects, folders, and organization:
```
./cirrus.py gcp --key-file creds.json logs --project-id PID1,PID2,PID3 --folder-id FID1,FID2 --organization-id OID --preview
```

#### Configurations Collection Parser

```
usage: cirrus.py gcp [...] configurations [-h] --configs CONFIGS [--project-id PROJECT_ID] [--folder-id FOLDER_ID] [--organization-id ORGANIZATION_ID]

optional arguments:
  -h, --help            show this help message and exit
  --configs CONFIGS     in comma-delimited format (no spaces), specify configurations to collect: ['gcp_map', 'rb_map', 'sa_info', 'sa_key_info', 'all_configs']
  --project-id PROJECT_ID
                        in comma-delimited format (no spaces), specify project ID(s) for config collection                                                      
  --folder-id FOLDER_ID
                        in comma-delimited format (no spaces), specify folder ID(s) for config collection                                                       
  --organization-id ORGANIZATION_ID
                        in comma-delimited format (no spaces), specify organization ID for config collection
```

Example of collecting service account information against two projects:
```
./cirrus.py gcp --key-file creds.json configurations --project-id PID1,PID2 --configs sa_details,sa_key_details
```

Example of collecting all role bindings of all resources under one folder:
```
./cirrus.py gcp --key-file creds.json configurations --folder-id FID1 --configs rb_map
```

Example of collecting a resource hierarchy map, role bindings, and service account information against an organization:
```
./cirrus.py gcp --key-file creds.json configurations --organization-id OID --configs all_configs
```

## Troubleshooting<hr>

### VPC Service Controls
**Problem:** VPC Service Control restrictions may hinder the ability to collect configuration or log information. 
Through VPC Service Controls, a service perimeter configured in “Enforced Mode” can restrict access to the 
“Stackdriver Logging API” or “Google Cloud Asset API” services against specific projects.

**Solution:** When scoping a GCP environment, determine if a service perimeter has been configured and if the 
relevant services and project(s) have been restricted. Once identified, speak with an environment admin about 
one of the following solutions:
1. Add the service account identity to an ingress rule allowing access to targeted project(s) and service(s) **(preferred)**
2. Temporarily remove targeted service from “Restricted Services” list **(last resort)**
3. Temporarily remove targeted project from “Projects to protect” list **(last resort)**

## Reference Links<hr>
| **API**                   | **Link**                                                     |
|---------------------------|--------------------------------------------------------------|
| Cloud Logging API         | https://cloud.google.com/logging/docs/reference/v2/rest      |
| Cloud Asset Inventory API | https://cloud.google.com/asset-inventory/docs/reference/rest |

## Appendix A<hr>

### Required Roles

| **Capability**           | **Required Role**                                      |
|--------------------------|--------------------------------------------------------|
| Log collection           | Private Logs Viewer (`roles/logging.privateLogViewer`) |
| Configuration collection | Cloud Asset Viewer (`roles/cloudasset.viewer`)         |

### Required API
Use of the configurations collection capability requires that the Cloud Asset API has been enabled in the project 
where the service account (being used for authentication) was originally created. The API can be enabled via GCloud:

```
gcloud config set project <project_id>
gcloud services enable cloudasset.googleapis.com
gcloud services list --enabled 
```