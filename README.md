# Mirage - Google Cloud Forensic Collection

![mirage_image](./mirage.jpg)

## Overview<hr>

Mirage is a command-line tool written in Python to facilitate environment access and evidence collection across
Google Cloud. Mirage has been designed to support incident response and threat hunting operations. Sygnia
created Mirage and an associated blog
series ([Foundations](https://blog.sygnia.co/incident-response-in-google-cloud-foundations)
& [Forensic Artifacts](https://blog.sygnia.co/incident-response-in-google-cloud-forensic-artifacts)) to help solve gaps
with incident response in Google Cloud.

## Capabilities<hr>

Mirage is composed of two scripts:

1. **Assistant**: automate Google Cloud access setup and cleanup
2. **Collector**: collect log, configuration, and user data

The *Assistant* script is responsible for automating access prerequisites to
a Google Cloud environment in preparation for evidence collection by the *Collector*. The Assistant script is
built for execution in Google Cloud Shell, while the Collector script can be executed from any terminal. The Collector
script utilizes a service account key file to authenticate to a Google Cloud environment, which can be generated through
the Assistant script or manual creation.

### Assistant

To prepare a Google Cloud environment for evidence collection,
reference [Assistant documentation](./Assistant/README.md).

### Collector

To collect evidence from Google Cloud, reference [Collector documentation](./Collectors/README.md).

## Authors & Contributors<hr>

### Authors

- Itay Angi (@NG-Syg)
- Wesley Guerra (@wrguerra)

### Contributors

- @yogevyuval - Provided code review.
- @yuvalmarciano - Provided code review.
