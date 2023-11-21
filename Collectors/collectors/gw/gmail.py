import logging
import os

from .admin_directory import DEFAULT_MAILBOX_SETUP_FILE, AdminDirectory
from ..shared.module_handler import ModuleHandler


class Gmail(ModuleHandler):
    def __init__(self, creds, file_handler, service=None):
        super().__init__(creds=creds, file_handler=file_handler, service=service, module='gmail')

    @staticmethod
    def get_relevant_gmail_users(admin_directory_handler: AdminDirectory, users: list, override=False):
        logging.info('Getting relevant gmail users')
        gmail_users = []
        # if mailbox_setup_enabled was already gathered by getting all users
        if os.path.exists(DEFAULT_MAILBOX_SETUP_FILE) and not override:
            logging.info('Retrieving from cache file')
            with open(DEFAULT_MAILBOX_SETUP_FILE, 'r') as f:
                for line in f:
                    gmail_users.append(line.rstrip())
        # else => gather mailbox_setup_enabled users with admin_directory handler
        else:
            if override:
                logging.info('overriding cache file')
            else:
                logging.info('No cache file found, getting mailbox settings for all users')
            gmail_users = admin_directory_handler.get_mailbox_enabled_users()

        # match given users list to gmail users and give the in
        logging.info(f'Got {len(users)} total users, retrieved {len(gmail_users)} gmail users.')
        relevant_gmail_users = list(set(users) & set(gmail_users))
        logging.info(f'Got {len(relevant_gmail_users)} users after comparison.')
        return relevant_gmail_users
