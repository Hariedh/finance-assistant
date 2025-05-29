from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetrieverAgent:
    def __init__(self):
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            self.vector_store = None
        except Exception as e:
            logger.error(f"Error initializing retriever: {str(e)}")
            self.embeddings = None

    def index_documents(self, documents: List[Document]) -> None:
        """Index documents using FAISS."""
        try:
            if documents and self.embeddings:
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
            else:
                logger.warning("No documents or embeddings available for indexing")
        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")

    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve top-k relevant documents."""
        try:
            if self.vector_store:
                return self.vector_store.similarity_search(query, k=k)
            return []
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []