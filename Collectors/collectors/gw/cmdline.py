from argparse import ArgumentParser

from .log_events import ALL_APPLICATIONS
from ..shared.shared_utils import DEFAULT_LOG_FILE, Validators


class Parser:
    def __init__(self):
        # Main parser
        self.parser = ArgumentParser('cirrus.py gw',
                                     description='Google Workspace and Cloud Identity forensic collection tool')
        self.subparsers = self.parser.add_subparsers(title='modules', required=True, dest='module',
                                                     metavar='logs, admin_directory, gmail, all')
        self.admin_directory_parser = self.subparsers.add_parser('admin_directory',
                                                                 help='administrator information about domains, users, groups, etc.')
        self.log_events_parser = self.subparsers.add_parser('logs',
                                                            help='logs generated from application and user activity')
        self.gmail_parser = self.subparsers.add_parser('gmail',
                                                       help='user(s) mailbox configurations and data')
        self.all_parser = self.subparsers.add_parser('all',
                                                     help='get all information from the account not considered '
                                                          '"on-demand" (see README to view all actions that apply)')

        # Admin directory subparsers
        self.admin_directory_subparsers = self.admin_directory_parser.add_subparsers(dest='action', required=True)
        self.admin_directory_all_parser = self.admin_directory_subparsers.add_parser('all')
        self.admin_directory_users_parser = self.admin_directory_subparsers.add_parser('users')
        self.admin_directory_deleted_users_parser = self.admin_directory_subparsers.add_parser('deleted_users')
        self.admin_directory_domains_parser = self.admin_directory_subparsers.add_parser('domains')
        self.admin_directory_asps_parser = self.admin_directory_subparsers.add_parser('asps')
        self.admin_directory_chromeosdevices_parser = self.admin_directory_subparsers.add_parser('chromeosdevices')
        self.admin_directory_customers_parser = self.admin_directory_subparsers.add_parser('customers')
        self.admin_directory_groups_parser = self.admin_directory_subparsers.add_parser('groups')
        self.admin_directory_members_parser = self.admin_directory_subparsers.add_parser('members')
        self.admin_directory_mobiledevices_parser = self.admin_directory_subparsers.add_parser('mobiledevices')
        self.admin_directory_orgunits_parser = self.admin_directory_subparsers.add_parser('orgunits')
        self.admin_directory_roles_parser = self.admin_directory_subparsers.add_parser('roles')
        self.admin_directory_roleAssignments_parser = self.admin_directory_subparsers.add_parser('roleAssignments')
        self.admin_directory_tokens_parser = self.admin_directory_subparsers.add_parser('tokens')

        # Gmail subparsers
        self.gmail_subparsers = self.gmail_parser.add_subparsers(dest='action', required=True)
        self.gmail_all_parser = self.gmail_subparsers.add_parser('all')
        self.gmail_threads_parser = self.gmail_subparsers.add_parser('threads')
        self.gmail_thread_parser = self.gmail_subparsers.add_parser('thread')
        self.gmail_messages_parser = self.gmail_subparsers.add_parser('messages')
        self.gmail_message_parser = self.gmail_subparsers.add_parser('message')
        self.gmail_message_history_parser = self.gmail_subparsers.add_parser('message_history')
        self.gmail_send_as_parser = self.gmail_subparsers.add_parser('send_as')
        self.gmail_delegates_parser = self.gmail_subparsers.add_parser('delegates')
        self.gmail_auto_forwarding_parser = self.gmail_subparsers.add_parser('auto_forwarding')
        self.gmail_forwarding_addresses_parser = self.gmail_subparsers.add_parser('forwarding_addresses')
        self.gmail_imap_parser = self.gmail_subparsers.add_parser('imap')
        self.gmail_pop_parser = self.gmail_subparsers.add_parser('pop')
        self.gmail_labels_parser = self.gmail_subparsers.add_parser('labels')
        self.gmail_get_attachment_parser = self.gmail_subparsers.add_parser('get_attachment')

        # Add arguments
        self.add_main_args()
        self.add_admin_directory_args()
        self.add_log_events_args()
        self.add_gmail_args()

    def add_main_args(self):
        self.parser.add_argument('--key-file', type=str, required=True, default=None,
                                 help="string path to service account JSON key file")
        self.parser.add_argument('--output', type=str,
                                 help='output folder (default is folder "output")')
        self.parser.add_argument('--log-file', type=str,
                                 help=f"output log file path; default filename: [{DEFAULT_LOG_FILE}]")
        self.parser.add_argument('--override-cache', action='store_true',
                                 help='override active_users and groups cache that is created (use this flag in case '
                                      'the investigated environment was changed or once a cache refresh is required)')
        self.parser.add_argument('--super-admin', type=str, required=True,
                                 help='the Super Admin privileged user email address being used to gather '
                                      'information on behalf of the service account')

    def add_admin_directory_args(self):
        self.admin_directory_asps_parser.add_argument('--users', type=str, required=True,
                                                      help='in comma-delimited format (no spaces), specify users to '
                                                           'acquire information for (enter "all_users" for all users)')
        self.admin_directory_members_parser.add_argument('--groups', type=str, required=True,
                                                         help='in comma-delimited format (no spaces), specify groups to acquire '
                                                              'their members (enter "all_groups" for all groups)')
        self.admin_directory_tokens_parser.add_argument('--users', type=str, required=True,
                                                        help='in comma-delimited format (no spaces), specify users to '
                                                             'acquire information for (enter "all_users" for all users)')

    def add_log_events_args(self):
        self.log_events_parser.add_argument('--logs', required=True, type=str,
                                            help=f'in comma-delimited format (no spaces), specify logs (enter '
                                                 f'"all_logs" for all logs) to collect: {ALL_APPLICATIONS}')
        self.log_events_parser.add_argument('--users', required=True, type=str,
                                            help='in comma-delimited format (no spaces), specify users to acquire '
                                                 'information for (enter "all_users" for all users)')
        self.log_events_parser.add_argument('--start-time', type=Validators.time,
                                            help='specify collection start date (RFC3339 format)')
        self.log_events_parser.add_argument('--end-time', type=Validators.time,
                                            help='specify collection end date (RFC3339 format)')

    def add_gmail_args(self):
        self.gmail_parser.add_argument('--users', type=str, required=True,
                                       help='in comma-delimited format (no spaces), specify users to acquire '
                                            'information for (enter "all_users" for all users)')
        self.gmail_threads_parser.add_argument('--exclude-trash-spam', action='store_true',
                                               help='add this flag to exclude trash and spam from threads search')
        self.gmail_threads_parser.add_argument('--query', type=str,
                                               help='the query to search for threads (default is with no query)')
        self.gmail_thread_parser.add_argument('--id', required=True, type=str,
                                              help='the requested thread id')
        self.gmail_messages_parser.add_argument('--exclude-trash-spam', action='store_true',
                                                help='add this flag to exclude trash and spam from messages search')
        self.gmail_messages_parser.add_argument('--query', type=str,
                                                help='the query to search for messages (default is with no query)')
        self.gmail_message_parser.add_argument('--id', required=True, type=str,
                                               help='the requested message id')
        self.gmail_message_history_parser.add_argument('--id', required=True, type=str,
                                                       help='the requested message history id')
        self.gmail_get_attachment_parser.add_argument('--message-id', required=True, type=str,
                                                      help='the requested message id containing the attachment')
        self.gmail_get_attachment_parser.add_argument('--attachment-id', required=True, type=str,
                                                      help='the attachment id')
