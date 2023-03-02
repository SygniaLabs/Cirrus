import logging
from googleapiclient.discovery import build

from ..shared.module_handler import ModuleHandler
from ..shared.shared_utils import MemoryCache

SUPPORTED_CONFIGS = ['gcp_map', 'rb_map', 'sa_info', 'sa_key_info', 'all_configs']


class AssetInventoryManagement(ModuleHandler):
    def __init__(self, creds, file_handler):
        super().__init__(creds, file_handler, build('cloudasset', 'v1', credentials=creds, cache=MemoryCache()), 'asset_inventory')

    @staticmethod
    def collect_configs(handler, resource_ids: list, config_selection: list):
        """Collect configuration data based on user-specified configs"""
        resource_type = resource_ids[0].split('/')[0]
        if 'rb_map' in config_selection or 'all_configs' in config_selection:
            AssetInventoryManagement.collect_role_bindings(handler, resource_type, resource_ids)
        if 'sa_info' in config_selection or 'all_configs' in config_selection:
            AssetInventoryManagement.collect_service_accounts(handler, resource_type, resource_ids)
        if 'sa_key_info' in config_selection or 'all_configs' in config_selection:
            AssetInventoryManagement.collect_service_account_keys(handler, resource_type, resource_ids)
        if resource_type == 'folders' or resource_type == 'organizations':
            if 'gcp_map' in config_selection or 'all_configs' in config_selection:
                AssetInventoryManagement.create_gcp_resource_map(handler, resource_type, resource_ids)

    @staticmethod
    def collect_role_bindings(handler, resource_type: str, resource_ids: list):
        """Used to parse user-specified resources where role bindings are being collected"""
        if resource_type == 'organizations':
            org_id = resource_ids[0]
            AssetInventoryManagement.create_role_bindings_map(handler, org_id)
        elif resource_type == 'folders':
            for folder_id in resource_ids:
                AssetInventoryManagement.create_role_bindings_map(handler, folder_id)
        elif resource_type == 'projects':
            for project_id in resource_ids:
                AssetInventoryManagement.create_role_bindings_map(handler, project_id)

    @staticmethod
    def create_role_bindings_map(handler, resource_id: str):
        """Collects role bindings in specified resource"""
        # Set up parameters to execute API call: collect active role bindings across specified resource
        rb_params = {
            'parent': f'{resource_id}',
            'contentType': 'IAM_POLICY'
        }
        # API call
        isolated_resource_id = resource_id.split('/')[1]
        logging.info(f"Collecting role bindings from [{resource_id}]")
        handler.list_action(function='assets', params=rb_params, inner_object='assets',
                            documented_item=f"role_bindings_{isolated_resource_id}")
        handler.close()

    @staticmethod
    def collect_service_accounts(handler, resource_type: str, resource_ids: list):
        """Used to parse user-specified resources where service account info is being collected"""
        if resource_type == 'organizations':
            org_id = resource_ids[0]
            AssetInventoryManagement.collect_service_account_information(handler, org_id)
        elif resource_type == 'folders':
            for folder_id in resource_ids:
                AssetInventoryManagement.collect_service_account_information(handler, folder_id)
        elif resource_type == 'projects':
            for project_id in resource_ids:
                AssetInventoryManagement.collect_service_account_information(handler, project_id)

    @staticmethod
    def collect_service_account_information(handler, resource_id: str):
        """Collects information associated with service accounts originating in user-specified resources"""
        # Set up parameters to execute API call: collect service account(s) info from specified resources
        sa_params = {
            'parent': f'{resource_id}',
            'assetTypes': 'iam.googleapis.com/ServiceAccount',
            'contentType': 'RESOURCE'
        }
        # API call
        isolated_resource_id = resource_id.split('/')[1]
        logging.info(f"Collecting service account information from [{resource_id}]")
        handler.list_action(function='assets', params=sa_params, inner_object='assets',
                            documented_item=f"service_accounts_{isolated_resource_id}")
        handler.close()

    @staticmethod
    def collect_service_account_keys(handler, resource_type: str, resource_ids: list):
        """Used to gather service account key information across specified resource ID(s)"""
        if resource_type == 'organizations':
            org_id = resource_ids[0]
            AssetInventoryManagement.collect_service_account_information(handler, org_id)
        elif resource_type == 'folders':
            for folder_id in resource_ids:
                AssetInventoryManagement.collect_service_account_information(handler, folder_id)
        elif resource_type == 'projects':
            for project_id in resource_ids:
                AssetInventoryManagement.collect_service_account_information(handler, project_id)

    @staticmethod
    def collect_service_account_key_info(handler, resource_id: str):
        """Collects information associated with service account keys originating in user-specified resources"""
        # Set up parameters to execute API call: gather info on service account keys from targeted project(s)
        sa_key_params = {
            'parent': f'{resource_id}',
            'assetTypes': 'iam.googleapis.com/ServiceAccountKey',
            'contentType': 'RESOURCE'
        }
        # API call
        isolated_resource_id = resource_id.split('/')[1]
        logging.info(f"Collecting service account key information from [{resource_id}]")
        handler.list_action(function='assets', params=sa_key_params, inner_object='assets',
                            documented_item=f"service_accounts_keys_{isolated_resource_id}")
        handler.close()

    @staticmethod
    def create_gcp_resource_map(handler, resource_type: str, resource_ids: list):
        """Used to create a GCP resource hierarchy map (only available when access is given against a folder or org)"""
        if resource_type == 'organizations':
            org_id = resource_ids[0]
            logging.info(f"Generating resource hierarchy map from [{org_id}]")
            AssetInventoryManagement.create_resource_hierarchy_map(handler, 'organizations', org_id)
            AssetInventoryManagement.create_resource_hierarchy_map(handler, 'folders', org_id)
            AssetInventoryManagement.create_resource_hierarchy_map(handler, 'projects', org_id)
        if resource_type == 'folders':
            for folder_id in resource_ids:
                logging.info(f"Generating resource hierarchy map from [{folder_id}]")
                AssetInventoryManagement.create_resource_hierarchy_map(handler, 'folders', folder_id)
                AssetInventoryManagement.create_resource_hierarchy_map(handler, 'projects', folder_id)

    @staticmethod
    def create_resource_hierarchy_map(handler, resource_type: str, resource_id: str):
        """Collects resource hierarchy information from the perspective of targeted resource ID"""
        formatted_resource_type = resource_type[:-1].capitalize()
        params = {
            'parent': f'{resource_id}',
            'assetTypes': f'cloudresourcemanager.googleapis.com/{formatted_resource_type}',
            'contentType': 'RESOURCE'
        }
        isolated_resource_id = resource_id.split('/')[1]
        handler.list_action(function='assets', params=params, inner_object='assets',
                            documented_item=f"resource_hierarchy_{resource_type}_{isolated_resource_id}")
        handler.close()
