
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import MagicMock, AsyncMock

# Mock services before import
# sys.modules['services.sharepoint_service.sharepoint_service'] = MagicMock()
# sys.modules['rag.pinecone_client.pinecone_client'] = MagicMock()

from services.ingestion_service import ingestion_service

async def test_dry_run():
    print("Starting Dry Run Verification...")
    
    # Mock SharePoint
    mock_sp = MagicMock()
    mock_sp.search_site.return_value = "site_123"
    mock_sp.get_drives.return_value = [{'name': 'Documents', 'id': 'drive_123'}]
    mock_sp.list_drive_items.return_value = [
        {'name': '00_TrainingReference', 'folder': {}, 'id': 'f_00'},
        {'name': '01_FL_State_Authority', 'folder': {}, 'id': 'f_01'}
    ]
    # Simulate recursive listing returning one file
    mock_sp.recursive_list_items.return_value = [
        {
            'name': 'test_policy.docx', 
            'id': 'file_1', 
            'file': {}, 
            'fields': {'State': 'FL', 'ProductUniverse': 'ACA'}
        }
    ]
    # Mock file content (Empty DOCX signature or minimal valid docx bytes?)
    # We'll just mock get_file_content to return None to skip parsing in this dry run 
    # OR we can mock the parsing method.
    mock_sp.get_file_content.return_value = None 
    
    ingestion_service.sharepoint = mock_sp
    
    # Mock Pinecone
    mock_pc = MagicMock()
    mock_pc.upsert_chunks.return_value = 1
    ingestion_service.pinecone = mock_pc
    
    # Mock Embeddings
    mock_emb = MagicMock()
    ingestion_service.embeddings = mock_emb
    
    # Run Pipeline
    print("Running Pipeline...")
    await ingestion_service.run_pipeline()
    
    # Inspect calls
    print(f"SharePoint Search Site called: {mock_sp.search_site.called}")
    print(f"Recursive List Items called: {mock_sp.recursive_list_items.called}")
    
    print("Dry Run Complete.")

if __name__ == "__main__":
    asyncio.run(test_dry_run())
