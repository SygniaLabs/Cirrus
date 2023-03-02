import os
import json
import logging
import argparse
from datetime import datetime
from google.oauth2.service_account import Credentials

RUNNING_DIRECTORY = os.path.realpath(__file__).rpartition('\\')[0]
DEFAULT_LOG_FILE = os.path.realpath(os.path.join(RUNNING_DIRECTORY, 'google_collectors.log'))
DEFAULT_OUTPUT_FOLDER = os.path.realpath(os.path.join(RUNNING_DIRECTORY, 'output'))
DEFAULT_CACHE_FOLDER = os.path.realpath(os.path.join(RUNNING_DIRECTORY, 'cache'))


class FileHandler:
    def __init__(self, folder, log_file, cmdline):
        self.folder = folder if folder is not None else DEFAULT_OUTPUT_FOLDER
        # self.tmp_file = DEFAULT_TMP_FILE
        self.log_file = log_file if log_file is not None else DEFAULT_LOG_FILE
        self._init_folder()
        self._init_log(cmdline)

    def results_handler(self, results={}, outfile='output.json', function_name='', writing_mode='w'):
        # obtain log file location from TMP file
        if not results:
            with open(self.log_file, 'a') as f:
                f.write(f'No results were found for function {function_name}\n')
        else:
            timestamp = FileHandler._get_time()
            parts = outfile.rpartition('.')
            outfile_with_time = f'{parts[0]}_{timestamp}.{parts[-1]}'
            new_file = os.path.realpath(os.path.join(self.folder, outfile_with_time))
            if os.path.exists(new_file):  # in case two file were created in the same millisecond
                _parts = new_file.rpartition('.')
                new_file = _parts[0] + "_." + _parts[-1]
            with open(new_file, writing_mode) as f:
                json.dump(results, f)
            with open(self.log_file, 'a') as f:
                f.write(f'Results for function {function_name} can found here: {new_file}\n')

    def _init_log(self, cmdline):
        try:
            with open(self.log_file, 'a') as f:
                f.write('-----------------------------------------------------------\n')
                f.write(f"Time: {FileHandler._get_time()}\n")
                f.write(f'Running command: {cmdline}\n')
        except:
            raise Exception(f'cannot init log file: {self.log_file}')

    def append_log(self, data):
        with open(self.log_file, 'a') as f:
            f.write(str(data) + '\n')

    def _init_folder(self):
        try:
            if not os.path.exists(self.folder):
                os.mkdir(self.folder)
        except:
            raise Exception(f'cannot create folder: {self.folder}')

    @staticmethod
    def _get_time():
        return datetime.utcnow().isoformat(sep='_', timespec='milliseconds').replace(':', '_')


class Validators:
    @staticmethod
    def time(value):
        try:
            datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
            return value
        except ValueError:
            raise argparse.ArgumentTypeError('Time fields should match RFC3339 date format: %Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def prompt_time(value):
        try:
            datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
            return True
        except ValueError:
            return False

    @staticmethod
    def credentials(cred_file):
        try:
            Credentials.from_service_account_file(cred_file)
        except:
            exit("Unable to generate credentials from service account key file")

    @staticmethod
    def table(user_prompt, range1, range2):
        bool_check = True
        for value in user_prompt:
            if value not in [str(i) for i in list(range(range1, range2))]:
                bool_check = False
        return bool_check

    @staticmethod
    def clear_terminal():
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")


class ConsoleFormatter:
    """Class for informative and stylized console output, so each module can handle console output dynamically"""

    def __init__(self):
        self.BG = "\u001b[32;1m"  # Bright green
        self.GD = "\u001b[33;5;220m"  # Gold
        self.RR = "\u001b[0m"  # Reset

    def configure(self):
        logging.basicConfig(level=logging.INFO)
        console = logging.StreamHandler()
        formatter = logging.Formatter(f"[{self.GD}{datetime.utcnow().isoformat(sep=' ', timespec='seconds')}{self.RR}] %(message)s")
        console.setFormatter(formatter)
        logging.getLogger("").addHandler(console)
        logging.getLogger().removeHandler(logging.getLogger().handlers[0])


class MemoryCache:
    """Class used to handle file_cache error when using oauth2client >= 4.0.0"""
    _CACHE = {}

    def get(self, url):
        return MemoryCache._CACHE.get(url)

    def set(self, url, content):
        MemoryCache._CACHE[url] = content