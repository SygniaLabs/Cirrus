import logging
import os
import sys
import time
from sys import exit

from google.oauth2.service_account import Credentials

from .admin_directory import AdminDirectory, DEFAULT_CACHE_FOLDER
from .cmdline import Parser
from .gmail import Gmail
from .log_events import LogEvents, ALL_APPLICATIONS
from ..shared.shared_utils import FileHandler, DEFAULT_OUTPUT_FOLDER

SCOPES = ['https://www.googleapis.com/auth/admin.directory.user.readonly',
          'https://www.googleapis.com/auth/admin.directory.domain.readonly',
          'https://www.googleapis.com/auth/admin.directory.user.security',
          'https://www.googleapis.com/auth/admin.directory.device.chromeos.readonly',
          'https://www.googleapis.com/auth/admin.directory.customer.readonly',
          'https://www.googleapis.com/auth/admin.directory.group.readonly',
          'https://www.googleapis.com/auth/admin.directory.device.mobile.readonly',
          'https://www.googleapis.com/auth/admin.directory.orgunit.readonly',
          'https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly',
          'https://www.googleapis.com/auth/admin.reports.audit.readonly',
          'https://www.googleapis.com/auth/admin.reports.usage.readonly',
          'https://www.googleapis.com/auth/gmail.readonly']
SUPPORTED_MODULES = ['admin_directory', 'logs', 'gmail']
CUSTOMER_ID_DEFAULT_PARAMS = {'customerId': 'my_customer'}
CUSTOMER_DEFAULT_PARAMS = {'customer': 'my_customer'}

BG = "\u001b[32;1m"  # Bright green
RR = "\u001b[0m"  # Reset

log_file = None


