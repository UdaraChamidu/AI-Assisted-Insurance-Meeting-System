
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

    def _safe_get_items(self, base_url: str) -> Dict[str, Any]:
        """
        Helper to get items with fallback for expand=fields.
        """
        headers = self._get_headers()
        if not headers: return {}
        
        # Try with expand
        url = f"{base_url}?$expand=fields"
        resp = requests.get(url, headers=headers)
        
        if resp.status_code == 200:
            return resp.json()
            
        if resp.status_code == 400:
            # Fallback: Try without expand
            logger.warning(f"Metadata expansion failed (400) for {base_url}. Retrying without metadata.")
            resp = requests.get(base_url, headers=headers)
            if resp.status_code == 200:
                return resp.json()
                
        # Error
        logger.error(f"Failed to list items ({resp.status_code}): {resp.text}")
        return {}
        
    def list_drive_items(self, drive_id: str, folder_path: str = None) -> List[Dict[str, Any]]:
        """
        List items in a drive folder. 
        """
        if folder_path:
            url = f"{self.graph_endpoint}/drives/{drive_id}/root:/{folder_path}:/children"
        else:
            url = f"{self.graph_endpoint}/drives/{drive_id}/root/children"
            
        data = self._safe_get_items(url)
        return data.get('value', [])

    def recursive_list_items(self, drive_id: str, folder_id: str = "root") -> List[Dict[str, Any]]:
        """
        Recursively list all files in a drive/folder.
        """
        all_items = []
        
        try:
            # Handle root vs specific folder
            if folder_id == "root":
                url = f"{self.graph_endpoint}/drives/{drive_id}/root/children"
            else:
                url = f"{self.graph_endpoint}/drives/{drive_id}/items/{folder_id}/children"
            
            # Helper logic for pagination + recursion
            # Note: _safe_get_items doesn't handle pagination loop easily, so we implement logic here
            
            # Initial fetch (try with expand)
            current_url = url + "?$expand=fields"
            fallback_mode = False
            
            while current_url:
                headers = self._get_headers()
                if not headers: break
                
                resp = requests.get(current_url, headers=headers)
                
                # Handle Fallback for 400
                if resp.status_code == 400 and not fallback_mode:
                    logger.warning("Switching to no-metadata mode due to 400 error.")
                    fallback_mode = True
                    current_url = url # Reset to base
                    continue

                if resp.status_code != 200:
                    logger.error(f"Failed to list items ({resp.status_code}): {resp.text}")
                    break
                    
                data = resp.json()
                items = data.get('value', [])
                
                for item in items:
                    # If folder, recurse
                    if 'folder' in item:
                        sub_items = self.recursive_list_items(drive_id, item['id'])
                        all_items.extend(sub_items)
                    elif 'file' in item:
                        all_items.append(item)
                
                # Pagination
                current_url = data.get('@odata.nextLink')
                # If fallback mode is on, nextLink usually comes correct (without expand? or we might need to strip it?)
                # Graph API nextLink usually preserves query params.
                
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
