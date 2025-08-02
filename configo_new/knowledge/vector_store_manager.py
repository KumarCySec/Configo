"""
CONFIGO Vector Store Manager
===========================

Handles vector database operations for CONFIGO.
Provides semantic search capabilities for error matching and tool similarity.
"""

import logging
import json
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Vector database manager for CONFIGO.
    
    Handles semantic search, error matching, and tool similarity
    using ChromaDB or FAISS for intelligent decision making.
    """
    
    def __init__(self, storage_path: str = ".configo_vectors", mode: str = "chroma"):
        """Initialize the vector store manager."""
        self.storage_path = Path(storage_path)
        self.mode = mode
        self.client = None
        self.collection = None
        self.embedder = None
        
        self.storage_path.mkdir(exist_ok=True)
        self._initialize_vector_store()
        logger.info("CONFIGO Vector Store Manager initialized")
    
    def _initialize_vector_store(self) -> None:
        """Initialize the vector database (ChromaDB or FAISS)."""
        try:
            if self.mode == "chroma":
                self._initialize_chroma()
            elif self.mode == "faiss":
                self._initialize_faiss()
            else:
                logger.warning(f"Unknown vector mode: {self.mode}, using fallback")
                self._initialize_fallback()
        except Exception as e:
            logger.warning(f"Failed to initialize vector store: {e}")
            self._initialize_fallback()
    
    def _initialize_chroma(self) -> None:
        """Initialize ChromaDB vector store."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(self.storage_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="configo_knowledge",
                metadata={"description": "CONFIGO knowledge base"}
            )
            
            logger.info("ChromaDB vector store initialized")
        except ImportError:
            logger.warning("ChromaDB not available - using fallback")
            self._initialize_fallback()
        except Exception as e:
            logger.warning(f"Failed to initialize ChromaDB: {e}")
            self._initialize_fallback()
    
    def _initialize_faiss(self) -> None:
        """Initialize FAISS vector store."""
        try:
            import faiss
            import numpy as np
            from sentence_transformers import SentenceTransformer
            
            # Initialize sentence transformer
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize FAISS index
            dimension = self.embedder.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatIP(dimension)
            
            # Load existing data if available
            self._load_faiss_data()
            
            logger.info("FAISS vector store initialized")
        except ImportError:
            logger.warning("FAISS not available - using fallback")
            self._initialize_fallback()
        except Exception as e:
            logger.warning(f"Failed to initialize FAISS: {e}")
            self._initialize_fallback()
    
    def _initialize_fallback(self) -> None:
        """Initialize fallback vector store (simple keyword-based)."""
        self.mode = "fallback"
        self.documents = []
        self.document_metadata = {}
        logger.info("Using fallback vector store")
    
    def _load_faiss_data(self) -> None:
        """Load existing FAISS data from disk."""
        try:
            index_file = self.storage_path / "faiss_index.bin"
            metadata_file = self.storage_path / "faiss_metadata.json"
            
            if index_file.exists() and metadata_file.exists():
                # Load index
                self.index = faiss.read_index(str(index_file))
                
                # Load metadata
                with open(metadata_file, 'r') as f:
                    self.document_metadata = json.load(f)
                
                logger.info("Loaded existing FAISS data")
        except Exception as e:
            logger.warning(f"Failed to load FAISS data: {e}")
    
    def _save_faiss_data(self) -> None:
        """Save FAISS data to disk."""
        try:
            if hasattr(self, 'index'):
                # Save index
                faiss.write_index(self.index, str(self.storage_path / "faiss_index.bin"))
                
                # Save metadata
                with open(self.storage_path / "faiss_metadata.json", 'w') as f:
                    json.dump(self.document_metadata, f, indent=2)
                
                logger.info("Saved FAISS data")
        except Exception as e:
            logger.warning(f"Failed to save FAISS data: {e}")
    
    def add_document(self, content: str, metadata: Dict[str, Any]) -> bool:
        """
        Add a document to the vector store.
        
        Args:
            content: Document content
            metadata: Document metadata
            
        Returns:
            bool: Success status
        """
        try:
            if self.mode == "chroma":
                return self._add_document_chroma(content, metadata)
            elif self.mode == "faiss":
                return self._add_document_faiss(content, metadata)
            else:
                return self._add_document_fallback(content, metadata)
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    def _add_document_chroma(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Add document to ChromaDB."""
        try:
            # Generate document ID
            doc_id = hashlib.md5(content.encode()).hexdigest()
            
            # Add to collection
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Added document to ChromaDB: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add document to ChromaDB: {e}")
            return False
    
    def _add_document_faiss(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Add document to FAISS."""
        try:
            # Generate embedding
            embedding = self.embedder.encode([content])[0]
            
            # Add to index
            self.index.add(embedding.reshape(1, -1))
            
            # Store metadata
            doc_id = hashlib.md5(content.encode()).hexdigest()
            self.document_metadata[doc_id] = {
                'content': content,
                'metadata': metadata,
                'index': len(self.document_metadata)
            }
            
            # Save data
            self._save_faiss_data()
            
            logger.info(f"Added document to FAISS: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add document to FAISS: {e}")
            return False
    
    def _add_document_fallback(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Add document to fallback store."""
        try:
            doc_id = hashlib.md5(content.encode()).hexdigest()
            
            self.documents.append(content)
            self.document_metadata[doc_id] = {
                'content': content,
                'metadata': metadata,
                'index': len(self.documents) - 1
            }
            
            logger.info(f"Added document to fallback store: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add document to fallback store: {e}")
            return False
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents using semantic similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Search results
        """
        try:
            if self.mode == "chroma":
                return self._search_chroma(query, limit)
            elif self.mode == "faiss":
                return self._search_faiss(query, limit)
            else:
                return self._search_fallback(query, limit)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def _search_chroma(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search in ChromaDB."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            search_results = []
            for i in range(len(results['documents'][0])):
                search_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else 0.0
                })
            
            return search_results
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []
    
    def _search_faiss(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search in FAISS."""
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode([query])[0]
            
            # Search in index
            distances, indices = self.index.search(
                query_embedding.reshape(1, -1), 
                min(limit, self.index.ntotal)
            )
            
            search_results = []
            for i, (distance, index) in enumerate(zip(distances[0], indices[0])):
                if index < len(self.document_metadata):
                    # Find document by index
                    for doc_id, doc_info in self.document_metadata.items():
                        if doc_info['index'] == index:
                            search_results.append({
                                'content': doc_info['content'],
                                'metadata': doc_info['metadata'],
                                'distance': float(distance)
                            })
                            break
            
            return search_results
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return []
    
    def _search_fallback(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search in fallback store."""
        try:
            query_lower = query.lower()
            results = []
            
            for doc_id, doc_info in self.document_metadata.items():
                content = doc_info['content'].lower()
                metadata = doc_info['metadata']
                
                # Simple keyword matching
                if query_lower in content:
                    score = content.count(query_lower) / len(content)
                    results.append({
                        'content': doc_info['content'],
                        'metadata': metadata,
                        'distance': 1.0 - score  # Convert to distance
                    })
            
            # Sort by distance (lower is better)
            results.sort(key=lambda x: x['distance'])
            return results[:limit]
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return []
    
    def search_error(self, error_message: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar error messages and their solutions.
        
        Args:
            error_message: Error message to search for
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Error search results
        """
        try:
            # Add error context to query
            query = f"error: {error_message}"
            results = self.search(query, limit)
            
            # Filter for error-related documents
            error_results = []
            for result in results:
                metadata = result.get('metadata', {})
                if (metadata.get('type') == 'error' or 
                    'error' in result['content'].lower() or
                    'fail' in result['content'].lower()):
                    error_results.append(result)
            
            return error_results
        except Exception as e:
            logger.error(f"Error search failed: {e}")
            return []
    
    def search_similar_errors(self, error_log: str) -> List[Dict[str, Any]]:
        """
        Search for similar errors based on error log.
        
        Args:
            error_log: Error log text
            
        Returns:
            List[Dict[str, Any]]: Similar errors
        """
        return self.search_error(error_log, 5)
    
    def search_similar_tool_requests(self, user_prompt: str) -> List[Dict[str, Any]]:
        """
        Search for similar tool requests based on user prompt.
        
        Args:
            user_prompt: User's tool request
            
        Returns:
            List[Dict[str, Any]]: Similar tool requests
        """
        try:
            query = f"tool request: {user_prompt}"
            results = self.search(query, 5)
            
            # Filter for tool-related documents
            tool_results = []
            for result in results:
                metadata = result.get('metadata', {})
                if (metadata.get('type') == 'tool' or 
                    'tool' in result['content'].lower() or
                    'install' in result['content'].lower()):
                    tool_results.append(result)
            
            return tool_results
        except Exception as e:
            logger.error(f"Tool request search failed: {e}")
            return []
    
    def add_error_knowledge(self, error_message: str, solution: str, 
                           tool_name: str, system_info: Dict[str, Any]) -> bool:
        """
        Add error knowledge to the vector store.
        
        Args:
            error_message: Error message
            solution: Solution or fix
            tool_name: Name of the tool
            system_info: System information
            
        Returns:
            bool: Success status
        """
        try:
            content = f"Error: {error_message}\nSolution: {solution}\nTool: {tool_name}"
            metadata = {
                'type': 'error',
                'tool_name': tool_name,
                'system_info': system_info,
                'timestamp': datetime.now().isoformat()
            }
            
            return self.add_document(content, metadata)
        except Exception as e:
            logger.error(f"Failed to add error knowledge: {e}")
            return False
    
    def add_tool_knowledge(self, tool_name: str, description: str, 
                          category: str, metadata: Dict[str, Any]) -> bool:
        """
        Add tool knowledge to the vector store.
        
        Args:
            tool_name: Name of the tool
            description: Tool description
            category: Tool category
            metadata: Additional metadata
            
        Returns:
            bool: Success status
        """
        try:
            content = f"Tool: {tool_name}\nDescription: {description}\nCategory: {category}"
            metadata = {
                'type': 'tool',
                'name': tool_name,
                'category': category,
                'description': description,
                **metadata
            }
            
            return self.add_document(content, metadata)
        except Exception as e:
            logger.error(f"Failed to add tool knowledge: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        try:
            if self.mode == "chroma":
                return self._get_chroma_stats()
            elif self.mode == "faiss":
                return self._get_faiss_stats()
            else:
                return self._get_fallback_stats()
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'documents': 0, 'status': 'error'}
    
    def _get_chroma_stats(self) -> Dict[str, Any]:
        """Get ChromaDB statistics."""
        try:
            count = self.collection.count()
            return {
                'documents': count,
                'mode': 'chroma',
                'status': 'connected'
            }
        except Exception as e:
            return {'documents': 0, 'mode': 'chroma', 'status': 'error'}
    
    def _get_faiss_stats(self) -> Dict[str, Any]:
        """Get FAISS statistics."""
        try:
            count = self.index.ntotal if hasattr(self.index, 'ntotal') else len(self.document_metadata)
            return {
                'documents': count,
                'mode': 'faiss',
                'status': 'connected'
            }
        except Exception as e:
            return {'documents': 0, 'mode': 'faiss', 'status': 'error'}
    
    def _get_fallback_stats(self) -> Dict[str, Any]:
        """Get fallback store statistics."""
        return {
            'documents': len(self.documents),
            'mode': 'fallback',
            'status': 'connected'
        }
    
    def backup(self, backup_path: Path) -> bool:
        """
        Create a backup of the vector store.
        
        Args:
            backup_path: Path for backup
            
        Returns:
            bool: Success status
        """
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            if self.mode == "chroma":
                # ChromaDB is already persistent
                import shutil
                shutil.copytree(self.storage_path, backup_path / "chroma", dirs_exist_ok=True)
            elif self.mode == "faiss":
                # Save FAISS data
                self._save_faiss_data()
                import shutil
                shutil.copytree(self.storage_path, backup_path / "faiss", dirs_exist_ok=True)
            else:
                # Save fallback data
                with open(backup_path / "fallback_data.json", 'w') as f:
                    json.dump({
                        'documents': self.documents,
                        'metadata': self.document_metadata
                    }, f, indent=2)
            
            logger.info(f"Vector store backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup vector store: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all data from the vector store."""
        try:
            if self.mode == "chroma":
                # Delete collection
                self.client.delete_collection("configo_knowledge")
                self.collection = self.client.create_collection("configo_knowledge")
            elif self.mode == "faiss":
                # Reset index
                dimension = self.embedder.get_sentence_embedding_dimension()
                self.index = faiss.IndexFlatIP(dimension)
                self.document_metadata = {}
                self._save_faiss_data()
            else:
                # Clear fallback data
                self.documents = []
                self.document_metadata = {}
            
            logger.info("Vector store cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            return False 