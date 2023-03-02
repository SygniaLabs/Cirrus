from googleapiclient.discovery import build

from ..shared.module_handler import ModuleHandler
from ..shared.shared_utils import MemoryCache

ALL_APPLICATIONS = ['access_transparency', 'admin', 'calendar', 'chat', 'drive', 'gcp', 'gplus', 'groups',
                    'groups_enterprise', 'jamboard', 'login', 'meet', 'mobile', 'rules', 'saml', 'token',
                    'user_accounts', 'context_aware_access', 'chrome', 'data_studio', 'keep']


class LogEvents(ModuleHandler):
    def __init__(self, creds, file_handler):
        super().__init__(creds, file_handler, build('admin', 'reports_v1', credentials=creds, cache=MemoryCache()), 'log_events')

    @staticmethod
    def check_apps(apps: list):
        for app in apps:
            if app not in ALL_APPLICATIONS:
                return False
        return True
