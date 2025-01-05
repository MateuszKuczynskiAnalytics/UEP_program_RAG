from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import SpacyTextSplitter
import os
import json
import re
from scrapers.utils import logger, setup_logging

def clean_text(text):
    """
    Preprocess the text by removing newlines, handling unicode, and normalizing whitespace.
    """
    # Remove newlines
    text = text.replace("\n", " ")

    # Remove unwanted unicode characters
    text = text.replace("\x0c", "").replace("\x0b", "").replace("\xa0")

    # Normalize multiple spaces into one
    text = re.sub(r"\s+", " ", text).strip()

    return text

def load_and_split_documents(base_dir, max_length=1000000):
    setup_logging("logs/loading_logs.log")
    from scrapers.utils import logger
    all_chunks = []

    text_splitter = SpacyTextSplitter(
        separator="\n\n",
        pipeline="pl_core_news_sm",
        max_length=max_length
    )

    pdf_files = [os.path.join(root, file) for root, _, files in os.walk(base_dir) for file in files if file.endswith(".pdf")]
    total_files = len(pdf_files)

    for idx, pdf_path in enumerate(pdf_files, start=1):
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        logger.info(f"({idx}/{total_files}) Successfully loaded document: {pdf_path}")

        json_path = pdf_path.replace(".pdf", ".json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as json_file:
                metadata = json.load(json_file)

            for doc in documents:
                if metadata:
                    doc.metadata.update(metadata)
                doc.page_content = clean_text(doc.page_content)

            for doc in documents:
                chunks = text_splitter.split_documents([doc])
                all_chunks.extend(chunks)

            logger.info(f"({idx}/{total_files}) Successfully split PDF file into chunks: {pdf_path}")
        else:
            logger.warning(f"({idx}/{total_files}) Metadata JSON not found for {pdf_path}")

    return all_chunks

base_dir = "raw_data"
all_chunks = load_and_split_documents(base_dir)