def main():
    """Parses the command line arguments and executes the relevant function to execute the relevant API queries"""
    global log_file
    file_handler = None
    try:
        # Parse arguments
        parser = Parser()
        args = parser.parser.parse_args(sys.argv[2:])
        module = args.module
        cmdline = " ".join(sys.argv)
        query = ''

        include_trash_spam = not args.exclude_trash_spam if 'exclude_trash_spam' in args else None
        if 'query' in args:
            query = args.query
        if 'users' in args and args.users != 'all_users':
            users = [x.lower() for x in args.users.split(',')]
        if 'groups' in args and args.groups != 'all_groups':
            groups = [x.lower() for x in args.groups.split(',')]

        # Create file handler (for output folder and log file)
        file_handler = FileHandler(folder=args.output, log_file=args.log_file, cmdline=cmdline)
        log_file = file_handler.log_file

        # Basic validations
        if not os.access(args.key_file, os.R_OK):
            exit('cannot find/access the secret file location on disk. Exiting.')

        # Generate creds
        try:
            source_credentials = (Credentials.from_service_account_file(args.key_file, scopes=SCOPES))
        except:
            exit('unable to generate credentials from service account. Exiting.')
        try:
            delegated_credentials = source_credentials.with_subject(args.super_admin)
        except:
            exit('unable to delegate credentials from service account to the Super Admin privileged user. Exiting.')

        # Applying action
        if module == 'logs':
            action = None  # currently log events contains only one predefined action
        elif module == 'all':
            action = 'all'
        else:
            action = args.action

        # Getting all users/groups in case none were asked for
        # This section is executed in case no users/groups were given while they are required for the requested action
        # This section also checks whether Gmail settings were requested to gather all "mailbox_setup enabled users"
        mailbox_setup_required = (module == 'all' or module == 'gmail')
        all_users_flag = (module == 'all' or
                          (module == 'admin_directory' and action == 'all') or
                          ('users' in args and args.users == 'all_users'))
        all_groups_flag = (module == 'all' or
                           (module == 'admin_directory' and
                            (action == 'all' or ('groups' in args and args.groups == 'all_groups'))))
        if all_groups_flag or all_users_flag:
            admin_directory_handler = AdminDirectory(creds=delegated_credentials, file_handler=file_handler)
            # Create Cache folder if it doesn't exist
            if not os.path.exists(DEFAULT_CACHE_FOLDER):
                os.makedirs(DEFAULT_CACHE_FOLDER)
            if all_users_flag:
                # Gmail does not require getting all users
                if mailbox_setup_required:
                    users = admin_directory_handler.get_all_active_users(override=args.override_cache,
                                                                         mailbox_setup=mailbox_setup_required)
                else:
                    users = admin_directory_handler.get_all_active_users(override=args.override_cache)
                if len(users) == 0:
                    exit('could not retrieved users to work with. Exiting.')
            if all_groups_flag:
                groups = admin_directory_handler.get_all_groups(override=args.override_cache)

        # Script start time
        script_start_time = time.time()

        # Admin directory module
        if module == 'admin_directory' or module == 'all':
            admin_directory_handler = AdminDirectory(creds=delegated_credentials, file_handler=file_handler)
            print(f"{BG}Starting to collect configurations from Admin Directory{RR}")
            if action == 'users' or action == 'all':
                admin_directory_handler.list_action(function='users', params=CUSTOMER_DEFAULT_PARAMS,
                                                    inner_object='users')
            if action == 'deleted_users' or action == 'all':
                admin_directory_handler.list_action(function='users', params={'customer': 'my_customer',
                                                                              'showDeleted': True},
                                                    inner_object='users', documented_item='deleted')

            if action == 'domains' or action == 'all':
                admin_directory_handler.list_action(function='domains', params=CUSTOMER_DEFAULT_PARAMS,
                                                    inner_object='domains')
            if action == 'asps' or action == 'all':
                admin_directory_handler.list_action_by_values(function='asps', params={'userKey': None},
                                                              list_items=users,
                                                              inner_object='items', dynamic_key_param='userKey',
                                                              item_as_data=True)
            if action == 'chromeosdevices' or action == 'all':
                admin_directory_handler.list_action(function='chromeosdevices',
                                                    params=CUSTOMER_ID_DEFAULT_PARAMS,
                                                    inner_object='chromeosdevices')
            if action == 'customers' or action == 'all':
                admin_directory_handler.list_action(function='customers',
                                                    params={'customerKey': 'my_customer'},
                                                    is_get_action=True)
            if action == 'groups' or action == 'all':
                admin_directory_handler.list_action(function='groups',
                                                    params=CUSTOMER_DEFAULT_PARAMS,
                                                    inner_object='groups')
            if action == 'members' or action == 'all':
                admin_directory_handler.list_action_by_values(function='members',
                                                              params={'groupKey': None,
                                                                      'includeDerivedMembership': True},
                                                              list_items=groups,
                                                              inner_object='members', dynamic_key_param='groupKey',
                                                              item_as_data=True)
            if action == 'mobiledevices' or action == 'all':
                admin_directory_handler.list_action(function='mobiledevices',
                                                    params=CUSTOMER_ID_DEFAULT_PARAMS,
                                                    inner_object='mobiledevices')
            if action == 'orgunits' or action == 'all':
                admin_directory_handler.list_action(function='orgunits',
                                                    params=CUSTOMER_ID_DEFAULT_PARAMS,
                                                    inner_object='organizationUnits')
            if action == 'roles' or action == 'all':
                admin_directory_handler.list_action(function='roles',
                                                    params=CUSTOMER_DEFAULT_PARAMS,
                                                    inner_object='items')
            if action == 'roleAssignments' or action == 'all':
                admin_directory_handler.list_action(function='roleAssignments',
                                                    params=CUSTOMER_DEFAULT_PARAMS,
                                                    inner_object='items')
            if action == 'tokens' or action == 'all':
                admin_directory_handler.list_action_by_values(function='tokens',
                                                              params={'userKey': None},
                                                              list_items=users,
                                                              inner_object='items', dynamic_key_param='userKey',
                                                              item_as_data=True)
            admin_directory_handler.close()

        # Log events module
        if module == 'logs' or module == 'all':
            log_events_handler = LogEvents(creds=delegated_credentials, file_handler=file_handler)
            print(f"{BG}Starting to collect logs from Google Log Events{RR}")
            if 'logs' in args and args.logs != "all_logs":
                apps = [x.lower() for x in args.logs.split(',')]
                formatted_logs = apps
                if not log_events_handler.check_apps(apps):
                    raise Exception(f'logs should be one of: {str(ALL_APPLICATIONS)}')
            else:
                apps = ALL_APPLICATIONS
                formatted_logs = ["all"]
            formatted_log_selection = [word.replace("_", " ").title() for word in formatted_logs]
            final_format_logs = ', '.join(formatted_log_selection)
            params = {'applicationName': None}
            if 'start_time' in args:
                params['startTime'] = args.start_time
            if 'end_time' in args:
                params['endTime'] = args.end_time

            if all_users_flag:  # short version to get information for all users instead iterating them

                params['userKey'] = 'all'
                logging.info('Beginning log collection for activity across the organization ...')
                log_events_handler.list_action_by_values(function='activities',
                                                         params=params,
                                                         list_items=apps,
                                                         item_as_data=True,
                                                         dynamic_key_param='applicationName',
                                                         inner_object='items', results_only=True)


            else:  # specific users were supplied
                for user in users:
                    tmp_params = params.copy()
                    tmp_params['userKey'] = user
                    try:
                        logging.info(f'Collecting [{final_format_logs}] log events for user ...')
                        log_events_handler.list_action_by_values(function='activities',
                                                                 params=tmp_params,
                                                                 list_items=apps,
                                                                 item_as_data=True,
                                                                 dynamic_key_param='applicationName',
                                                                 inner_object='items', results_only=True,
                                                                 filename_additions=user)


                    except:
                        logging.info(f'Error in collecting log events for user {user}!')

            log_events_handler.close()

        # Gmail module
        if module == 'gmail' or module == 'all':
            gmail_handler = Gmail(creds=source_credentials, file_handler=file_handler)
            admin_directory_handler = AdminDirectory(creds=delegated_credentials, file_handler=file_handler)
            # Create Cache folder if it doesn't exist
            os.makedirs(DEFAULT_CACHE_FOLDER, exist_ok=True)
            gmail_users = gmail_handler.get_relevant_gmail_users(admin_directory_handler=admin_directory_handler,
                                                                 users=users, override=args.override_cache)
            print(f"{BG}Starting to collect configurations/data from Gmail{RR}")
            if action == 'threads':
                gmail_handler.list_action_by_values(function='threads',
                                                    base_functions=['users'],
                                                    params={'includeSpamTrash': include_trash_spam,
                                                            'q': query, 'userId': 'me'},
                                                    list_items=gmail_users,
                                                    main_key='user',
                                                    inner_object='threads',
                                                    delegate_users=True)
            if action == 'messages':
                gmail_handler.list_action_by_values(function='messages',
                                                    base_functions=['users'],
                                                    params={'includeSpamTrash': include_trash_spam,
                                                            'q': query, 'userId': 'me'},
                                                    list_items=gmail_users,
                                                    main_key='user',
                                                    inner_object='messages',
                                                    delegate_users=True)
            if action == 'send_as' or action == 'all':
                gmail_handler.list_action_by_values(function='sendAs',
                                                    base_functions=['users', 'settings'],
                                                    params={'userId': 'me'},
                                                    list_items=gmail_users,
                                                    main_key='user',
                                                    inner_object='sendAs',
                                                    delegate_users=True)
            if action == 'delegates' or action == 'all':
                gmail_handler.list_action_by_values(function='delegates',
                                                    base_functions=['users', 'settings'],
                                                    params={'userId': 'me'},
                                                    list_items=gmail_users,
                                                    main_key='user',
                                                    inner_object='delegates',
                                                    delegate_users=True)
            if action == 'auto_forwarding' or action == 'all':
                gmail_handler.list_action_by_values(function='getAutoForwarding',
                                                    base_functions=['users', 'settings'],
                                                    params={'userId': 'me'},
                                                    list_items=gmail_users,
                                                    main_key='user',
                                                    delegate_users=True,
                                                    is_no_action=True)
            if action == 'forwarding_addresses' or action == 'all':
                gmail_handler.list_action_by_values(function='forwardingAddresses',
                                                    base_functions=['users', 'settings'],
                                                    params={'userId': 'me'},
                                                    list_items=gmail_users,
                                                    main_key='user',
                                                    inner_object='forwardingAddresses',
                                                    delegate_users=True)
            if action == 'imap' or action == 'all':
                gmail_handler.list_action_by_values(function='getImap',
                                                    base_functions=['users', 'settings'],
                                                    params={'userId': 'me'},
                                                    list_items=gmail_users,
                                                    main_key='user',
                                                    delegate_users=True,
                                                    is_no_action=True)
            if action == 'pop' or action == 'all':
                gmail_handler.list_action_by_values(function='getPop',
                                                    base_functions=['users', 'settings'],
                                                    params={'userId': 'me'},
                                                    list_items=gmail_users,
                                                    main_key='user',
                                                    delegate_users=True,
                                                    is_no_action=True)
            if action == 'labels':
                gmail_handler.list_action_by_values(function='labels',
                                                    base_functions=['users'],
                                                    params={'userId': 'me'},
                                                    list_items=gmail_users,
                                                    main_key='user',
                                                    inner_object='labels',
                                                    delegate_users=True)
            if action == 'message' and 'id' in args:
                gmail_handler.list_action_by_values(function='messages',
                                                    base_functions=['users'],
                                                    params={'userId': 'me', 'id': args.id},
                                                    list_items=gmail_users,
                                                    main_key='user',
                                                    is_get_action=True,
                                                    delegate_users=True,
                                                    filename_additions=args.id)
            if action == 'thread' and 'id' in args:
                gmail_handler.list_action_by_values(function='threads',
                                                    base_functions=['users'],
                                                    params={'userId': 'me', 'id': args.id},
                                                    list_items=gmail_users,
                                                    main_key='user',
                                                    is_get_action=True,
                                                    delegate_users=True,
                                                    filename_additions=args.id)
            if action == 'message_history' and 'id' in args:
                gmail_handler.list_action_by_values(function='history',
                                                    base_functions=['users'],
                                                    params={'userId': 'me',
                                                            'startHistoryId': int(args.id) - 1},
                                                    list_items=gmail_users,
                                                    main_key='user',
                                                    inner_object='history',
                                                    delegate_users=True,
                                                    filename_additions=args.id)
            if action == 'get_attachment' and args.message_id and args.attachment_id:
                gmail_handler.list_action_by_values(function='attachments',
                                                    base_functions=['users', 'messages'],
                                                    params={'userId': 'me',
                                                            'messageId': args.message_id,
                                                            'id': args.attachment_id},
                                                    list_items=gmail_users,
                                                    main_key='user',
                                                    is_get_action=True,
                                                    delegate_users=True,
                                                    filename_additions=args.message_id + "_attachment")
            gmail_handler.close()

        print(f"{BG}Results are tracked in [{DEFAULT_OUTPUT_FOLDER}]{RR}")
        print(f"{BG}More detailed results can be found at [{log_file}]{RR}")
        file_handler.append_log(f'Finished in {(time.time() - script_start_time) / 60} minutes')

    # General exception catcher
    except (Exception, SystemExit) as e:
        if str(e) != '0':  # Good system exit
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            err_msg = f'ERROR => {exc_type.__name__}: {str(exc_obj)}, line {exc_tb.tb_lineno}, in file {fname}.'
            if log_file is not None and os.access(log_file, os.R_OK):
                file_handler.append_log(data=err_msg)
                logging.info(f'ERROR! please see log {log_file}')
            else:  # in case log file can't be accesses => print to stdout
                logging.info(err_msg)


if __name__ == '__main__':
    main()
