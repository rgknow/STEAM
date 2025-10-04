"""
RAG Engine Core
Main engine for retrieval-augmented generation with curriculum and resource integration
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
from datetime import datetime
from uuid import uuid4
import numpy as np
from pathlib import Path
import pickle
import hashlib
from abc import ABC, abstractmethod

# Vector storage and embedding dependencies
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: ChromaDB not available. Install with: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: SentenceTransformers not available. Install with: pip install sentence-transformers")


class VectorStore(ABC):
    """Abstract base class for vector storage implementations."""
    
    @abstractmethod
    async def add_documents(self, documents: List[Dict[str, Any]], collection_name: str):
        pass
    
    @abstractmethod
    async def search(self, query_embedding: List[float], collection_name: str, top_k: int = 10) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def create_collection(self, collection_name: str, metadata: Dict[str, Any] = None):
        pass


class ChromaDBStore(VectorStore):
    """ChromaDB implementation of vector storage."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB not available. Install with: pip install chromadb")
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(allow_reset=True)
        )
        self.collections = {}
    
    async def create_collection(self, collection_name: str, metadata: Dict[str, Any] = None):
        """Create a new collection."""
        try:
            collection = self.client.create_collection(
                name=collection_name,
                metadata=metadata or {}
            )
            self.collections[collection_name] = collection
        except Exception as e:
            # Collection might already exist
            collection = self.client.get_collection(collection_name)
            self.collections[collection_name] = collection
    
    async def add_documents(self, documents: List[Dict[str, Any]], collection_name: str):
        """Add documents to a collection."""
        if collection_name not in self.collections:
            await self.create_collection(collection_name)
        
        collection = self.collections[collection_name]
        
        ids = [doc["id"] for doc in documents]
        embeddings = [doc["embedding"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        documents_text = [doc["text"] for doc in documents]
        
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents_text
        )
    
    async def search(self, query_embedding: List[float], collection_name: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        if collection_name not in self.collections:
            return []
        
        collection = self.collections[collection_name]
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Convert results to standard format
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                result = {
                    "id": results["ids"][0][i],
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"][0] else {},
                    "distance": results["distances"][0][i] if results["distances"] and results["distances"][0] else 0.0
                }
                formatted_results.append(result)
        
        return formatted_results


class InMemoryVectorStore(VectorStore):
    """Simple in-memory vector store for development/testing."""
    
    def __init__(self):
        self.collections = {}
    
    async def create_collection(self, collection_name: str, metadata: Dict[str, Any] = None):
        """Create a new collection."""
        self.collections[collection_name] = {
            "documents": [],
            "metadata": metadata or {}
        }
    
    async def add_documents(self, documents: List[Dict[str, Any]], collection_name: str):
        """Add documents to a collection."""
        if collection_name not in self.collections:
            await self.create_collection(collection_name)
        
        self.collections[collection_name]["documents"].extend(documents)
    
    async def search(self, query_embedding: List[float], collection_name: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search using cosine similarity."""
        if collection_name not in self.collections:
            return []
        
        documents = self.collections[collection_name]["documents"]
        if not documents:
            return []
        
        # Calculate cosine similarities
        query_vector = np.array(query_embedding)
        similarities = []
        
        for doc in documents:
            doc_vector = np.array(doc["embedding"])
            similarity = np.dot(query_vector, doc_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(doc_vector)
            )
            similarities.append((similarity, doc))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # Return top_k results
        results = []
        for similarity, doc in similarities[:top_k]:
            result = {
                "id": doc["id"],
                "text": doc["text"],
                "metadata": doc.get("metadata", {}),
                "distance": 1.0 - similarity  # Convert similarity to distance
            }
            results.append(result)
        
        return results


@dataclass
class DocumentChunk:
    """Represents a chunk of a document for RAG processing."""
    chunk_id: str
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_document: str = ""
    chunk_index: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.chunk_id,
            "text": self.text,
            "embedding": self.embedding,
            "metadata": {
                **self.metadata,
                "source_document": self.source_document,
                "chunk_index": self.chunk_index
            }
        }


@dataclass
class DocumentCollection:
    """Collection of documents for RAG processing."""
    collection_id: str
    name: str
    description: str
    documents: List[DocumentChunk] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_document(self, chunk: DocumentChunk):
        """Add a document chunk to the collection."""
        self.documents.append(chunk)
    
    def get_document_count(self) -> int:
        """Get the number of documents in the collection."""
        return len(self.documents)
    
    def get_metadata_summary(self) -> Dict[str, Any]:
        """Get summary of collection metadata."""
        return {
            "collection_id": self.collection_id,
            "name": self.name,
            "description": self.description,
            "document_count": self.get_document_count(),
            "metadata": self.metadata
        }


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        pass


class SentenceTransformerEmbedding(EmbeddingProvider):
    """SentenceTransformers embedding provider."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("SentenceTransformers not available. Install with: pip install sentence-transformers")
        
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        return self.model.get_sentence_embedding_dimension()


class MockEmbeddingProvider(EmbeddingProvider):
    """Mock embedding provider for testing."""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings."""
        embeddings = []
        for text in texts:
            # Generate deterministic but pseudo-random embeddings based on text hash
            text_hash = hashlib.md5(text.encode()).hexdigest()
            np.random.seed(int(text_hash[:8], 16))  # Use first 8 chars of hash as seed
            embedding = np.random.normal(0, 1, self.dimension).tolist()
            embeddings.append(embedding)
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        return self.dimension


class RAGEngine:
    """Main RAG engine for curriculum and resource retrieval."""
    
    def __init__(self, 
                 vector_store: Optional[VectorStore] = None,
                 embedding_provider: Optional[EmbeddingProvider] = None,
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        
        # Initialize vector store
        if vector_store is None:
            try:
                self.vector_store = ChromaDBStore()
            except ImportError:
                self.vector_store = InMemoryVectorStore()
        else:
            self.vector_store = vector_store
        
        # Initialize embedding provider
        if embedding_provider is None:
            try:
                self.embedding_provider = SentenceTransformerEmbedding()
            except ImportError:
                self.embedding_provider = MockEmbeddingProvider()
        else:
            self.embedding_provider = embedding_provider
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.collections = {}
        
        self.logger = logging.getLogger("rag_engine")
    
    async def create_collection(self, collection_spec: Dict[str, Any]) -> str:
        """Create a new document collection."""
        collection_id = collection_spec.get("collection_id", str(uuid4()))
        
        collection = DocumentCollection(
            collection_id=collection_id,
            name=collection_spec.get("name", "Untitled Collection"),
            description=collection_spec.get("description", ""),
            metadata=collection_spec.get("metadata", {})
        )
        
        self.collections[collection_id] = collection
        
        # Create vector store collection
        await self.vector_store.create_collection(
            collection_name=collection_id,
            metadata=collection.get_metadata_summary()
        )
        
        self.logger.info(f"Created collection: {collection.name} ({collection_id})")
        return collection_id
    
    async def add_documents_to_collection(self, collection_id: str, documents: List[Dict[str, Any]]):
        """Add documents to a collection with chunking and embedding."""
        if collection_id not in self.collections:
            raise ValueError(f"Collection {collection_id} not found")
        
        collection = self.collections[collection_id]
        
        # Process each document
        all_chunks = []
        for doc in documents:
            chunks = await self._process_document(doc, collection_id)
            all_chunks.extend(chunks)
            
            # Add chunks to collection
            for chunk in chunks:
                collection.add_document(chunk)
        
        # Generate embeddings for all chunks
        texts = [chunk.text for chunk in all_chunks]
        embeddings = await self.embedding_provider.generate_embeddings(texts)
        
        # Update chunks with embeddings
        for chunk, embedding in zip(all_chunks, embeddings):
            chunk.embedding = embedding
        
        # Add to vector store
        vector_docs = [chunk.to_dict() for chunk in all_chunks]
        await self.vector_store.add_documents(vector_docs, collection_id)
        
        self.logger.info(f"Added {len(all_chunks)} chunks to collection {collection_id}")
    
    async def _process_document(self, doc: Dict[str, Any], collection_id: str) -> List[DocumentChunk]:
        """Process a single document into chunks."""
        doc_id = doc.get("id", str(uuid4()))
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})
        
        # Simple text chunking (can be enhanced with more sophisticated methods)
        chunks = []
        text = content.strip()
        
        if len(text) <= self.chunk_size:
            # Document is small enough to be a single chunk
            chunk = DocumentChunk(
                chunk_id=f"{doc_id}_0",
                text=text,
                metadata=metadata,
                source_document=doc_id,
                chunk_index=0
            )
            chunks.append(chunk)
        else:
            # Split into overlapping chunks
            start = 0
            chunk_index = 0
            
            while start < len(text):
                end = start + self.chunk_size
                
                # Try to break at sentence boundary
                if end < len(text):
                    # Look for sentence endings near the boundary
                    sentence_end = text.rfind('.', start, end)
                    if sentence_end > start + self.chunk_size // 2:
                        end = sentence_end + 1
                
                chunk_text = text[start:end].strip()
                
                if chunk_text:
                    chunk = DocumentChunk(
                        chunk_id=f"{doc_id}_{chunk_index}",
                        text=chunk_text,
                        metadata=metadata,
                        source_document=doc_id,
                        chunk_index=chunk_index
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Move start position with overlap
                start = max(start + 1, end - self.chunk_overlap)
                
                # Prevent infinite loop
                if start >= len(text):
                    break
        
        return chunks
    
    async def search(self, query: str, collection_ids: Optional[List[str]] = None, top_k: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Search across collections for relevant documents."""
        # Generate query embedding
        query_embeddings = await self.embedding_provider.generate_embeddings([query])
        query_embedding = query_embeddings[0]
        
        # Determine which collections to search
        if collection_ids is None:
            collection_ids = list(self.collections.keys())
        
        results = {}
        
        for collection_id in collection_ids:
            if collection_id in self.collections:
                collection_results = await self.vector_store.search(
                    query_embedding, collection_id, top_k
                )
                results[collection_id] = collection_results
        
        return results
    
    async def get_context_for_query(self, query: str, collection_ids: Optional[List[str]] = None, max_context_length: int = 4000) -> Dict[str, Any]:
        """Get relevant context for a query with length limits."""
        search_results = await self.search(query, collection_ids, top_k=20)
        
        # Combine and rank results from all collections
        all_results = []
        for collection_id, results in search_results.items():
            for result in results:
                result["collection_id"] = collection_id
                all_results.append(result)
        
        # Sort by distance (lower is better)
        all_results.sort(key=lambda x: x.get("distance", 1.0))
        
        # Build context within length limit
        context_chunks = []
        current_length = 0
        
        for result in all_results:
            chunk_text = result["text"]
            chunk_length = len(chunk_text)
            
            if current_length + chunk_length <= max_context_length:
                context_chunks.append({
                    "text": chunk_text,
                    "source": result["metadata"].get("source_document", "unknown"),
                    "collection": result["collection_id"],
                    "relevance_score": 1.0 - result.get("distance", 0.0)
                })
                current_length += chunk_length
            else:
                break
        
        return {
            "query": query,
            "context_chunks": context_chunks,
            "total_context_length": current_length,
            "chunks_used": len(context_chunks),
            "collections_searched": len(search_results)
        }
    
    async def similarity_search_with_metadata(self, query: str, metadata_filters: Dict[str, Any], collection_ids: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search with metadata filtering."""
        # Get basic search results
        results = await self.search(query, collection_ids)
        
        # Filter results based on metadata
        filtered_results = {}
        
        for collection_id, collection_results in results.items():
            filtered_collection_results = []
            
            for result in collection_results:
                result_metadata = result.get("metadata", {})
                
                # Check if result matches all metadata filters
                matches_filters = True
                for filter_key, filter_value in metadata_filters.items():
                    if filter_key not in result_metadata:
                        matches_filters = False
                        break
                    
                    result_value = result_metadata[filter_key]
                    
                    # Support different filter types
                    if isinstance(filter_value, list):
                        # List filter - result value must be in list
                        if result_value not in filter_value:
                            matches_filters = False
                            break
                    elif isinstance(filter_value, dict):
                        # Range filter - supports "min" and "max" keys
                        if "min" in filter_value and result_value < filter_value["min"]:
                            matches_filters = False
                            break
                        if "max" in filter_value and result_value > filter_value["max"]:
                            matches_filters = False
                            break
                    else:
                        # Exact match filter
                        if result_value != filter_value:
                            matches_filters = False
                            break
                
                if matches_filters:
                    filtered_collection_results.append(result)
            
            filtered_results[collection_id] = filtered_collection_results
        
        return filtered_results
    
    def get_collection_info(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a collection."""
        if collection_id not in self.collections:
            return None
        
        collection = self.collections[collection_id]
        return collection.get_metadata_summary()
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections."""
        return [
            collection.get_metadata_summary() 
            for collection in self.collections.values()
        ]
    
    async def delete_collection(self, collection_id: str):
        """Delete a collection."""
        if collection_id in self.collections:
            del self.collections[collection_id]
            # Note: Vector store deletion would depend on implementation
            self.logger.info(f"Deleted collection: {collection_id}")
    
    async def get_collection_statistics(self, collection_id: str) -> Dict[str, Any]:
        """Get detailed statistics for a collection."""
        if collection_id not in self.collections:
            return {"error": "Collection not found"}
        
        collection = self.collections[collection_id]
        
        # Calculate statistics
        total_chunks = len(collection.documents)
        total_text_length = sum(len(chunk.text) for chunk in collection.documents)
        
        # Source document statistics
        source_docs = {}
        for chunk in collection.documents:
            source = chunk.source_document
            if source not in source_docs:
                source_docs[source] = {"chunk_count": 0, "text_length": 0}
            source_docs[source]["chunk_count"] += 1
            source_docs[source]["text_length"] += len(chunk.text)
        
        # Metadata analysis
        metadata_keys = set()
        for chunk in collection.documents:
            metadata_keys.update(chunk.metadata.keys())
        
        return {
            "collection_id": collection_id,
            "collection_name": collection.name,
            "total_chunks": total_chunks,
            "total_text_length": total_text_length,
            "average_chunk_length": total_text_length / max(1, total_chunks),
            "source_documents": len(source_docs),
            "source_document_details": source_docs,
            "metadata_keys": list(metadata_keys),
            "embedding_dimension": self.embedding_provider.get_embedding_dimension()
        }


# Example usage and testing
async def main():
    """Example usage of the RAG engine."""
    print("=== RAG Engine Demo ===")
    
    # Initialize RAG engine
    rag = RAGEngine()
    
    # Create a curriculum collection
    curriculum_collection_id = await rag.create_collection({
        "name": "Elementary STEM Curriculum",
        "description": "Grade-level STEM curriculum resources",
        "metadata": {
            "level": "elementary",
            "subject": "STEM",
            "grade_range": "K-5"
        }
    })
    
    # Add sample curriculum documents
    curriculum_docs = [
        {
            "id": "grade1_science",
            "content": "Grade 1 Science Curriculum: Students will explore basic concepts of living and non-living things. They will observe plants and animals in their environment, identify basic needs of living things, and understand seasonal changes. Through hands-on activities, students will develop observation skills and begin to ask scientific questions about the world around them.",
            "metadata": {
                "grade": 1,
                "subject": "science",
                "topic": "living_things",
                "standards": ["NGSS K-LS1-1", "NGSS 1-LS1-1"]
            }
        },
        {
            "id": "grade2_math",
            "content": "Grade 2 Mathematics: Addition and subtraction within 100. Students will use various strategies including counting on, making ten, decomposing numbers, and using the relationship between addition and subtraction. They will solve word problems involving adding to, taking from, putting together, taking apart, and comparing situations.",
            "metadata": {
                "grade": 2,
                "subject": "mathematics",
                "topic": "addition_subtraction",
                "standards": ["CCSS.MATH.2.OA.A.1", "CCSS.MATH.2.NBT.B.5"]
            }
        },
        {
            "id": "grade3_engineering",
            "content": "Grade 3 Engineering Design: Students will define simple design problems and generate solutions. They will plan and carry out investigations to determine which materials work best for intended purposes. Students will analyze data from tests to determine how well a solution meets specified criteria and constraints.",
            "metadata": {
                "grade": 3,
                "subject": "engineering",
                "topic": "design_process",
                "standards": ["NGSS 3-5-ETS1-1", "NGSS 3-5-ETS1-2"]
            }
        }
    ]
    
    await rag.add_documents_to_collection(curriculum_collection_id, curriculum_docs)
    
    # Create resource library collection
    resource_collection_id = await rag.create_collection({
        "name": "Teaching Resources",
        "description": "User guides and documentation for educators",
        "metadata": {
            "type": "resources",
            "audience": "educators"
        }
    })
    
    # Add resource documents
    resource_docs = [
        {
            "id": "classroom_management",
            "content": "Effective Classroom Management Strategies: Establish clear expectations and routines from the first day. Use positive reinforcement to encourage desired behaviors. Create a classroom environment that supports learning through organized spaces and accessible materials. Implement consistent consequences for inappropriate behavior while maintaining respect for all students.",
            "metadata": {
                "category": "classroom_management",
                "audience": "teachers",
                "experience_level": "all"
            }
        },
        {
            "id": "stem_activities",
            "content": "Hands-On STEM Activities: Design challenges that encourage problem-solving and creativity. Use everyday materials to build bridges, towers, and simple machines. Incorporate measurement, data collection, and analysis into activities. Connect STEM concepts to real-world applications that students can relate to their daily lives.",
            "metadata": {
                "category": "activities",
                "subject": "STEM",
                "age_group": "elementary"
            }
        }
    ]
    
    await rag.add_documents_to_collection(resource_collection_id, resource_docs)
    
    # Test searches
    print("\n--- Testing Curriculum Search ---")
    query1 = "What should Grade 2 students learn about math?"
    results1 = await rag.search(query1, [curriculum_collection_id])
    print(f"Query: {query1}")
    for collection_id, collection_results in results1.items():
        for result in collection_results[:2]:  # Show top 2 results
            print(f"  - {result['metadata'].get('subject', 'Unknown')}: {result['text'][:100]}...")
    
    print("\n--- Testing Resource Search ---")
    query2 = "How to manage a classroom effectively?"
    results2 = await rag.search(query2, [resource_collection_id])
    print(f"Query: {query2}")
    for collection_id, collection_results in results2.items():
        for result in collection_results[:2]:
            print(f"  - {result['metadata'].get('category', 'Unknown')}: {result['text'][:100]}...")
    
    print("\n--- Testing Cross-Collection Search ---")
    query3 = "STEM activities for elementary students"
    results3 = await rag.search(query3)  # Search all collections
    print(f"Query: {query3}")
    for collection_id, collection_results in results3.items():
        print(f"Collection: {rag.collections[collection_id].name}")
        for result in collection_results[:1]:
            print(f"  - {result['text'][:100]}...")
    
    print("\n--- Testing Context Generation ---")
    context = await rag.get_context_for_query("Grade 3 engineering design activities")
    print(f"Context for: {context['query']}")
    print(f"Chunks used: {context['chunks_used']}")
    print(f"Context length: {context['total_context_length']} characters")
    
    print("\n--- Collection Statistics ---")
    stats = await rag.get_collection_statistics(curriculum_collection_id)
    print(f"Collection: {stats['collection_name']}")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Source documents: {stats['source_documents']}")
    print(f"Average chunk length: {stats['average_chunk_length']:.1f} characters")
    
    print("\n=== RAG Engine Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())