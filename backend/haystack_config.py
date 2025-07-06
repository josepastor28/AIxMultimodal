from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import PreProcessor, EmbeddingRetriever
from haystack.nodes.retriever import BM25Retriever
from haystack.pipelines import DocumentSearchPipeline
from haystack.schema import Document
import os
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeBaseManager:
    def __init__(self):
        """Initialize the knowledge base with Haystack and Elasticsearch"""
        self.document_store = None
        self.preprocessor = None
        self.retriever = None
        self.search_pipeline = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize Haystack components"""
        try:
            # Initialize Elasticsearch document store
            self.document_store = ElasticsearchDocumentStore(
                host="localhost",
                port=9200,
                username="",
                password="",
                index="knowledge_base",
                similarity="cosine",
                embedding_dim=768
            )
            logger.info("✅ Elasticsearch document store initialized")
            
            # Initialize preprocessor for document processing
            self.preprocessor = PreProcessor(
                clean_empty_lines=True,
                clean_whitespace=True,
                clean_header_footer=True,
                split_by="word",
                split_length=500,
                split_overlap=50
            )
            logger.info("✅ Document preprocessor initialized")
            
            # Initialize BM25 retriever for keyword-based search
            self.retriever = BM25Retriever(document_store=self.document_store)
            logger.info("✅ BM25 retriever initialized")
            
            # Create search pipeline
            self.search_pipeline = DocumentSearchPipeline(self.retriever)
            logger.info("✅ Search pipeline initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Haystack components: {e}")
            # Fallback to in-memory document store for development
            self._initialize_fallback()
    
    def _initialize_fallback(self):
        """Initialize fallback components for development"""
        try:
            from haystack.document_stores import InMemoryDocumentStore
            
            self.document_store = InMemoryDocumentStore(
                embedding_dim=768,
                similarity="cosine",
                use_bm25=True
            )
            logger.info("✅ Fallback to InMemory document store")
            
            self.preprocessor = PreProcessor(
                clean_empty_lines=True,
                clean_whitespace=True,
                clean_header_footer=True,
                split_by="word",
                split_length=500,
                split_overlap=50
            )
            
            self.retriever = BM25Retriever(document_store=self.document_store)
            self.search_pipeline = DocumentSearchPipeline(self.retriever)
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize fallback components: {e}")
    
    def add_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """Add documents to the knowledge base"""
        try:
            # Preprocess documents
            processed_docs = self.preprocessor.process(documents)
            
            # Write to document store
            self.document_store.write_documents(processed_docs)
            
            logger.info(f"✅ Added {len(processed_docs)} processed documents to knowledge base")
            
            return {
                "success": True,
                "message": f"Successfully added {len(processed_docs)} documents",
                "document_count": len(processed_docs)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to add documents: {e}")
            return {
                "success": False,
                "message": f"Failed to add documents: {str(e)}",
                "document_count": 0
            }
    
    def search_documents(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search documents in the knowledge base"""
        try:
            # Perform search
            results = self.search_pipeline.run(query=query, params={"Retriever": {"top_k": top_k}})
            
            # Extract relevant information from results
            documents = []
            for doc in results["documents"]:
                documents.append({
                    "content": doc.content,
                    "meta": doc.meta,
                    "score": doc.score if hasattr(doc, 'score') else None
                })
            
            logger.info(f"✅ Search completed for query: '{query}' - Found {len(documents)} documents")
            
            return {
                "success": True,
                "query": query,
                "documents": documents,
                "total_results": len(documents)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to search documents: {e}")
            return {
                "success": False,
                "message": f"Failed to search documents: {str(e)}",
                "query": query,
                "documents": [],
                "total_results": 0
            }
    
    def get_document_count(self) -> int:
        """Get total number of documents in the knowledge base"""
        try:
            return self.document_store.get_document_count()
        except Exception as e:
            logger.error(f"❌ Failed to get document count: {e}")
            return 0
    
    def clear_documents(self) -> Dict[str, Any]:
        """Clear all documents from the knowledge base"""
        try:
            self.document_store.delete_documents()
            logger.info("✅ Cleared all documents from knowledge base")
            
            return {
                "success": True,
                "message": "Successfully cleared all documents"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to clear documents: {e}")
            return {
                "success": False,
                "message": f"Failed to clear documents: {str(e)}"
            }

# Global instance
knowledge_base = KnowledgeBaseManager() 