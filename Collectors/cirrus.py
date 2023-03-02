#!/usr/bin/env python3
import sys

from collectors.gw import main as gw_main
from collectors.gcp import main as gcp_main


def arg_error():
    print('Please enter "gw" (Google Workspace/Cloud Identity) or "gcp" (Google Cloud Platform) to choose one of the collectors.')
    print('Usage examples:')
    print('\tcirrus.py gw --key-file /path/to/creds.json --super-admin admin@example.com --override-cache all')
    print('\tcirrus.py gcp --key-file /path/to/creds.json logs --project-id test-project-12345 --logs all_logs --start-time 2022-01-01T00:00:00Z --end-time 2022-01-08T00:00:00Z')


def main():
    args = sys.argv
    if len(args) < 2:
        arg_error()
        return

    if args[1] == 'gw':
        gw_main()
    elif args[1] == 'gcp':
        gcp_main()
    else:
        arg_error()


if __name__ == '__main__':
    main()
