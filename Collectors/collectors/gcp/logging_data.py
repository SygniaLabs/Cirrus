import logging
import os
import time

from googleapiclient.discovery import build
from tabulate import tabulate

from ..shared.module_handler import ModuleHandler
from ..shared.shared_utils import DEFAULT_OUTPUT_FOLDER, MemoryCache

LOG_PREVIEW_TRACKER = os.path.join(DEFAULT_OUTPUT_FOLDER, "log_preview")

SUPPORTED_LOGS = ['admin_activity', 'data_access', 'policy_denied', 'access_transparency', 'system_event',
                  'vpc_flow', 'gce_data', 'dns', 'fw_rules', 'load_balancer', 'k8s', 'cloud_sql', 'all_logs']

LOG_MAPPING = {
    "admin_activity": "%2Factivity",
    "data_access": "%2Fdata_access",
    "policy_denied": "%2Fpolicy",
    "system_event": "%2Fsystem_event",
    "access_transparency": "%2Faccess_transparency",
    "vpc_flow": "%2Fvpc_flows",
    "dns": "%2Fdns_queries",
    "fw_rules": "%2Ffirewall",
    "k8s": ["kube", "gke"],
    "gce_data": ["logs/GCE", "logs/OSConfig"],
    "load_balancer": "logs/requests",
    "cloud_sql": ["%2Fmysql.err", "%2Fmysql-slow.log", "%2Fmysql-general.log", "%2Freplication-setup.log",
                  "%2Freplication-status.log", "%2Fmysql-upgrade.log", "%2Fpostgres.log", "%2Fpostgres-audit.log",
                  "%2Fsqlserver.err", "%2Fsqlagent.out", "%2Foperationdetails.log", "%2Fpostgres-upgrade.log"]
}


class LogManagement(ModuleHandler):
    def __init__(self, creds, file_handler):
        super().__init__(creds, file_handler, build('logging', 'v2', credentials=creds, cache=MemoryCache()),
                         'log_collection')

    @staticmethod
    def check_logs(logs: list):
        return all(log in SUPPORTED_LOGS for log in logs)

    @staticmethod
    def collect_logs(handler, resource_ids: list = None, log_selection: list = None,
                     custom_selection: list = None, start_time: str = None, end_time: str = None):
        """Used to gather historical logs against specified project(s), folder(s), and/or organization"""

        for rid in resource_ids:

            # Formatting resources and specified logs for the "filter" portion of the API request body
            if log_selection is not None:
                if "all_logs" in log_selection:
                    final_format_logs = "logName : *"
                else:
                    formatted_log_list = []
                    for log in log_selection:
                        formatted_log_name = f"{LOG_MAPPING[log]}"
                        formatted_log_list.append(formatted_log_name)
                    final_format_logs = ''
                    count = 0
                    for formatted_log in formatted_log_list:
                        if count == 0:
                            final_format_logs = f'"{formatted_log}"'
                            count += 1
                        elif 0 < count != len(formatted_log_list):
                            final_format_logs = f'{final_format_logs} OR "{formatted_log}"'
                            count += 1
                    final_format_logs = f'logName : ({final_format_logs})'
                    if "load_balancer" in log_selection:
                        final_format_logs = f'{final_format_logs} OR resource.type : ("http_load_balancer")'
                    if "gce_data" in log_selection:
                        final_format_logs = f'{final_format_logs} OR resource.type : ("gce")'
                    if "k8s" in log_selection:
                        final_format_logs = f'{final_format_logs} OR resource.type : ("k8s") OR resource.type : ("gke")'
                    if "cloud_sql" in log_selection:
                        final_format_logs = f'{final_format_logs} OR resource.type : ("cloudsql")'
            if custom_selection is not None:
                if log_selection is None:
                    final_format_logs = ''
                    count = 0
                    for custom_log in custom_selection:
                        if count == 0:
                            final_format_logs = f'"{custom_log}"'
                            count += 1
                        elif 0 < count != len(custom_selection):
                            final_format_logs = f'{final_format_logs} OR "{custom_log}"'
                    final_format_logs = f'logName : ({final_format_logs})'
                else:
                    for custom_log in custom_selection:
                        final_format_logs = f'{final_format_logs} OR logName : ("{custom_log}")'

            # Formatted parameters to use in historical log collection API call
            params = {
                "body": {
                    'resourceNames': rid,
                    'orderBy': "timestamp desc",
                    'pageSize': 500,
                    'filter': f'timestamp >= \"{start_time}\" AND '
                              f'timestamp <= \"{end_time}\" AND '
                              f'({final_format_logs})'
                }
            }

            # API call
            formatted_resource_id = rid.split('/')[-1]
            logging.info(f"Collecting logs from [{rid}]")
            handler.list_action(function='entries',
                                params=params,
                                inner_object='entries',
                                is_wrapped=True,
                                results_only=True,
                                documented_item=f'{formatted_resource_id}')
            handler.close()

    @staticmethod
    def collect_preview(handler, resource_ids: list = None):
        # Create file and headers if they don't exist
        if not os.path.exists(LOG_PREVIEW_TRACKER):
            with open(LOG_PREVIEW_TRACKER, 'a', encoding='utf-8') as fh:
                fh.write(f"timestamp,resource,log_preview\n")

        # Iterate through list of resources and output/record log listings
        for resource_id in resource_ids:
            logging.info(f"Collecting preview of available logs for resource [{resource_id}] ...")
            resource_type = resource_id.split('/')[0]
            log_preview_params = {
                "parent": f"{resource_id}"
            }
            log_preview = handler.list_action(function='logs', params=log_preview_params,
                                              inner_object='logNames', add_to_log=False,
                                              base_functions=[resource_type], results_only=True)
            handler.close()
            formatted_log_list = LogManagement.format_logs(log_preview)
            tabulate_table = tabulate(formatted_log_list,
                                      headers=[f'Log Name ({resource_id})', 'Log Description'],
                                      tablefmt='simple_outline')
            logging.info(f"Log preview gathered successfully \u2705")
            with open(LOG_PREVIEW_TRACKER, 'a', encoding='utf-8') as fh:
                fh.write(f"{time.strftime('%m/%d/%Y %H:%M:%SZ', time.gmtime())},"
                         f"{resource_id},{log_preview}\n{tabulate_table}\n")

    @staticmethod
    def format_logs(api_response):
        """Format a Google API response to extract available logs per resource level and place into Tabulate table"""
        extracted_logs = []
        for extracted_log in api_response:
            log = extracted_log.split(',')
            count = 0
            # Adds human-readable log name for Tabulate output based on LOG_MAPPING constant
            # Example: "/project/wrg-12345/logs/GCEGuestAgent" translates to "gce_data" on the table
            for short_name, long_names in LOG_MAPPING.items():
                if isinstance(long_names, str):
                    long_names = [long_names]
                for name in long_names:
                    if any(name in i for i in log):
                        log.append(short_name)
                        count = 1
            if count == 0:
                log.append('-')
            extracted_logs.append(log)
        return extracted_logs
