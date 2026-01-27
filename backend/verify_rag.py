import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.pinecone_client import PineconeClient
from rag.embeddings import embedding_service
from rag.retriever import retriever_service

def verify_rag():
    print("--- RAG SYSTEM DIAGNOSTIC ---")
    
    # 1. Load Environment
    load_dotenv(override=True)
    print("[1] Environment loaded.")
    
    # 2. Check Pinecone Connection
    print("\n[2] Checking Pinecone Connection...")
    try:
        # Bypass get_pinecone_client check to test if Key works despite dummy Environment var
        pc_client = PineconeClient()
        stats = pc_client.get_stats()
        print(f"✅ Pinecone Connected. Index Stats: {stats}")
        
        if stats.get('total_vectors', 0) == 0:
            print("⚠️ Warning: Index is empty. RAG search will return no results.")

    except Exception as e:
        print(f"❌ Pinecone Connection Failed: {e}")
        return
    
    # 3. Test Embedding Service
    print("\n[3] Testing Embedding Service...")
    test_query = "Who is the regulator for Florida Medicaid?"
    try:
        query_embedding = embedding_service.embed_query(test_query)
        print(f"✅ Embedding generated. Vector dimension: {len(query_embedding)}")
    except Exception as e:
        print(f"❌ Embedding Generation Failed: {e}")
        return

    # 4. Test Search (Raw Pinecone)
    print("\n[4] Testing Raw Pinecone Search...")
    try:
        results = pc_client.search(query_embedding, top_k=3)
        print(f"✅ Search executed successfully. Found {len(results)} matches.")
        for i, match in enumerate(results):
            score = match.get('score', 0)
            meta = match.get('metadata', {})
            filename = meta.get('filename', 'Unknown')
            universe = meta.get('universe', 'Unknown')
            print(f"   {i+1}. Score: {score:.4f} | File: {filename} | Universe: {universe}")
    except Exception as e:
        print(f"❌ Search Failed: {e}")
        return

    # 5. Test Full Retriever Service (End-to-End)
    print("\n[5] Testing Retriever Service (End-to-End)...")
    try:
        # Using run_in_executor for async if needed, but retriever has async method
        # and we are in sync main. We will just call the sync wrapper logic or run async loop
        result = asyncio.run(retriever_service.retrieve(test_query, top_k=3))
        
        print(f"✅ Retriever Service returned {result['total_results']} results.")
        if result.get('error'):
            print(f"❌ Retriever Error: {result['error']}")
    except Exception as e:
        print(f"❌ Retriever Service Failed: {e}")

    print("\n--- DIAGNOSTIC COMPLETE ---")

if __name__ == "__main__":
    verify_rag()
