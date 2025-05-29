from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentLoader:
    def load_and_split(self, text: str) -> List[Document]:
        """Split text into chunks for embedding."""
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=512,
                chunk_overlap=50
            )
            return text_splitter.create_documents([text])
        except Exception as e:
            logger.error(f"Error splitting text: {str(e)}")
            return []