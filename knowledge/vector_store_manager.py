"""
CONFIGO Vector Store Manager
============================

Vector database manager for semantic search, error matching, and user persona similarity.
Supports Chroma and FAISS with configurable embeddings.

Features:
- 🔍 Semantic search for error messages and tool descriptions
- 🧠 User persona similarity detection
- 📝 Tool description and command embedding
- 🎯 Fuzzy error matching and resolution
- 📊 Similarity-based recommendations
- 🔄 Self-improving search capabilities
"""

import os
import logging
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

# Try to import vector store libraries
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
    logger.info("ChromaDB available - using vector database")
except ImportError:
    CHROMA_AVAILABLE = False
    logger.info("ChromaDB not available - using local vector simulation")

try:
    import faiss
    FAISS_AVAILABLE = True
    logger.info("FAISS available - using vector database")
except ImportError:
    FAISS_AVAILABLE = False
    logger.info("FAISS not available - using local vector simulation")

# Try to import sentence transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    logger.info("Sentence transformers available - using embeddings")
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.info("Sentence transformers not available - using simple text similarity")


@dataclass
class VectorEntry:
    """Represents a vector database entry."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class LocalVectorSimulator:
    """
    Local vector simulator for when Chroma/FAISS is not available.
    
    Simulates vector operations using simple text similarity and JSON storage.
    """
    
    def __init__(self, storage_path: str = ".configo_vectors"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # In-memory vector data
        self.entries: Dict[str, VectorEntry] = {}
        self.collections: Dict[str, List[str]] = {}  # collection_name -> [entry_ids]
        
        self._load_data()
    
    def _load_data(self) -> None:
        """Load vector data from JSON files."""
        try:
            # Load entries
            entries_file = self.storage_path / "entries.json"
            if entries_file.exists():
                with open(entries_file, 'r') as f:
                    data = json.load(f)
                    for entry_id, entry_data in data.items():
                        entry_data['timestamp'] = datetime.fromisoformat(entry_data['timestamp'])
                        self.entries[entry_id] = VectorEntry(**entry_data)
            
            # Load collections
            collections_file = self.storage_path / "collections.json"
            if collections_file.exists():
                with open(collections_file, 'r') as f:
                    self.collections = json.load(f)
                    
        except Exception as e:
            logger.warning(f"Failed to load vector data: {e}")
    
    def _save_data(self) -> None:
        """Save vector data to JSON files."""
        try:
            # Save entries
            entries_data = {}
            for entry_id, entry in self.entries.items():
                entries_data[entry_id] = asdict(entry)
                entries_data[entry_id]['timestamp'] = entry.timestamp.isoformat()
            
            with open(self.storage_path / "entries.json", 'w') as f:
                json.dump(entries_data, f, indent=2)
            
            # Save collections
            with open(self.storage_path / "collections.json", 'w') as f:
                json.dump(self.collections, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save vector data: {e}")
    
    def _simple_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity using word overlap."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _generate_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate a unique ID for an entry."""
        combined = f"{content}:{json.dumps(metadata, sort_keys=True)}"
        return hashlib.md5(combined.encode()).hexdigest()


