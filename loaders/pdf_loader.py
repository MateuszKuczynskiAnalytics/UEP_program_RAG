from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import json
from scrapers.utils import logger, setup_logging

def load_and_split_documents(base_dir, chunk_size=1000, chunk_overlap=200):
    setup_logging("logs/loading_logs.log")
    from scrapers.utils import logger
    all_chunks = []

    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # Count total PDF files
    pdf_files = [os.path.join(root, file) for root, _, files in os.walk(base_dir) for file in files if file.endswith(".pdf")]
    total_files = len(pdf_files)

    for idx, pdf_path in enumerate(pdf_files, start=1):
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        logger.info(f"({idx}/{total_files}) Successfully loaded document: {pdf_path}")

        # Load corresponding JSON metadata
        json_path = pdf_path.replace(".pdf", ".json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as json_file:
                metadata = json.load(json_file)

            # Enrich each document with metadata
            for doc in documents:
                doc.metadata.update(metadata)

            # Split the document into chunks
            chunks = text_splitter.split_documents(documents)

            # Add chunks to the list
            all_chunks.extend(chunks)
            logger.info(f"({idx}/{total_files}) Successfully split PDF file into chunks: {pdf_path}")
        else:
            logger.warning(f"({idx}/{total_files}) Metadata JSON not found for {pdf_path}")

    return all_chunks


base_dir = "raw_data"
all_chunks = load_and_split_documents(base_dir)