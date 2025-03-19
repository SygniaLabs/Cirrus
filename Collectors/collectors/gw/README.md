# Mirage - Google Workspace Collector

## Capabilities<hr>

Mirage Google Workspace Collector is a command-line tool written in Python that utilizes REST APIs
to collect forensic artifacts from Google Workspace or Cloud Identity for incident response, threat hunting, and
increasing security posture. The script collects configurations, logs, and data.

- **Configuration:** Admin Directory and Gmail users' mailbox settings
- **Logs:** log events captured across Google Workspace and Cloud Identity **(log visibility depends on subscription
  level)**
- **Data:** Gmail messages, threads, and attachments

Visit Sygnia's incident response in Google
Cloud [blog](https://blog.sygnia.co/incident-response-in-google-cloud-forensic-artifacts) to learn more about the
forensic artifacts!

### Admin Directory Configurations

This Admin Directory handler collects the following information:<br>

| Function              | Description                                                                                                                                                                                                                                                                                                               |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Users**             | List of all the users and their configurations.                                                                                                                                                                                                                                                                           | 
| **Deleted Users**     | List of all the deleted users and their configurations.                                                                                                                                                                                                                                                                   | 
| **Domains**           | Information about the domains registered in the account (customer).                                                                                                                                                                                                                                                       | 
| **Asps**              | List all the application-specific passwords (ASPs) per user. Asps are used with applications that do not accept a verification code when logging into the application on certain devices. The ASP access code is used instead of the login and password you commonly use when accessing an application through a browser. | 
| **Chrome OS Devices** | List all Google Chrome devices run on the Chrome OS.                                                                                                                                                                                                                                                                      | 
| **Customers**         | Retrieves information about the current customer account (Google business account).                                                                                                                                                                                                                                       | 
| **Groups**            | List all the groups and their settings (without their members).                                                                                                                                                                                                                                                           | 
| **Members**           | List all the group members of a selected group.                                                                                                                                                                                                                                                                           | 
| **Mobile Devices**    | List Google Workspace Mobile Management devices includes Android, Google Sync, and iOS devices.                                                                                                                                                                                                                           | 
| **Org Units**         | List all the account's organizational units.                                                                                                                                                                                                                                                                              | 
| **Roles**             | List all the roles in the account, without which user is assigned to each role.                                                                                                                                                                                                                                           | 
| **Role Assignments**  | List all the bindings between roles and users.                                                                                                                                                                                                                                                                            | 
| **Tokens**            | List all tokens that were issued by users to 3rd party applications.                                                                                                                                                                                                                                                      |

### Log Events

This Log Events handler collects the following information:<br>

| App                       | Description                                                                                                                                                                                        |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **access_transparency**   | The Google Workspace Access Transparency contain information about different types of Access Transparency activity events.                                                                         |
| **admin**                    | The Admin console application's contain account information about different types of administrator activity events.                                                                                |
| **calendar**                 | The Google Calendar application's contain information about various Calendar activity events.                                                                                                      |
| **chat**                     | The Chat contain information about various Chat activity events.                                                                                                                                   |
| **drive**                    | The Google Drive application's contain information about various Google Drive activity events. The Drive activity report is only available for Google Workspace Business and Enterprise customers. |
| **gcp**                      | The Google Cloud Platform application's contain information about Interaction with the Cloud OS Login API which are related to GCP.                                                                |
| **gplus**                    | The Google+ application's contain information about various Google+ activity events.                                                                                                               |
| **groups**                   | The Google Groups application's contain information about various Groups activity events.                                                                                                          |
| **groups_enterprise**        | The Enterprise Groups contain information about various Enterprise group activity events.                                                                                                          |
| **jamboard**                 | The Jamboard contain information about various Jamboard activity events.                                                                                                                           |
| **login**                    | The Login application's contain account information about different types of Login activity events.                                                                                                |
| **meet**                     | The Meet Audit activity report returns information about different types of Meet Audit activity events.                                                                                            |
| **mobile**                   | The Device Audit activity report returns information about different types of Device Audit activity events.                                                                                        |
| **rules**                    | The Rules activity report returns information about different types of Rules activity events.                                                                                                      |
| **saml**                     | The SAML activity report returns information about different types of SAML activity events.                                                                                                        |
| **token**                    | The Token application's contain account information about different types of Token activity events.                                                                                                |
| **user_accounts**            | The User Accounts application's contain account information about different types of User Accounts activity events.                                                                                |
| **context_aware_access**     | The Context-aware access contain information about users' access denied events due to Context-aware access rules.                                                                                  |
| **chrome**                   | The Chrome contain information about Chrome browser and Chrome OS events.                                                                                                                          |
| **data_studio**              | The Data Studio contain information about various types of Data Studio activity events.                                                                                                            |
| **keep**                     | The Keep application's contain information about various Google Keep activity events. The Keep activity report is only available for Google Workspace Business and Enterprise customers.           |

### Gmail Configurations & Data

The Gmail handler provides deep inspection for users' mailboxes and settings.
To collect the information, the script delegates each user that has Gmail access using the service account credentials.

| Function                 | Description                                                                                                                                                                                                                                                          |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Threads**              | List of all message threads / conversations, including a short snippet of the messages in each thread. The threads can be retrieved based on a query, and to include/exclude threads in the spam/trash folders.                                                      | 
| **Messages**             | List of all message ids and their matching threads. The messages can be retrieved based on a query, and to include/exclude threads in the spam/trash folders.                                                                                                        | 
| **SendAs**              | Lists the send-as aliases for the specified user. The result includes the primary send-as address associated with the account as well as any custom "from" aliases.                                                                                                  | 
| **Delegates**            | Lists the delegates for the specified account. Delegates can read, send, and delete messages, as well as view and add contacts, for the delegator's users.                                                                                                           | 
| **AutoForwarding**      | List auto-forwarding settings for a user.                                                                                                                                                                                                                            | 
| **ForwardingAddresses** | Lists the forwarding addresses for the specified user.                                                                                                                                                                                                               | 
| **IMAP**                 | List the IMAP settings for an account.                                                                                                                                                                                                                               | 
| **POP**                  | POP settings for an account.                                                                                                                                                                                                                                         | 
| **Labels**               | Lists all labels in the user's mailbox. Labels are used to categorize messages and threads within the user's mailbox. The labels often indicate the folder that a message is found in. Listing labels can give an high-level understanding of the mailbox structure. | 
| **Message**              | Obtain a requested message by its message id.                                                                                                                                                                                                                        | 
| **Thread**               | Obtain a requested thread by its thread id.                                                                                                                                                                                                                          | 
| **MessageHistory**      | Lists a certain change to a given mailbox by its history id. Each Messages has its current history id that indicates the last change that was made to it.                                                                                                            |
| **GetAttachment**       | Gets an attachments from a message by the attachment id and the relevant message id.                                                                                                                                                                                 |

## Usage<hr>

### Prerequisites

To execute the script, we need to have a service account key authorized with the appropriate access scopes. APIs also
need to be enabled in the
service account parent project. We recommend using the [Mirage Assistant](../../../Assistant/README.md) script to
facilitate access to a Google Cloud
environment, however the required access scopes and APIs can be found in Appendix A in case manual setup is desired.

### Main Parser

```
usage: mirage.py gw [-h] --key-file KEY_FILE [--output OUTPUT] [--log-file LOG_FILE] [--override-cache] --super-admin SUPER_ADMIN logs, admin_directory, gmail, all ...

Google Workspace and Cloud Identity forensic collection tool

optional arguments:                                                                                                                                                                                               
  -h, --help            show this help message and exit
  --key-file KEY_FILE   string path to service account JSON key file
  --output OUTPUT       output folder (default is folder "output")
  --log-file LOG_FILE   output log file path; default filename: [DEFAULT_LOG_FILE]
  --override-cache      override active_users and groups cache that is created (use this flag in case the investigated environment was changed or once a cache refresh is required)
  --super-admin SUPER_ADMIN
                        the Super Admin privileged user email address being used to gather information on behalf of the service account

modules:
  logs, admin_directory, gmail, all
    admin_directory     administrator information about domains, users, groups, etc.
    logs                logs generated from application and user activity
    gmail               user(s) mailbox configurations and data
    all                 get all information from the account not considered "on-demand" (see README to view all actions that apply)
```

#### Admin Directory Parser

```
usage: mirage.py gw [...] admin_directory [-h] {all,users,deleted_users,domains,asps,chromeosdevices,customers,groups,members,mobiledevices,orgunits,roles,roleAssignments,tokens} ...

positional arguments:
  {all,users,deleted_users,domains,asps,chromeosdevices,customers,groups,members,mobiledevices,orgunits,roles,roleAssignments,tokens}

optional arguments:
  -h, --help            show this help message and exit
```

The subparser "all" includes all the modules with no exceptions. <br>

| Function            | Additional Arguments                                                                                                                                                                                           |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **users**           | X                                                                                                                                                                                                              |
| **deleted_users**   | X                                                                                                                                                                                                              |
| **domains**         | X                                                                                                                                                                                                              |
| **asps**            | --users <br>`The users to acquire information for. applies only for. Multiple values need to be separated by commas (without space). Enter "all" for all users. Example: user1@example.com,user2@example.com`  |
| **chromeosdevices** | X                                                                                                                                                                                                              |
| **customers**       | X                                                                                                                                                                                                              |
| **groups**          | X                                                                                                                                                                                                              |
| **members**         | --groups <br> `The groups to retrieve their members. Multiple values need to be separated by commas (without space). Enter "all" for all groups`                                                               |
| **mobiledevices**   | X                                                                                                                                                                                                              |
| **orgunits**        | X                                                                                                                                                                                                              |
| **roles**           | X                                                                                                                                                                                                              |
| **roleAssignments** | X                                                                                                                                                                                                              |
| **tokens**          | --users <br> `the users to acquire information for. applies only for. Multiple values need to be separated by commas (without space). Enter "all" for all users. Example: user1@example.com,user2@example.com` |
| **all**             | X                                                                                                                                                                                                              |

#### Log Events Parser

```
usage: mirage.py gw [...] logs [-h] --logs LOGS --users USERS [--start-time START_TIME] [--end-time END_TIME]

optional arguments:
  -h, --help            show this help message and exit
  --logs LOGS           in comma-delimited format (no spaces), specify logs (enter "all_logs" for all logs) to collect: ['access_transparency', 'admin', 'calendar', 'chat', 'drive', 'gcp', 'gplus', 'groups', 'groups_enterprise', 'jamboard', 'login', 'meet', 'mobile', 'rules', 'saml', 'token', 'user_accounts', 'context_aware_access', 'chrome', 'data_studio', 'keep']
  --users USERS         in comma-delimited format (no spaces), specify users to acquire information for (enter "all_users" for all users)
  --start-time START_TIME
                        specify collection start date (RFC3339 format)
  --end-time END_TIME   specify collection end date (RFC3339 format)
```

| Function | Additional Arguments                                                                                                                                                                                                                                                                                                               |
|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **logs** | --logs <br> `Enter "all_logs" for all logs. Current supported logs include: ['access_transparency', 'admin', 'calendar', 'chat', 'drive', 'gcp', 'gplus', 'groups','groups_enterprise', 'jamboard', 'login', 'meet', 'mobile', 'rules', 'saml', 'token','user_accounts', 'context_aware_access', 'chrome', 'data_studio', 'keep']` |

#### Gmail Parser

```
usage: mirage.py gw [...] gmail [-h] --users USERS {all,threads,thread,messages,message,message_history,send_as,delegates,auto_forwarding,forwarding_addresses,imap,pop,labels,get_attachment} ...

positional arguments:
  {all,threads,thread,messages,message,message_history,send_as,delegates,auto_forwarding,forwarding_addresses,imap,pop,labels,get_attachment}

optional arguments:
  -h, --help            show this help message and exit
  --users USERS         in comma-delimited format (no spaces), specify users to acquire information for (enter "all_users" for all users)
```

The subparser `all` executes only selected modules as listed below in the table. <br>

| Function             | Additional Arguments                                                                                                                                             | Included in "all" Subparser |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------|
| threads              | --exclude_trash_spam<br> `add this flag to exclude trash and spam from threads search`<br>--query `the query to search for threads. default is with no query.`   | N                           |
| thread               | --id `the requested thread id.`                                                                                                                                  | N                           |
| messages             | --exclude_trash_spam<br> `add this flag to exclude trash and spam from messages search`<br>--query `the query to search for messages. default is with no query.` | N                           |
| message              | --id `the requested message id.`                                                                                                                                 | N                           |
| message_history      | --id `the requested message history id.`                                                                                                                         | N                           |
| send_as              | N/A                                                                                                                                                              | Y                           |
| delegates            | N/A                                                                                                                                                              | Y                           |
| auto_forwarding      | N/A                                                                                                                                                              | Y                           |
| forwarding_addresses | N/A                                                                                                                                                              | Y                           |
| imap                 | N/A                                                                                                                                                              | Y                           |
| pop                  | N/A                                                                                                                                                              | Y                           |
| labels               | N/A                                                                                                                                                              | N                           |

_Note: Threads and Messages can be queries by the Gmail search language as can be found
here: https://support.google.com/mail/answer/7190?hl=en_

#### All Parser

This parser is used in order to run all the features for all users in Admin Directory, Log Events (for all apps),
and selected Gmail settings (as mentioned in the gmail paser section above).

```
usage: mirage.py [...] gw all [-h]

optional arguments:
  -h, --help  show this help message and exit
```

## References Links<hr>

| description                              | link                                                                              |
|------------------------------------------|-----------------------------------------------------------------------------------|
| Admin Directory API                      | https://developers.google.cn/admin-sdk/directory/reference/rest                   |
| Log Events API                           | https://developers.google.com/admin-sdk/reports/reference/rest                    |
| Gmail API #1                             | https://developers.google.com/gmail/api/reference/rest                            |
| Gmail API #2                             | https://www.any-api.com/googleapis_com/gmail/docs/users                           | 
| General Google API objects by module     | https://googleapis.dev/ruby/google-api-client/v0.27.0/Google/Apis.html            |
| GCP list all projects                    | https://cloud.google.com/resource-manager/reference/rest/v1/projects/list         |
| GCP list all service accounts by project | https://cloud.google.com/iam/docs/reference/rest/v1/projects.serviceAccounts/list |
| Cloud Shell Editor                       | https://shell.cloud.google.com/                                                   |
| Gmail Search Langauge                    | https://support.google.com/mail/answer/7190?hl=en                                 |

## Appendix A<hr>

### Required Access Scopes

| **Scope**                                                                | **Description**                                         |
|--------------------------------------------------------------------------|---------------------------------------------------------|
| https://www.googleapis.com/auth/admin.directory.user.readonly            | See info about users on your domain |
| https://www.googleapis.com/auth/admin.directory.domain.readonly          | View domains related to your customers |
| https://www.googleapis.com/auth/admin.directory.user.security            | Manage data access permissions for users on your domain |
| https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly | View your ChromeOS devices' metadata |
| https://www.googleapis.com/auth/admin.directory.customer.readonly        | View customer related information |
| https://www.googleapis.com/auth/admin.directory.group.readonly           | View groups on your domain |
| https://www.googleapis.com/auth/admin.directory.device.mobile.readonly   | View your mobile devices' metadata |
| https://www.googleapis.com/auth/admin.directory.orgunit.readonly         | View organization units on your domain |
| https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly  | View delegated admin roles for your domain|
| https://www.googleapis.com/auth/admin.reports.audit.readonly             | View audit reports for your Google Workspace domain |
| https://www.googleapis.com/auth/admin.reports.usage.readonly             | View usage reports for your Google Workspace domain |
| https://www.googleapis.com/auth/gmail.readonly                           | View your email messages and settings |

### Required APIs

Use of the Mirage Workspace Collector requires that the Admin SDK and Gmail APIs are enabled in the service account
parent project.
The API can be enabled via GCloud:

```
gcloud config set project <project_id>
gcloud services enable admin.googleapis.com          
gcloud services enable gmail.googleapis.com
gcloud services list --enabled 
```
