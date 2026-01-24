"""
Document ingestion script for RAG system.
Processes insurance documents and uploads to Pinecone.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from rag.embeddings import embedding_service, chunk_text, generate_chunk_id
from rag.pinecone_client import pinecone_client
import PyPDF2
import docx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        logger.error(f"Failed to read PDF {file_path}: {str(e)}")
    return text


def read_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    text = ""
    try:
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        logger.error(f"Failed to read DOCX {file_path}: {str(e)}")
    return text


def read_txt(file_path: str) -> str:
    """Read text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Failed to read TXT {file_path}: {str(e)}")
        return ""


def process_document(file_path: str, source_name: str = None):
    """
    Process a single document.
    
    Args:
        file_path: Path to document
        source_name: Optional source name (defaults to filename)
    
    Returns:
        List of chunks with embeddings and metadata
    """
    if not source_name:
        source_name = Path(file_path).name
    
    logger.info(f"Processing: {source_name}")
    
    # Read document based on extension
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        text = read_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        text = read_docx(file_path)
    elif ext == '.txt':
        text = read_txt(file_path)
    else:
        logger.warning(f"Unsupported file type: {ext}")
        return []
    
    if not text.strip():
        logger.warning(f"No text extracted from {source_name}")
        return []
    
    # Chunk text
    chunks = chunk_text(text, chunk_size=500, chunk_overlap=100)
    logger.info(f"Created {len(chunks)} chunks from {source_name}")
    
    # Generate embeddings
    embeddings = embedding_service.embed_batch(chunks)
    
    # Create chunk objects
    chunk_objects = []
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_id = generate_chunk_id(chunk, source_name, idx)
        
        chunk_objects.append({
            'id': chunk_id,
            'embedding': embedding,
            'metadata': {
                'text': chunk,
                'source': source_name,
                'chunk_index': idx,
                'total_chunks': len(chunks)
            }
        })
    
    return chunk_objects


def ingest_directory(directory_path: str):
    """
    Ingest all documents from a directory.
    
    Args:
        directory_path: Path to directory containing documents
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        logger.error(f"Directory not found: {directory_path}")
        return
    
    # Supported extensions
    supported_exts = ['.pdf', '.docx', '.doc', '.txt']
    
    # Find all documents
    all_chunks = []
    
    for file_path in directory.rglob('*'):
        if file_path.suffix.lower() in supported_exts:
            chunks = process_document(str(file_path))
            all_chunks.extend(chunks)
    
    if not all_chunks:
        logger.warning("No chunks created from documents")
        return
    
    logger.info(f"Total chunks to upload: {len(all_chunks)}")
    
    # Upload to Pinecone
    count = pinecone_client.upsert_chunks(all_chunks)
    logger.info(f"Successfully uploaded {count} chunks to Pinecone")
    
    # Print stats
    stats = pinecone_client.get_stats()
    logger.info(f"Pinecone index stats: {stats}")


def ingest_sample_data():
    """Create and ingest sample insurance documents."""
    logger.info("Creating sample insurance documents...")
    
    # Create documents directory
    docs_dir = Path(__file__).parent.parent / 'documents'
    docs_dir.mkdir(exist_ok=True)
    
    # Sample insurance content
    sample_policies = {
        'life_insurance.txt': """
Life Insurance Policy Information

Coverage Types:
- Term Life Insurance: Provides coverage for a specific period (10, 20, or 30 years). Lower premiums but no cash value.
- Whole Life Insurance: Lifetime coverage with cash value accumulation. Higher premiums but includes investment component.
- Universal Life Insurance: Flexible premiums and death benefit. Cash value grows based on market performance.

Pricing Factors:
- Age: Younger applicants receive lower rates
- Health: Medical exam required, better health = lower premium
- Coverage Amount: Higher coverage = higher premium
- Term Length: Longer terms may have slightly higher premiums

Important Notes:
COMPLIANCE: All quotes are estimates. Final pricing requires medical underwriting.
COMPLIANCE: Guaranteed issue policies available but at higher cost.
""",
        'auto_insurance.txt': """
Auto Insurance Policy Information

Required Coverage Types:
- Liability: Covers damage you cause to others (minimum $25,000/$50,000)
- Collision: Covers damage to your vehicle
- Comprehensive: Covers theft, vandalism, weather damage

Optional Coverage:
- Personal Injury Protection: Medical expenses regardless of fault
- Uninsured Motorist: Protects against uninsured drivers
- Roadside Assistance: Towing and emergency services

Discounts Available:
- Multi-car discount: 15-20% savings
- Safe driver: No accidents for 3 years = 20% discount
- Bundling: Combine with home insurance for 25% savings

COMPLIANCE: Minimum liability coverage required by law. We recommend higher limits for better protection.
""",
        'home_insurance.txt': """
Home Insurance Policy Information

Standard Coverage Includes:
- Dwelling: Structure of your home
- Personal Property: Belongings inside home (typically 50-70% of dwelling coverage)
- Liability: Legal protection if someone is injured on your property
- Additional Living Expenses: Temporary housing if home is uninhabitable

Pricing Based On:
- Home Value: Replacement cost, not market value
- Location: Flood zones and crime rates affect pricing
- Deductible: Higher deductible = lower premium
- Claims History: No claims in 5 years = better rates

Common Add-ons:
- Flood Insurance: Required in flood zones, separate policy
- Earthquake Coverage: Additional premium in high-risk areas
- Valuable Items Rider: Extra coverage for jewelry, art

COMPLIANCE: Standard policies do NOT cover flood or earthquake damage without additional riders.
COMPLIANCE: Review coverage annually to ensure adequate replacement cost coverage.
"""
    }
    
    # Write sample files
    for filename, content in sample_policies.items():
        file_path = docs_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        logger.info(f"Created: {filename}")
    
    # Ingest the directory
    ingest_directory(str(docs_dir))


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest documents for RAG system")
    parser.add_argument(
        '--directory',
        type=str,
        help='Directory containing documents to ingest'
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Create and ingest sample insurance documents'
    )
    
    args = parser.parse_args()
    
    if args.sample:
        ingest_sample_data()
    elif args.directory:
        ingest_directory(args.directory)
    else:
        print("Usage:")
        print("  Create sample data: python ingest_documents.py --sample")
        print("  Ingest directory:   python ingest_documents.py --directory /path/to/docs")
