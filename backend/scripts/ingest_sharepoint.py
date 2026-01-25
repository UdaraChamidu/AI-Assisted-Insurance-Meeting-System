
import asyncio
import os
import sys
import json
import io
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sharepoint_service import sharepoint_service
from rag.embeddings import embedding_service
from rag.pinecone_client import pinecone_client
from typing import List, Dict

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
KB_SITE_NAME = "Compliance"
KB_LIB_NAME = "KB-DEV"
IGNORED_FOLDERS = ["00_TrainingReference", "Forms"]
STATE_FILE = "sync_state.json"

class LocalFileService:
    """Mock Service for Local Ingestion"""
    def __init__(self, root_path):
        self.root_path = root_path
        
    def list_drive_items(self, drive_id, folder_path=None):
        target_path = os.path.join(self.root_path, folder_path) if folder_path else self.root_path
        items = []
        if not os.path.exists(target_path):
            return []
            
        for entry in os.scandir(target_path):
            item = {
                'id': entry.path,
                'name': entry.name,
                'lastModifiedDateTime': str(entry.stat().st_mtime), # Incremental Key
                'fields': {'Regulator': 'LocalMock', 'AuthorityLevel': 'LocalMock'}
            }
            if entry.is_dir():
                item['folder'] = {}
            else:
                item['file'] = {}
            items.append(item)
        return items

    def get_file_content(self, drive_id, file_id):
        try:
            with open(file_id, 'rb') as f:
                return f.read()
        except Exception:
            return None

class IngestionPipeline:
    def __init__(self):
        self.state_file = STATE_FILE
        self.sync_state = self._load_state()

    def _load_state(self) -> Dict[str, str]:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_state(self):
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.sync_state, f, indent=2)
        except Exception:
            pass

    def extract_text(self, file_content: bytes, file_name: str) -> str:
        try:
            if file_name.endswith('.txt'):
                return file_content.decode('utf-8', errors='ignore')
            elif file_name.endswith('.pdf'):
                import PyPDF2
                pdf = PyPDF2.PdfReader(io.BytesIO(file_content))
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                return text
            return ""
        except Exception as e:
            logger.error(f"Text extraction failed for {file_name}: {e}")
            return ""

    def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1
            if current_length >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    async def run(self, local_mode: bool = False):
        logger.info(f"Starting Ingestion Pipeline (Local Mode: {local_mode})...")
        processed_count = 0
        
        if local_mode:
            logger.info("Using LOCAL Mock Service reading from 'kb_dev'...")
            service = LocalFileService(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'kb_dev'))
            drive_id = "local_drive"
            root_items = service.list_drive_items(drive_id)
        else:
            # SharePoint Login Logic
            site_id = os.getenv("SHAREPOINT_SITE_ID")
            if not site_id:
                 site_id = sharepoint_service.search_site(KB_SITE_NAME)
            if not site_id:
                logger.error("Could not find SharePoint Site ID.")
                return

            drives = sharepoint_service.get_drives(site_id)
            kb_drive = next((d for d in drives if d['name'] == KB_LIB_NAME), None)
            if not kb_drive:
                logger.error(f"Could not find Document Library '{KB_LIB_NAME}'")
                return
            
            drive_id = kb_drive['id']
            service = sharepoint_service
            root_items = service.list_drive_items(drive_id)

        for item in root_items:
            if "folder" in item and item['name'] not in IGNORED_FOLDERS:
                universe_name = item['name']
                logger.info(f"Checking Universe: {universe_name}")
                files = service.list_drive_items(drive_id, folder_path=universe_name)
                
                for file in files:
                    if "file" in file:
                        file_id = file['id']
                        file_name = file['name']
                        last_modified = file.get('lastModifiedDateTime', '')
                        
                        # INCREMENTAL CHECK
                        if self.sync_state.get(file_id) == last_modified:
                            continue
                            
                        logger.info(f"  > Processing New/Modified File: {file_name}")
                        
                        # Process
                        fields = file.get('fields', {})
                        content = service.get_file_content(drive_id, file_id)
                        if not content: continue
                        
                        text = self.extract_text(content, file_name)
                        if not text: continue
                        
                        chunks = self.chunk_text(text)
                        vectors = []
                        for i, chunk_text in enumerate(chunks):
                            embedding = embedding_service.embed_query(chunk_text)
                            vector_id = f"{universe_name}_{file_name}_{i}"
                            vector_id = "".join([c if c.isalnum() else "_" for c in vector_id])
                            
                            metadata = {
                                "text": chunk_text, 
                                "source": file_name, 
                                "universe": universe_name,
                                "regulator": fields.get('Regulator', 'Unknown'),
                                "authority": fields.get('AuthorityLevel', 'Unknown'),
                                "last_modified": last_modified
                            }
                            
                            vectors.append({"id": vector_id, "values": embedding, "metadata": metadata})
                            
                        if vectors:
                            pinecone_client.upsert_chunks(vectors)
                            processed_count += 1
                            self.sync_state[file_id] = last_modified
                            self._save_state()

        logger.info(f"Ingestion Complete. Processed {processed_count} new files.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", help="Run in local simulation mode")
    args = parser.parse_args()
    asyncio.run(IngestionPipeline().run(local_mode=args.local))
