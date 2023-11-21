import logging
import os

from googleapiclient.discovery import build

from ..shared.module_handler import ModuleHandler
from ..shared.shared_utils import DEFAULT_CACHE_FOLDER, MemoryCache

DEFAULT_USERS_FILE = os.path.join(DEFAULT_CACHE_FOLDER,
                                  'active_users.tmp')  # Active users are non suspended users that have logged in at least once
DEFAULT_GROUPS_FILE = os.path.join(DEFAULT_CACHE_FOLDER, 'groups.tmp')
DEFAULT_MAILBOX_SETUP_FILE = os.path.join(DEFAULT_CACHE_FOLDER,
                                          'gmail_users.tmp')  # Contains all users that have their mailbox
# setup enables (and has Gmail access). This file keeps updating every time a new user is queries for its mailboxsetup settings.

CUSTOMER_DEFAULT_PARAMS = {'customer': 'my_customer'}
NO_LOGIN_TIME = '1970-01-01T00:00:00.000Z'


class AdminDirectory(ModuleHandler):
    def __init__(self, creds, file_handler):
        super().__init__(creds, file_handler, build('admin', 'directory_v1', credentials=creds, cache=MemoryCache()),
                         'admin_directory')

    def get_all_active_users(self, override=False, mailbox_setup=False):
        console = logging.getLogger(__name__)
        if not os.path.exists(DEFAULT_USERS_FILE) or override:
            if override and os.path.exists(DEFAULT_USERS_FILE):
                console.info('Overriding cache')
            logging.info("Creating temp file with all active users (non-suspended + have logged in)")
            results = self._get_raw_active_users()
            if type(results[0]) == list:  # more than one page
                users = [user_data['primaryEmail'].lower() for page_results in results for user_data in page_results
                         if user_data['lastLoginTime'] != NO_LOGIN_TIME]
            else:
                users = [user_data['primaryEmail'].lower() for user_data in results
                         if user_data['lastLoginTime'] != NO_LOGIN_TIME]

            # If "mailbox_setup" collection was requested, get all users that have access to Gmail
            if mailbox_setup:
                self._handle_gmail_users(results)
            with open(DEFAULT_USERS_FILE, 'w') as f:
                for user in users:
                    f.write(str(user) + '\n')
        else:
            logging.info("Loading users from temp file ...")
            users = []
            with open(DEFAULT_USERS_FILE, 'r') as f:
                for line in f:
                    users.append(line.rstrip())
            console.info("Users loaded from temp file")
        return users

    def get_all_groups(self, override=False):
        if not os.path.exists(DEFAULT_GROUPS_FILE) or override:
            if override and os.path.exists(DEFAULT_GROUPS_FILE):
                logging.info('Overriding cache')
            logging.info("Creating temp file with all the groups")
            results = self.list_action(function='groups',
                                       params=CUSTOMER_DEFAULT_PARAMS,
                                       inner_object='groups', add_to_log=False)
            if type(results[0]) == list:  # more than one page
                groups = [group_data['email'].lower() for page_results in results for group_data in page_results]
            else:  # one page
                groups = [group_data['email'].lower() for group_data in results]
            with open(DEFAULT_GROUPS_FILE, 'w') as f:
                for group in groups:
                    f.write(str(group) + '\n')
        else:
            logging.info("Loading groups from temp file")
            groups = []
            with open(DEFAULT_GROUPS_FILE, 'r') as f:
                for line in f:
                    groups.append(line.rstrip())
        logging.info(f"Working with {len(groups)} groups. First group is: {groups[0] if len(groups) > 0 else 'None'}")
        return groups

    def get_mailbox_enabled_users(self) -> list:
        """
        Gets all uses with mailbox enabled, save them to temp file and returns them.
        Use this function if the main script worked with specific users, hence not all users were collected
        with their mailbox enables settings.
        """
        results = self._get_raw_active_users()
        return self._handle_gmail_users(results=results)

    def _handle_gmail_users(self, results):
        logging.info('Gathering all active users with mailbox enabled.')
        if type(results[0]) == list:  # more than one page
            gmail_users = [user_data['primaryEmail'].lower() for page_results in results for user_data in page_results
                           if user_data['lastLoginTime'] != NO_LOGIN_TIME and user_data['isMailboxSetup']]
        else:  # one page
            gmail_users = [user_data['primaryEmail'].lower() for user_data in results
                           if user_data['lastLoginTime'] != NO_LOGIN_TIME and user_data['isMailboxSetup']]

        if len(gmail_users) > 0:
            with open(DEFAULT_MAILBOX_SETUP_FILE, 'w') as f:
                for gmail_user in gmail_users:
                    f.write(str(gmail_user) + '\n')
        logging.info(f'Collected {len(gmail_users)} active users with mailbox enabled.')
        return gmail_users

    def _get_raw_active_users(self):
        params = CUSTOMER_DEFAULT_PARAMS.copy()
        params['query'] = 'isSuspended=false'
        results = self.list_action(function='users', params=CUSTOMER_DEFAULT_PARAMS,
                                   inner_object='users', add_to_log=False)
        return results
