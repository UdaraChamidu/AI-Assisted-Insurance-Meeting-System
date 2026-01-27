
import logging
import io
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

# External libraries
import docx
import PyPDF2

# Services
from services.sharepoint_service import sharepoint_service
from rag.embeddings import embedding_service
from rag.pinecone_client import pinecone_client

logger = logging.getLogger(__name__)

class IngestionService:
    """
    Orchestrates the RAG ingestion pipeline:
    SharePoint -> Extract -> Chunk -> Embed -> Pinecone
    """
    
    TARGET_FOLDERS = [
        "00_TrainingReference",
        "01_FL_State_Authority",
        "02_CMS_Medicare_Authority",
        "03_Federal_ACA_Authority",
        "04_ERISA_IRS_SelfFunded",
        "05_FL_Medicaid_Agency",
        "06_Carrier_FMO_Policies"
    ]
    
    def __init__(self):
        self.sharepoint = sharepoint_service
        self.embeddings = embedding_service
        self.pinecone = pinecone_client
        
    async def run_pipeline(self, site_name: str = "EliteDealBroker"):
        """Run the full ingestion pipeline."""
        logger.info(f"Starting ingestion pipeline for site: {site_name}")
        
        # 1. Get Site ID
        site_id = self.sharepoint.search_site(site_name)
        if not site_id:
            logger.error(f"Site '{site_name}' not found.")
            return
            
        # 2. Get Drives
        drives = self.sharepoint.get_drives(site_id)
        target_drive = None
        
        # Priority: KB-DEV > Documents
        for drive in drives:
            name = drive.get('name', '')
            if name in ["KB-DEV", "KBDEV"]:
                target_drive = drive
                break
        
        if not target_drive:
            # Fallback to Documents
            for drive in drives:
                if drive.get('name') == "Documents":
                    target_drive = drive
                    break
        
        if not target_drive:
            target_drive = drives[0] if drives else None
            
        if not target_drive:
            logger.error("No drives found.")
            return

        drive_id = target_drive['id']
        logger.info(f"Using Drive: {target_drive.get('name')} ({drive_id})")
        
        docs_processed = 0
        chunks_upserted = 0
        
        # 3. Process each Target Folder explicitly
        # This ensures we know which "Regulatory Universe" the file belongs to.
        
        # First, list root items to map folder names to IDs
        root_items = self.sharepoint.list_drive_items(drive_id)
        folder_map = {item['name']: item['id'] for item in root_items if 'folder' in item}
        
        for folder_name in self.TARGET_FOLDERS:
            if folder_name not in folder_map:
                logger.warning(f"Target folder not found: {folder_name}")
                continue
                
            folder_id = folder_map[folder_name]
            logger.info(f"Scanning Universe: {folder_name}")
            
            # Recursive list from this folder
            items = self.sharepoint.recursive_list_items(drive_id, folder_id)
            
            for item in items:
                # Skip folders
                if 'folder' in item: continue
                
                # Check file extension
                filename = item.get('name', '').lower()
                if not (filename.endswith('.docx') or filename.endswith('.pdf')):
                    continue
                
                try:
                    logger.info(f"Processing file: {filename} in {folder_name}")
                    
                    # Download
                    content = self.sharepoint.get_file_content(drive_id, item['id'])
                    if not content: continue
                    
                    # Parse & Chunk
                    # Pass folder_name as universe
                    metadata = self._extract_metadata(item)
                    metadata['universe'] = folder_name # Explicit Universe Tagging
                    
                    chunks = self._parse_and_chunk(filename, content, metadata)
                    
                    if not chunks: continue
                        
                    # Embed & Upsert
                    vectors_to_upsert = []
                    texts_to_embed = [c['text'] for c in chunks]
                    embeddings_list = self.embeddings.embed_batch(texts_to_embed)
                    
                    for i, chunk in enumerate(chunks):
                        vector = {
                            "id": chunk['id'],
                            "embedding": embeddings_list[i],
                            "metadata": chunk['metadata']
                        }
                        vectors_to_upsert.append(vector)
                    
                    count = self.pinecone.upsert_chunks(vectors_to_upsert)
                    chunks_upserted += count
                    docs_processed += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process {filename}: {e}")
                
        logger.info(f"Pipeline Complete. Docs: {docs_processed}, Chunks: {chunks_upserted}")

    def _extract_metadata(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize SharePoint metadata fields."""
        # Graph API returns custom columns in 'fields' dict
        fields = item.get('fields', {})
        
        return {
            "filename": item.get('name'),
            "sharepoint_id": item.get('id'),
            "web_url": item.get('webUrl'),
            "last_modified": item.get('lastModifiedDateTime'),
            "state": fields.get('State', 'General'),
            "product_universe": fields.get('ProductUniverse', 'General'),
            "regulator": fields.get('Regulator', 'General'),
            "authority_level": fields.get('AuthorityLevel', 'Reference'),
            "carrier": fields.get('Carrier', 'None')
        }

    def _parse_and_chunk(self, filename: str, content: bytes, base_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse file content and split into chunks."""
        text_chunks = []
        
        if filename.endswith('.docx'):
            text_chunks = self._parse_docx(content)
        elif filename.endswith('.pdf'):
            text_chunks = self._parse_pdf(content)
            
        # Add metadata and IDs
        final_chunks = []
        for i, chunk_text in enumerate(text_chunks):
            # 150-350 words check is done during parsing/chunking logic below
            
            chunk_id = f"{base_metadata['sharepoint_id']}_{i}"
            
            # Combine base metadata with chunk text
            meta = base_metadata.copy()
            meta['text'] = chunk_text
            meta['chunk_index'] = i
            
            final_chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": meta
            })
            
        return final_chunks

    def _parse_docx(self, content: bytes) -> List[str]:
        """
        Extract text from DOCX with heading-based chunking.
        Target: 150-350 words.
        """
        doc = docx.Document(io.BytesIO(content))
        chunks = []
        current_chunk = []
        current_word_count = 0
        current_header = ""
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text: continue
            
            style = para.style.name.lower()
            is_header = 'heading' in style
            
            word_count = len(text.split())
            
            # Decision: Start new chunk?
            # 1. If it's a header and we have enough content in current chunk
            # 2. If current chunk is too big
            
            if is_header:
                # If we have a significant chunk already, save it
                if current_word_count > 100: 
                    self._finalize_chunk(chunks, current_chunk, current_header)
                    current_chunk = []
                    current_word_count = 0
                    
                current_header = text
                current_chunk.append(f"## {text}") # Add header to chunk text
                current_word_count += word_count
                
            else:
                current_chunk.append(text)
                current_word_count += word_count
                
                # Check strict limits
                if current_word_count >= 300:
                    self._finalize_chunk(chunks, current_chunk, current_header)
                    current_chunk = []
                    current_word_count = 0
        
        # Finalize last chunk
        if current_chunk:
            self._finalize_chunk(chunks, current_chunk, current_header)
            
        return chunks

    def _parse_pdf(self, content: bytes) -> List[str]:
        """
        Extract from PDF. 
        Since PDF structure is hard, we use sliding window of ~300 words.
        """
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"
                
            # Simple text splitting
            words = full_text.split()
            chunks = []
            chunk_size = 300
            overlap = 50
            
            for i in range(0, len(words), chunk_size - overlap):
                chunk_words = words[i:i + chunk_size]
                chunk_text = " ".join(chunk_words)
                if len(chunk_text) > 50: # Min filtering
                    chunks.append(chunk_text)
                    
            return chunks
        except Exception as e:
            logger.error(f"PDF Parsing error: {e}")
            return []

    def _finalize_chunk(self, chunks_list, current_lines, header):
        """Helper to join lines and append to list."""
        text = "\n".join(current_lines).strip()
        if len(text) > 50: # Min length
            # If we captured a header but it's not in the text (e.g. from previous context), prepend it
             # (Logic simplified: we already added header to current_chunk in _parse_docx)
            chunks_list.append(text)

ingestion_service = IngestionService()
