
from msal import ConfidentialClientApplication
from config import settings
from typing import Optional, Dict, Any, List
import requests
import logging

logger = logging.getLogger(__name__)

class SharePointService:
    """
    Handles SharePoint integration via Graph API.
    Reuses the same App Registration (ClientId/Secret) as Bookings 
    assuming 'Sites.Read.All' permission is granted.
    """
    
    def __init__(self):
        self.client_id = settings.ms_client_id
        self.client_secret = settings.ms_client_secret
        self.tenant_id = settings.ms_tenant_id
        
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
        
        # Create MSAL app
        self.app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority
        )
        
        # Cache token briefly
        self._access_token = None

    def get_access_token(self) -> Optional[str]:
        """Get valid access token."""
        try:
            # Check if token needs refresh (simplified, MSAL handles caching usually)
            result = self.app.acquire_token_for_client(scopes=self.scopes)
            
            if "access_token" in result:
                return result["access_token"]
            else:
                logger.error(f"Failed to get token: {result.get('error_description')}")
                return None
        except Exception as e:
            logger.error(f"Token acquisition failed: {e}")
            return None

    def _get_headers(self) -> Optional[Dict[str, str]]:
        token = self.get_access_token()
        if not token:
            return None
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def search_site(self, site_name: str) -> Optional[str]:
        """Find a SharePoint site by name/keyword to get its Site ID."""
        headers = self._get_headers()
        if not headers: return None
        
        url = f"{self.graph_endpoint}/sites?search={site_name}"
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('value'):
                return data['value'][0]['id']
        return None

    def get_drives(self, site_id: str) -> List[Dict[str, Any]]:
        """List document libraries (Drives) in a site."""
        headers = self._get_headers()
        if not headers: return []
        
        url = f"{self.graph_endpoint}/sites/{site_id}/drives"
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json().get('value', [])
        return []

    def list_drive_items(self, drive_id: str, folder_path: str = None) -> List[Dict[str, Any]]:
        """
        List items in a drive folder. 
        If folder_path is None, lists root.
        """
        headers = self._get_headers()
        if not headers: return []
        
        if folder_path:
            # List specific folder by path
            url = f"{self.graph_endpoint}/drives/{drive_id}/root:/{folder_path}:/children"
        else:
            # List root
            url = f"{self.graph_endpoint}/drives/{drive_id}/root/children"
            
        # Expand fields to get custom columns (Metadata)
        url += "?$expand=fields"
        
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json().get('value', [])
        else:
            logger.error(f"Failed to list items ({resp.status_code}): {resp.text}")
            return []

    def recursive_list_items(self, drive_id: str, folder_id: str = "root") -> List[Dict[str, Any]]:
        """
        Recursively list all files in a drive/folder.
        """
        headers = self._get_headers()
        if not headers: return []
        
        all_items = []
        
        try:
            # Handle root vs specific folder
            if folder_id == "root":
                url = f"{self.graph_endpoint}/drives/{drive_id}/root/children?$expand=fields"
            else:
                url = f"{self.graph_endpoint}/drives/{drive_id}/items/{folder_id}/children?$expand=fields"
            
            while url:
                resp = requests.get(url, headers=headers)
                if resp.status_code != 200:
                    logger.error(f"Failed to list items recursivly ({resp.status_code}): {resp.text}")
                    break
                    
                data = resp.json()
                items = data.get('value', [])
                
                for item in items:
                    # If folder, recurse
                    if 'folder' in item:
                        sub_items = self.recursive_list_items(drive_id, item['id'])
                        all_items.extend(sub_items)
                    elif 'file' in item:
                        # Append file item
                        all_items.append(item)
                
                # Pagination
                url = data.get('@odata.nextLink')
                
            return all_items
            
        except Exception as e:
            logger.error(f"Recursive list failed: {e}")
            return all_items

    def get_file_content(self, drive_id: str, file_id: str) -> Optional[bytes]:
        """Download file content."""
        headers = self._get_headers()
        if not headers: return None
        
        url = f"{self.graph_endpoint}/drives/{drive_id}/items/{file_id}/content"
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.content
        return None

# Global Instance
sharepoint_service = SharePointService()