class VectorStoreManager:
    """
    Vector store manager for CONFIGO knowledge layer.
    
    Handles semantic search, error matching, and similarity detection.
    Falls back to local simulation when Chroma/FAISS is not available.
    """
    
    def __init__(self, storage_path: str = ".configo_vectors", 
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector store manager.
        
        Args:
            storage_path: Local storage path for vector data
            embedding_model: Sentence transformer model name
        """
        self.storage_path = storage_path
        self.embedding_model = embedding_model
        
        # Initialize embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(embedding_model)
                logger.info(f"Loaded embedding model: {embedding_model}")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
                self.model = None
        else:
            self.model = None
        
        # Initialize vector store
        if CHROMA_AVAILABLE:
            self._init_chroma()
        elif FAISS_AVAILABLE:
            self._init_faiss()
        else:
            self._init_local()
    
    def _init_chroma(self) -> None:
        """Initialize ChromaDB."""
        try:
            self.client = chromadb.PersistentClient(
                path=self.storage_path,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collections = {}
            logger.info("Initialized ChromaDB")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self._init_local()
    
    def _init_faiss(self) -> None:
        """Initialize FAISS."""
        try:
            self.index = None
            self.entries = {}
            self.entry_ids = []
            logger.info("Initialized FAISS")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {e}")
            self._init_local()
    
    def _init_local(self) -> None:
        """Initialize local simulator."""
        self.simulator = LocalVectorSimulator(self.storage_path)
        logger.info("Initialized local vector simulator")
    
    def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None,
                    collection_name: str = "default") -> str:
        """
        Add a document to the vector store.
        
        Args:
            content: Document content
            metadata: Optional metadata
            collection_name: Collection name
            
        Returns:
            str: Document ID
        """
        if metadata is None:
            metadata = {}
        
        if hasattr(self, 'client'):  # ChromaDB
            return self._add_document_chroma(content, metadata, collection_name)
        elif hasattr(self, 'index'):  # FAISS
            return self._add_document_faiss(content, metadata, collection_name)
        else:  # Local
            return self._add_document_local(content, metadata, collection_name)
    
    def _add_document_chroma(self, content: str, metadata: Dict[str, Any], 
                            collection_name: str) -> str:
        """Add document to ChromaDB."""
        try:
            if collection_name not in self.collections:
                self.collections[collection_name] = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": f"CONFIGO {collection_name} collection"}
                )
            
            collection = self.collections[collection_name]
            
            # Generate embedding if model is available
            if self.model:
                embedding = self.model.encode(content).tolist()
            else:
                embedding = None
            
            # Add document
            result = collection.add(
                documents=[content],
                metadatas=[metadata],
                embeddings=[embedding] if embedding else None
            )
            
            return result['ids'][0]
        except Exception as e:
            logger.error(f"Failed to add document to ChromaDB: {e}")
            return ""
    
    def _add_document_faiss(self, content: str, metadata: Dict[str, Any], 
                           collection_name: str) -> str:
        """Add document to FAISS."""
        try:
            # Generate embedding
            if self.model:
                embedding = self.model.encode(content)
            else:
                # Simple embedding using character frequencies
                embedding = self._simple_embedding(content)
            
            # Initialize index if needed
            if self.index is None:
                dimension = len(embedding)
                self.index = faiss.IndexFlatL2(dimension)
            
            # Add to index
            self.index.add(np.array([embedding]))
            
            # Store entry
            entry_id = hashlib.md5(content.encode()).hexdigest()
            self.entries[entry_id] = VectorEntry(
                id=entry_id,
                content=content,
                metadata=metadata,
                embedding=embedding.tolist()
            )
            self.entry_ids.append(entry_id)
            
            return entry_id
        except Exception as e:
            logger.error(f"Failed to add document to FAISS: {e}")
            return ""
    
    def _add_document_local(self, content: str, metadata: Dict[str, Any], 
                           collection_name: str) -> str:
        """Add document to local simulator."""
        try:
            entry_id = self.simulator._generate_id(content, metadata)
            
            entry = VectorEntry(
                id=entry_id,
                content=content,
                metadata=metadata
            )
            
            self.simulator.entries[entry_id] = entry
            
            if collection_name not in self.simulator.collections:
                self.simulator.collections[collection_name] = []
            
            if entry_id not in self.simulator.collections[collection_name]:
                self.simulator.collections[collection_name].append(entry_id)
            
            self.simulator._save_data()
            return entry_id
        except Exception as e:
            logger.error(f"Failed to add document locally: {e}")
            return ""
    
    def _simple_embedding(self, text: str) -> np.ndarray:
        """Generate simple embedding using character frequencies."""
        # Create a simple embedding based on character frequencies
        char_freq = {}
        for char in text.lower():
            if char.isalnum():
                char_freq[char] = char_freq.get(char, 0) + 1
        
        # Normalize to 128 dimensions
        embedding = np.zeros(128)
        for i, (char, freq) in enumerate(char_freq.items()):
            if i < 128:
                embedding[i] = freq
        
        return embedding / (np.linalg.norm(embedding) + 1e-8)
    
    def search(self, query: str, collection_name: str = "default", 
              limit: int = 5, similarity_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            collection_name: Collection to search in
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List[Dict[str, Any]]: Search results with content, metadata, and similarity score
        """
        if hasattr(self, 'client'):  # ChromaDB
            return self._search_chroma(query, collection_name, limit, similarity_threshold)
        elif hasattr(self, 'index'):  # FAISS
            return self._search_faiss(query, collection_name, limit, similarity_threshold)
        else:  # Local
            return self._search_local(query, collection_name, limit, similarity_threshold)
    
    def _search_chroma(self, query: str, collection_name: str, 
                      limit: int, similarity_threshold: float) -> List[Dict[str, Any]]:
        """Search in ChromaDB."""
        try:
            if collection_name not in self.collections:
                return []
            
            collection = self.collections[collection_name]
            
            # Generate query embedding
            if self.model:
                query_embedding = self.model.encode(query).tolist()
            else:
                query_embedding = None
            
            # Search
            result = collection.query(
                query_embeddings=[query_embedding] if query_embedding else None,
                query_texts=[query] if not query_embedding else None,
                n_results=limit
            )
            
            results = []
            for i in range(len(result['ids'][0])):
                similarity = 1.0 - result['distances'][0][i]  # Convert distance to similarity
                if similarity >= similarity_threshold:
                    results.append({
                        'id': result['ids'][0][i],
                        'content': result['documents'][0][i],
                        'metadata': result['metadatas'][0][i],
                        'similarity': similarity
                    })
            
            return results
        except Exception as e:
            logger.error(f"Failed to search in ChromaDB: {e}")
            return []
    
    def _search_faiss(self, query: str, collection_name: str, 
                     limit: int, similarity_threshold: float) -> List[Dict[str, Any]]:
        """Search in FAISS."""
        try:
            if self.index is None:
                return []
            
            # Generate query embedding
            if self.model:
                query_embedding = self.model.encode(query)
            else:
                query_embedding = self._simple_embedding(query)
            
            # Search
            distances, indices = self.index.search(
                np.array([query_embedding]), min(limit, len(self.entry_ids))
            )
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.entry_ids):
                    entry_id = self.entry_ids[idx]
                    entry = self.entries.get(entry_id)
                    if entry:
                        similarity = 1.0 / (1.0 + distance)  # Convert distance to similarity
                        if similarity >= similarity_threshold:
                            results.append({
                                'id': entry_id,
                                'content': entry.content,
                                'metadata': entry.metadata,
                                'similarity': similarity
                            })
            
            return results
        except Exception as e:
            logger.error(f"Failed to search in FAISS: {e}")
            return []
    
    def _search_local(self, query: str, collection_name: str, 
                     limit: int, similarity_threshold: float) -> List[Dict[str, Any]]:
        """Search in local simulator."""
        try:
            if collection_name not in self.simulator.collections:
                return []
            
            results = []
            for entry_id in self.simulator.collections[collection_name]:
                entry = self.simulator.entries.get(entry_id)
                if entry:
                    similarity = self.simulator._simple_similarity(query, entry.content)
                    if similarity >= similarity_threshold:
                        results.append({
                            'id': entry_id,
                            'content': entry.content,
                            'metadata': entry.metadata,
                            'similarity': similarity
                        })
            
            # Sort by similarity and limit results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:limit]
        except Exception as e:
            logger.error(f"Failed to search locally: {e}")
            return []
    
    def add_error_message(self, error_message: str, tool_name: str, 
                         os_type: str, architecture: str, 
                         solution: Optional[str] = None) -> str:
        """
        Add an error message to the vector store.
        
        Args:
            error_message: Error message text
            tool_name: Name of the tool that generated the error
            os_type: Operating system type
            architecture: System architecture
            solution: Optional solution for the error
            
        Returns:
            str: Document ID
        """
        metadata = {
            'type': 'error',
            'tool_name': tool_name,
            'os_type': os_type,
            'architecture': architecture,
            'timestamp': datetime.now().isoformat()
        }
        
        if solution:
            content = f"Error: {error_message}\nSolution: {solution}"
            metadata['solution'] = solution
        else:
            content = f"Error: {error_message}"
        
        return self.add_document(content, metadata, "errors")
    
    def search_similar_errors(self, error_message: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar error messages.
        
        Args:
            error_message: Error message to search for
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Similar errors with solutions
        """
        return self.search(error_message, "errors", limit, similarity_threshold=0.3)
    
    def add_tool_description(self, tool_name: str, description: str, 
                           category: str, install_command: str) -> str:
        """
        Add a tool description to the vector store.
        
        Args:
            tool_name: Name of the tool
            description: Tool description
            category: Tool category
            install_command: Installation command
            
        Returns:
            str: Document ID
        """
        content = f"Tool: {tool_name}\nDescription: {description}\nCategory: {category}\nInstall: {install_command}"
        metadata = {
            'type': 'tool',
            'tool_name': tool_name,
            'category': category,
            'install_command': install_command
        }
        
        return self.add_document(content, metadata, "tools")
    
    def search_similar_tools(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar tools.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Similar tools
        """
        return self.search(query, "tools", limit, similarity_threshold=0.4)
    
    def add_user_persona(self, user_id: str, persona_description: str, 
                         preferences: Dict[str, Any]) -> str:
        """
        Add a user persona to the vector store.
        
        Args:
            user_id: User ID
            persona_description: Description of the user persona
            preferences: User preferences
            
        Returns:
            str: Document ID
        """
        content = f"User: {user_id}\nPersona: {persona_description}\nPreferences: {json.dumps(preferences)}"
        metadata = {
            'type': 'user_persona',
            'user_id': user_id,
            'preferences': preferences
        }
        
        return self.add_document(content, metadata, "personas")
    
    def find_similar_users(self, persona_description: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find users with similar personas.
        
        Args:
            persona_description: Description of the user persona
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Similar users
        """
        return self.search(persona_description, "personas", limit, similarity_threshold=0.5)
    
    def get_collection_stats(self, collection_name: str = "default") -> Dict[str, Any]:
        """
        Get statistics for a collection.
        
        Args:
            collection_name: Collection name
            
        Returns:
            Dict[str, Any]: Collection statistics
        """
        if hasattr(self, 'client'):  # ChromaDB
            return self._get_collection_stats_chroma(collection_name)
        elif hasattr(self, 'index'):  # FAISS
            return self._get_collection_stats_faiss(collection_name)
        else:  # Local
            return self._get_collection_stats_local(collection_name)
    
    def _get_collection_stats_chroma(self, collection_name: str) -> Dict[str, Any]:
        """Get collection stats from ChromaDB."""
        try:
            if collection_name not in self.collections:
                return {'count': 0}
            
            collection = self.collections[collection_name]
            count = collection.count()
            
            return {
                'count': count,
                'collection_name': collection_name
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats from ChromaDB: {e}")
            return {'count': 0}
    
    def _get_collection_stats_faiss(self, collection_name: str) -> Dict[str, Any]:
        """Get collection stats from FAISS."""
        try:
            count = len(self.entries)
            
            return {
                'count': count,
                'collection_name': collection_name,
                'index_size': self.index.ntotal if self.index else 0
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats from FAISS: {e}")
            return {'count': 0}
    
    def _get_collection_stats_local(self, collection_name: str) -> Dict[str, Any]:
        """Get collection stats from local simulator."""
        try:
            count = len(self.simulator.collections.get(collection_name, []))
            
            return {
                'count': count,
                'collection_name': collection_name
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats locally: {e}")
            return {'count': 0} 