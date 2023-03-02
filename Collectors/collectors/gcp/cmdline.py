from argparse import ArgumentParser

from .logging_data import SUPPORTED_LOGS
from .asset_inventory import SUPPORTED_CONFIGS
from ..shared.shared_utils import Validators, DEFAULT_LOG_FILE


class Parser:
    def __init__(self):
        # Main parser
        self.parser = ArgumentParser('cirrus.py gcp',
                                     description='Google Cloud Platform forensics collection tool')
        self.subparsers = self.parser.add_subparsers(title='modules', required=True, dest='module',
                                                     metavar='logs, configurations')
        self.parser_log = self.subparsers.add_parser('logs',
                                                     help='collect historical GCP logging data')
        self.parser_config = self.subparsers.add_parser('configurations',
                                                        help='collect current GCP configuration data')
        # Add arguments
        self.add_main_args()
        self.add_log_collection_args()
        self.add_config_collection_args()

    def add_main_args(self):
        self.parser.add_argument('--key-file', type=str, default=None,
                            help="string path to service account JSON key file")
        self.parser.add_argument('--output', type=str,
                            help='output folder (default is folder "output"')
        self.parser.add_argument('--log-file', type=str,
                            help=f"output log file path; default filename: [{DEFAULT_LOG_FILE}]")

    def add_log_collection_args(self):
        self.parser_log.add_argument('--logs', type=str, default=None,
                                     help=f'in comma-delimited format (no spaces), specify logs to collect (enter "all_logs" for all logs): {SUPPORTED_LOGS}')
        self.parser_log.add_argument('--project-id', type=str, default=None,
                                     help='in comma-delimited format (no spaces), specify project ID(s) for log collection')
        self.parser_log.add_argument('--folder-id', type=str, default=None,
                                     help='in comma-delimited format (no spaces), specify folder ID(s) for log collection')
        self.parser_log.add_argument('--organization-id', type=str, default=None,
                                     help='in comma-delimited format (no spaces), specify organization ID for log collection')
        self.parser_log.add_argument('--start-time', type=Validators.time,
                                     help='specify collection start date (RFC3339 format)')  # not required due to --preview
        self.parser_log.add_argument('--end-time', type=Validators.time,
                                     help='specify collection end date (RFC3339 format)')  # not required due to --preview
        self.parser_log.add_argument('--preview', action='store_true',
                                     help='preview logs contained within specified resource ID(s)')
        self.parser_log.add_argument('--custom-logs', type=str, default=None,
                                     help='in comma-delimited format (no spaces), specify custom log(s) for collection')

    def add_config_collection_args(self):
        self.parser_config.add_argument('--configs', required=True, type=str, default=None,
                                        help=f'in comma-delimited format (no spaces), specify configurations to collect: {SUPPORTED_CONFIGS}')
        self.parser_config.add_argument('--project-id', type=str, default=None,
                                        help='in comma-delimited format (no spaces), specify project ID(s) for config collection')
        self.parser_config.add_argument('--folder-id', type=str, default=None,
                                        help='in comma-delimited format (no spaces), specify folder ID(s) for config collection')
        self.parser_config.add_argument('--organization-id', type=str, default=None,
                                        help='in comma-delimited format (no spaces), specify organization ID for config collection')

    @staticmethod
    def validate_log_collection_args(parser, args):
        if args.logs is None and args.preview is None and args.custom_logs:
            parser.error('specify at least one action: [--logs LOG1,LOG2..] or [--custom-logs CL1,CL2..] or [--preview]')
        if args.project_id is None and args.folder_id is None and args.organization_id is None:
            parser.error("specify at least one resource type with the corresponding resource ID(s): "
                         "[--project-id ID1,ID2...] [--folder-id ID1,ID2...] [--organization-id ID]")
        if (args.project_id or args.folder_id or args.organization_id) and args.preview is None and \
                (args.start_time is None or args.end_time is None):
            parser.error('specify start and end timestamps: [--start-time YYYY-MM-DDTHH:MM:SSZ] [--end-time YYYY-MM-DDTHH:MM:SSZ]')


    @staticmethod
    def validate_config_collection_args(parser, args):
        if args.key_file:
            if args.project_id is None and args.folder_id is None and args.organization_id is None:
                parser.error("specify one resource type with the corresponding resource ID(s): "
                             "[--project-id ID1,ID2.. | --folder-id ID1,ID2.. | --organization-id ID]")
        if args.organization_id and (args.project_id or args.folder_id):
            parser.error('specify one resource tier at a time: [--project-id ID1,ID2.. | --folder-id ID1,ID2.. | --organization-id ID]')
        if args.folder_id and (args.organization_id or args.project_id):
            parser.error('specify one resource tier at a time: [--project-id ID1,ID2.. | --folder-id ID1,ID2.. | --organization-id ID]')
        if args.project_id and ("all_configs" in args.configs or "gcp_map" in args.configs):
            parser.error('resource hierarchy mapping only available when given access at the folder or org level')

    @staticmethod
    def user_cli_preview_logs(parser, args):
        # Credential file parse
        credential_file = args.key_file
        Validators.credentials(credential_file)
        # Resource tier parse
        resource_ids = []
        if args.project_id:
            project_ids = [project_id for project_id in args.project_id.split(',')]
            for pid in project_ids:
                resource_ids.append(f'projects/{pid}')
        if args.folder_id:
            folder_ids = [folder_id for folder_id in args.folder_id.split(',')]
            for fid in folder_ids:
                resource_ids.append(f'folders/{fid}')
        if args.organization_id:
            organization_id = [org_id for org_id in args.organization_id.split(',')]
            if len(organization_id) > 1:
                parser.error('specify only a single Organization ID')
            resource_ids.append(f'organizations/{organization_id}')

        return {'credential_file': credential_file,
                'resource_ids': resource_ids}

    @staticmethod
    def user_cli_log_collection(parser, args):
        # Credential file parse
        credential_file = args.key_file
        Validators.credentials(credential_file)
        # Resource tier parse
        resource_ids = []
        if args.project_id:
            project_ids = [project_id for project_id in args.project_id.split(',')]
            for pid in project_ids:
                resource_ids.append(f'projects/{pid}')
        if args.folder_id:
            folder_ids = [folder_id for folder_id in args.folder_id.split(',')]
            for fid in folder_ids:
                resource_ids.append(f'folders/{fid}')
        if args.organization_id:
            organization_id = [org_id for org_id in args.organization_id.split(',')]
            if len(organization_id) > 1:
                parser.error('specify only a single Organization ID')
            resource_ids.append(f'organizations/{organization_id}')
        # Log collection parse
        if args.module == 'logs':
            log_selection = [log for log in args.logs.split(',')]
            for user_specified_log in log_selection:
                if user_specified_log not in SUPPORTED_LOGS:
                    parser.error(f'specified logs should be one of: {str(SUPPORTED_LOGS)}')
        # Custom log parse
        if args.custom_logs:
            custom_selection = [log for log in args.custom_logs.split(',')]
        # Timestamp parse
        start_time = args.start_time
        end_time = args.end_time

        if args.logs and args.custom_logs:
            return {'credential_file': credential_file,
                    'resource_ids': resource_ids,
                    'log_selection': log_selection,
                    'custom_selection': custom_selection,
                    'start_time': start_time,
                    'end_time': end_time}
        elif args.custom_logs and not args.logs:
            return {'credential_file': credential_file,
                    'resource_ids': resource_ids,
                    'custom_selection': custom_selection,
                    'start_time': start_time,
                    'end_time': end_time}
        else:
            return {'credential_file': credential_file,
                    'resource_ids': resource_ids,
                    'log_selection': log_selection,
                    'start_time': start_time,
                    'end_time': end_time}

    @staticmethod
    def user_cli_config_collection(parser, args):
        # Credential file parse
        credential_file = args.key_file
        Validators.credentials(credential_file)
        # Resource tier parse
        resource_ids = []
        if args.project_id:
            project_ids = [project_id for project_id in args.project_id.split(',')]
            for pid in project_ids:
                resource_ids.append(f'projects/{pid}')
        if args.folder_id:
            folder_ids = [folder_id for folder_id in args.folder_id.split(',')]
            for fid in folder_ids:
                resource_ids.append(f'folders/{fid}')
        if args.organization_id:
            organization_id = [org_id for org_id in args.organization_id.split(',')]
            if len(organization_id) > 1:
                parser.error('specify only a single Organization ID')
            resource_ids.append(f'organizations/{organization_id[0]}')
        # Configuration collection parse
        config_selection = [config for config in args.configs.split(',')]
        for user_specified_config in config_selection:
            if user_specified_config not in SUPPORTED_CONFIGS:
                parser.error(f'specified configs should be one of: {str(SUPPORTED_CONFIGS)}')

        return {'credential_file': credential_file,
                'resource_ids': resource_ids,
                'config_selection': config_selection}
