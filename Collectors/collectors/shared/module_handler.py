import logging
from time import sleep

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build, Resource

from .shared_utils import FileHandler, ConsoleFormatter, MemoryCache

BG = "\u001b[32;1m"  # Bright green
RR = "\u001b[0m"  # Reset


class ModuleHandler:
    """
    ModuleHandler is a class that interacts with Google API using several methods to allow easily execution of API calls
    to Google. The best practice to use this class is to inherit from it, as can be seen for example in
    "admin_directory.py".
    """
    MAX_EVENTS = 50000
    MAX_PAGES = 50
    MAX_RETRY = 3
    SLEEP_SECONDS_FOR_RETRY = 5

    def __init__(self, creds: Credentials, file_handler: FileHandler, service: Resource, module: str,
                 console_formatter: ConsoleFormatter = None):
        """
        @param creds: Google creds object
        @param file_handler: FileHandler object from shared_utils.py
        @param service: the API service object, created by googleapiclient.discovery.build function
        @param module: a string describing the requestes service. Used mainly for documentation purposes.
        """
        self.creds = creds
        self.service = service
        self.file_handler = file_handler
        self.module = module
        self.delegates = {}
        self.configure_formatter()
        # self.console_formatter = console_formatter if console_formatter is not None else ConsoleFormatter()

    def list_action(self, function: str, params: dict, metadata_additions: list = None, documented_item: str = None,
                    inner_object: str = None, add_to_log: bool = True, service: object = None,
                    base_functions: list = None, results_only: bool = True, is_wrapped=False,
                    is_get_action: bool = False, is_no_action: bool = False, is_create_action: bool = False):
        """
        This function executes a single Google API call.

        Params introduction:

        Any Google API request is written in Python according to the following pattern:
        service.{base_function1().base_function2() ...}.function().action(params).execute()
        Examples:
            service.users().list(customer='my_customer', maxResults=10,orderBy='email').execute()

            service.users().settings().sendAd().list(userId='me').execute()
        @rtype: dict
        @param function: the main function that is used. this is the last function before the action.
        @param params: the params that are sent to the action method. The params needs to be structured as dictionary.
        @param metadata_additions: a list of tuples to add to metadata of the result. This data would be added to the
        params in the wrapped results, and does not affect the API call itself.
        @param documented_item: a specific entity (such as user, resource name, etc.) that the API call is executed for.
        If this parameter is supplied it is used only for output file names. Can also be used as a comment for the file
        name.
        @param inner_object: the inner object to extract from the results in the response.
        @param add_to_log: an indication for whether to add the results to the log or to simply return them.
        @param service: A custom service in case you wish to use a different service than of the object
        @param base_functions: all the functions that are before the main function, if there are any.
        @param results_only: by default the results are API response is wrapped by the function. This flag indicates
        to return the results without wrapping it.
        @param is_wrapped: for GCP responses, the response is wrapped with a key named "body", including metadata
        information which is used by the function for paging. If the submitted results are wrapped with "body",
        this flag indicates to unpack it.
        @param is_get_action: by default, the applied action is "list". Use this flag in order to change it to "get".
        @param is_no_action: by default, the applied action is "list". Use this flag in order to use no action.
        @param is_create_action: by default, the applied action is "list". Use this flag in order to change it
        to "create".
        @return: The function uses the FileHandler to write the results to the log file. In case the flag "add_to_log"
        was set to True, the function returns the results instead of writing them to the log.
        """
        requested_action = ''
        pages = 1
        try:

            # Get a handle for relevant API action based on service, base_functions and function (main function)
            service = service if service is not None else self.service
            if base_functions:
                for f in base_functions:
                    service = getattr(service, f)()
            action = getattr(service, function)
            results = {}
            total_event_count = 0
            final_results = []
            first_check = True
            partial_dump = False
            # Iterate each page of the results
            logging.info(f'Executing {self.module}=>{function}{requested_action}')
            self.file_handler.append_log(f'Executing {self.module}=>{function}{requested_action}, params: {params}')
            while first_check or 'nextPageToken' in results:
                # Update params token for next page if exists
                updated_params = params.copy()
                has_next_page = 'nextPageToken' in results
                if has_next_page:
                    if is_wrapped:  # for GCP historical logs results which are wrapped
                        updated_params['body']['pageToken'] = results['nextPageToken']
                    else:
                        updated_params['pageToken'] = results['nextPageToken']
                # Apply requested action with retry mechanism
                retry_count = 0
                success = False
                while retry_count < ModuleHandler.MAX_RETRY and not success:
                    try:
                        # Execute the relevant API action based on the relevant boolean flag
                        if is_get_action:
                            requested_action = '.get'  # for exception
                            results = action().get(**updated_params).execute()
                        elif is_create_action:
                            requested_action = '.create'  # for exception
                            results = action().create(**updated_params).execute()
                        elif is_no_action:
                            requested_action = ''
                            results = action(**updated_params).execute()
                        else:
                            requested_action = '.list'
                            results = action().list(**updated_params).execute()
                        success = True
                    except Exception as ex:
                        # Handle known errors
                        if 'Requested entity was not found.' in str(ex):
                            self.file_handler.append_log('Requested entity was not found')
                            break
                        # Retry Mechanism
                        else:
                            if retry_count == ModuleHandler.MAX_RETRY - 1:
                                self.add_error_to_log(function=function, requested_action=requested_action, page=pages,
                                                      latest_err=str(ex),
                                                      additions=f'Max retry count reached ({ModuleHandler.MAX_RETRY}).')
                                return {}  # END FUNCTION.
                            else:
                                retry_count += 1
                                sleep_time = retry_count * ModuleHandler.SLEEP_SECONDS_FOR_RETRY
                                logging.info(f'Failed to retrieve {function}{requested_action}, page #{pages}, '
                                             f'params {params}, metadata additions {metadata_additions}.\n'
                                             f'Exception: {str(ex)}\n'
                                             f'Retrying in {sleep_time} seconds...')
                                sleep(sleep_time)
                # append page results to final list
                final_result = results.get(inner_object, {}) if inner_object else results
                if len(final_result) > 0:
                    if type(final_result) == list:
                        final_results.extend(final_result)
                    else:
                        final_results.append(final_result)
                first_check = False

                # Check if there are too many pages. If so, the results are split to avoid high memory.
                # If the amount of pages is higher than the MAX_PAGES defined and add_to_log is False,
                # the function return only the first MAX_PAGES and writes an error to the log.
                if pages % ModuleHandler.MAX_PAGES == 0:
                    partial_dump = True
                    has_error = False
                    if results_only:
                        obj = final_results
                    else:
                        display_params = params.copy()
                        if metadata_additions is not None:
                            for key, value in metadata_additions:
                                display_params[key] = value
                        obj = {'module': self.module,
                               'function': function,
                               'params': display_params,
                               'data': final_results}
                    if add_to_log:
                        self.add_to_log(function=function, results=obj, documented_item=documented_item)
                        self.file_handler.append_log(
                            f'Partial dump for function {function}, params: {str(params)}. '
                            f'Total Pages written: {pages}')
                    else:
                        has_error = True
                        error_msg = f'WARNING: Max pages ({ModuleHandler.MAX_PAGES}) in memory ' \
                                    f'reached and results were ' \
                                    f'requested to be returned instead of being written to log. ' \
                                    f'Only partial results were returned.'
                        logging.info(error_msg)
                        self.add_error_to_log(function=function, requested_action=requested_action, page=pages,
                                              latest_err=error_msg)
                    # clear final results that were written to log
                    if not has_error:
                        final_results.clear()
                pages += 1

            # In case there are more results after partial dump, or only no partial dump at all
            if len(final_results) > 0:
                if results_only:
                    obj = final_results
                else:
                    display_params = params.copy()
                    if metadata_additions is not None:
                        for key, value in metadata_additions:
                            display_params[key] = value
                    obj = {'module': self.module,
                           'function': function,
                           'params': display_params,
                           'data': final_results}

                if add_to_log:

                    # Event counter
                    total_event_count = len(obj) if results_only else len(obj['data'])
                    if total_event_count % ModuleHandler.MAX_EVENTS == 0:
                        self.print_stdout(f"{total_event_count} events recorded and counting ...")
                    self.print_stdout(f'{total_event_count} results were found')
                    self.add_to_log(function=function, results=obj, documented_item=documented_item)
                    if partial_dump:
                        self.file_handler.append_log(
                            f'Ended partial dump for function {function}, params: {str(params)}. '
                            f'Total Pages written: {pages}')
                else:
                    return obj
            else:
                _out = f'No results for {function}{requested_action} with the following params ' \
                       f'{str(params)}. Acting as {self.creds._subject}'
                self.print_stdout('No Results Found')
                if add_to_log:
                    self.file_handler.append_log(_out)
                else:
                    logging.info(_out)
                return {}

            return None

        except Exception as ex:
            self.add_error_to_log(function=function, requested_action=requested_action, page=pages,
                                  latest_err=str(ex))

    def list_action_by_values(self, function: str, params: dict, list_items: list,
                              main_key: str = None,
                              inner_object: str = None, dynamic_key_param: str = None,
                              item_as_data: bool = False, delegate_users: bool = False,
                              base_functions: list = None, is_get_action: bool = False,
                              is_no_action: bool = False, is_create_action: bool = False,
                              results_only: bool = False, filename_additions: str = None
                              ) -> None:
        """
        This function executes multiple Google API call based on a given list.

        Params introduction:

        Any Google API request is written in Python according to the following pattern:
        service.{base_function1().base_function2() ...}.function().action(params).execute()
        Examples:
            service.users().list(customer='my_customer', maxResults=10,orderBy='email').execute()

            service.users().settings().sendAd().list(userId='me').execute()
        @rtype: None
        @param function: the main function that is used. this is the last function before the action.
        @param params: the params that are sent to the action method. The params needs to be structured as dictionary.
        @param list_items: the items to iterate on and execute a single API call for each one of them
        @param main_key: a string that represent the category of the items that the function iterated on,
        such as "user", "group", etc. This param is used only for the metadata_additions that are added to the results
        if there are wrapped.
        @param inner_object: the name of the JSON object in the results that contains the results data (other fields
        represent metadata).
        @param dynamic_key_param: If item_as_data is set to true - this param represents
        the keys in the "params" given to the function should have a dynamic value
        (each item in list_items) for each API call.
        @param item_as_data: Whether one of the keys in the "params" given to the function should have
        a dynamic value (each item in list_items) for each API call
        @param delegate_users: if list_items represent users, this boolean param indicates whether to create a new
        service with delegation for each user before applying the API call.
        @param base_functions: all the functions that are before the main function, if there are any.
        @param is_get_action: by default, the applied action is "list". Use this flag in order to change it to "get".
        @param is_no_action: by default, the applied action is "list". Use this flag in order to use no action.
        @param is_create_action: by default, the applied action is "list". Use this flag in order to change it
        to "create".
        @param results_only: by default the results are not wrapped by the list_action function
        with the requested params and metadata_additions. This flag indicates whether to return the results wrapped.
        @param filename_additions: additional string to add to after the supplied "item" in the output log filename.
        @return: None
        """
        self.file_handler.append_log(f'Iterating multiple items for function {function}')

        for item in list_items:
            if item_as_data and dynamic_key_param is not None:
                params[dynamic_key_param] = item
            service = None  # None service which is later sent to list_action method,
            # gets the service from self.service instead of overriding it

            if delegate_users:  # works only if item is the user
                if item in self.delegates:
                    delegated_credentials = self.delegates[item]
                else:
                    delegated_credentials = self.creds.with_subject(item)
                    self.delegates[item] = delegated_credentials

                if self.module == 'gmail':  # Currently the only module requires using the delegations
                    service = build('gmail', 'v1', credentials=delegated_credentials, cache=MemoryCache())

            metadata_additions = [(main_key, item)] if main_key is not None else None
            documented_item = f'{item}_{filename_additions}' if filename_additions else item

            self.print_stdout(f'Collecting data for [{item}] using the function {function}')

            self.file_handler.append_log(f'Current Item: {item}')
            self.list_action(function=function, params=params, inner_object=inner_object,
                             metadata_additions=metadata_additions,
                             service=service, base_functions=base_functions,
                             is_get_action=is_get_action, is_no_action=is_no_action,
                             is_create_action=is_create_action,
                             results_only=results_only, documented_item=documented_item)

            if service:
                service.close()

    def test_list_action(self, function: str, params: dict,
                         service: object = None,
                         base_functions: list = None,
                         is_get_action: bool = False, is_no_action: bool = False,
                         is_create_action: bool = False) -> dict:
        """
        This function tests a single Google API whether the API call was made successfully,
        a response sample, and API error message if there is one.

        Params introduction:

        Any Google API request is written in Python according to the following pattern:
        service.{base_function1().base_function2() ...}.function().action(params).execute()
        Examples:
            service.users().list(customer='my_customer', maxResults=10,orderBy='email').execute()

            service.users().settings().sendAd().list(userId='me').execute()
        @rtype: dict
        @param function: the main function that is used. this is the last function before the action.
        @param params: the params that are sent to the action method. The params needs to be structured as dictionary.
        @param service: A custom service in case you wish to use a different service than of the object
        @param base_functions: all the functions that are before the main function, if there are any.
        @param is_get_action: by default, the applied action is "list". Use this flag in order to change it to "get".
        @param is_no_action: by default, the applied action is "list". Use this flag in order to use no action.
        @param is_create_action: by default, the applied action is "list". Use this flag in order to change it
        to "create".
        @return: returns a "response" dictionary: response = {'success': bool,'results': dict,'error_msg': str}
        }
        """
        response = {
            'success': False,
            'results': None,
            'error_msg': None
        }
        try:
            service = service if service is not None else self.service
            if base_functions:
                for f in base_functions:
                    service = getattr(service, f)()
            action = getattr(service, function)
            results = {}
            if is_get_action:
                results = action().get(**params).execute()
            elif is_create_action:
                results = action().create(**params).execute()
            elif is_no_action:
                results = action(**params).execute()
            else:
                results = action().list(**params).execute()
            response['success'] = True
            response['results'] = results
        except Exception as ex:
            response['success'] = False
            response['error_msg'] = str(ex)
        return response

    def add_to_log(self, function: str, results: dict, documented_item: str = None):
        """
        This function adds the results of an API call to the log.

        @param function: the name of the function the results are for - used for output file name only
        @param results: the API response results
        @param documented_item: the name of the item that the function was executed for - used for output file name only
        @return: None
        """
        function_item = f'{function}_{documented_item}' if documented_item else function
        function_name = f'{self.module} {function_item}'
        outfile = f'{self.module}_{function_item}.json'
        try:
            self.file_handler.results_handler(results=results, outfile=outfile,
                                              function_name=function_name)
        except Exception as e:
            logging.info('Can\'t write to log:', str(e))
            logging.info(f"results for {function_item}=>", results)

    def add_error_to_log(self, function: str, requested_action: str,
                         page: int, latest_err: str, additions: str = '') -> None:
        """

        @param function: the name of the function the results are for - used for output file name only
        @param requested_action: the name of the requested action (get/list/create/etc.)
        that the function was executed for - used for output file name only.
        @param page: the page number in which the function failed at.
        @param latest_err: the error message itself that came back from the API.
        @param additions: custom additions to the logs
        @return: None
        """
        error_msg = f'Failed to retrieve {function}{requested_action}, page #{page}. Latest Error: {latest_err}'
        if additions != '':
            error_msg += '\n' + additions
        logging.info(error_msg)
        try:
            self.file_handler.append_log(error_msg)
        except Exception as e:
            logging.info('Can\'t write to log:', str(e))
            logging.info(error_msg)

    def print_stdout(self, msg):
        self.configure_formatter()
        console = logging.getLogger(__name__)
        console.info(msg)

    def configure_formatter(self):
        console_formatter = ConsoleFormatter()
        console_formatter.configure()

    def close(self):
        """
        closes the service.
        @return: None
        """
        if self.service:
            self.service.close()
