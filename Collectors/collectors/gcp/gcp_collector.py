import logging
import os
import sys
import time

from google.oauth2.service_account import Credentials

from .asset_inventory import AssetInventoryManagement
from .cmdline import Parser
from .logging_data import LogManagement
from ..shared.shared_utils import FileHandler, DEFAULT_OUTPUT_FOLDER

log_file = None

BG = "\u001b[32;1m"  # Bright green
RR = "\u001b[0m"  # Reset


def main():
    global log_file
    file_handler = None
    try:
        # Parse arguments
        parser = Parser()
        args = parser.parser.parse_args(sys.argv[2:])
        cmdline = " ".join(sys.argv)

        # Validate arguments
        if args.module == 'logs':
            parser.validate_log_collection_args(parser.parser, args)
        if args.module == 'configurations':
            parser.validate_config_collection_args(parser.parser, args)

        # Create file handler (for output folder and log file)
        file_handler = FileHandler(folder=args.output, log_file=args.log_file, cmdline=cmdline)
        log_file = file_handler.log_file

        # Basic validations
        if not os.access(args.key_file, os.R_OK):
            exit('cannot find/access the service account key file location on disk. Exiting.')

        # Script start time for tracking
        script_start_time = time.time()

        # Log collection (or log preview)
        if args.module == 'logs':
            # Log preview
            if args.preview:
                preview_log_values = parser.user_cli_preview_logs(parser.parser, args)

                service_account_credentials = Credentials.from_service_account_file(
                    preview_log_values['credential_file'])
                preview_handler = LogManagement(creds=service_account_credentials, file_handler=file_handler)

                LogManagement.collect_preview(preview_handler,
                                              resource_ids=preview_log_values['resource_ids'])
            # Log collection
            else:
                log_collection_values = parser.user_cli_log_collection(parser.parser, args)
                service_account_credentials = Credentials.from_service_account_file(
                    log_collection_values['credential_file'])
                log_handler = LogManagement(creds=service_account_credentials, file_handler=file_handler)

                if args.custom_logs:
                    LogManagement.collect_logs(log_handler,
                                               resource_ids=log_collection_values['resource_ids'],
                                               log_selection=log_collection_values['log_selection'],
                                               custom_selection=log_collection_values['custom_selection'],
                                               start_time=log_collection_values['start_time'],
                                               end_time=log_collection_values['end_time'])
                else:
                    LogManagement.collect_logs(log_handler,
                                               resource_ids=log_collection_values['resource_ids'],
                                               log_selection=log_collection_values['log_selection'],
                                               start_time=log_collection_values['start_time'],
                                               end_time=log_collection_values['end_time'])

        # Config collection
        if args.module == 'configurations':
            config_collection_values = parser.user_cli_config_collection(parser.parser, args)
            service_account_credentials = Credentials.from_service_account_file(
                config_collection_values['credential_file'])
            config_handler = AssetInventoryManagement(creds=service_account_credentials,
                                                      file_handler=file_handler)
            AssetInventoryManagement.collect_configs(config_handler,
                                                     resource_ids=config_collection_values['resource_ids'],
                                                     config_selection=config_collection_values['config_selection'])

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


if __name__ == "__main__":
    main()
