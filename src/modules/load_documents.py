import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import weaviate
from weaviate.classes.init import Auth
from config.config import Config
import os
from dotenv import load_dotenv
from src.config.logs import logger
load_dotenv()

def load_documents(path: str):
    """Load documents from the documents directory."""
    config = Config()
    os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY

    try:
        pdf_paths = glob.glob(path, recursive=True)
        
        all_docs = []
        for path in pdf_paths:
            loader = PyPDFLoader(path)
            docs = loader.load()
            all_docs.extend(docs)
        logger.info(f"Loaded {len(all_docs)} documents")
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        return None

    # print the number of documents loaded
    logger.info(f"Loaded {len(all_docs)} documents")

    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=config.CHUNK_SIZE)
        chunks = text_splitter.split_documents(all_docs)
        logger.info(f"Split {len(all_docs)} documents into {len(chunks)} chunks")
        
        # Sanitize metadata keys to be valid GraphQL property names
        # Replace dots and other invalid characters with underscores
        for chunk in chunks:
            if chunk.metadata:
                sanitized_metadata = {}
                for key, value in chunk.metadata.items():
                    # Replace dots and other invalid chars with underscores
                    sanitized_key = key.replace('.', '_').replace('-', '_').replace(' ', '_')
                    # Ensure it starts with a letter or underscore
                    if sanitized_key and not sanitized_key[0].isalpha() and sanitized_key[0] != '_':
                        sanitized_key = '_' + sanitized_key
                    # Truncate to 230 characters (GraphQL limit)
                    sanitized_key = sanitized_key[:230]
                    sanitized_metadata[sanitized_key] = value
                chunk.metadata = sanitized_metadata
    except Exception as e:
        logger.error(f"Error splitting documents: {e}")
        return None

    try:
        embeddings = GoogleGenerativeAIEmbeddings(model=config.EMBEDDINGS_MODEL_NAME, api_key=config.GOOGLE_API_KEY)
    except Exception as e:
        logger.error(f"Error creating embeddings: {e}")
        return None

    try:
        # Use the v4 client with langchain-weaviate
        client = weaviate.connect_to_local()
        vectorstore = WeaviateVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            client=client,
            index_name="Documents",
            text_key="text"
        )
        client.close()
    except Exception as e:
        logger.error(f"Error creating vectorstore: {e}")
        return None

    logger.info(f"Loaded {len(chunks)} chunks into vectorstore")
    return vectorstore

if __name__ == "__main__":
    load_documents("documents/*.pdf")