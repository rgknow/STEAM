"""
Embedding Manager
Manages embeddings, vector operations, and semantic similarity for the RAG system
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
from datetime import datetime
import numpy as np
from pathlib import Path
import pickle
import hashlib
from abc import ABC, abstractmethod

# Advanced embedding dependencies
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class EmbeddingModel(Enum):
    """Available embedding models."""
    # Sentence Transformers models
    ALL_MINILM_L6_V2 = "all-MiniLM-L6-v2"              # General purpose, fast
    ALL_MPNET_BASE_V2 = "all-mpnet-base-v2"            # Better quality, slower
    ALL_DISTILROBERTA_V1 = "all-distilroberta-v1"      # Good balance
    
    # Educational domain models
    SENTENCE_T5_BASE = "sentence-t5-base"               # Good for educational content
    PARAPHRASE_MULTILINGUAL = "paraphrase-multilingual-MiniLM-L12-v2"  # Multi-language
    
    # OpenAI models
    OPENAI_ADA_002 = "text-embedding-ada-002"          # OpenAI's embedding model
    
    # Custom educational models (placeholder)
    EDUCATIONAL_BERT = "educational-bert"               # Hypothetical edu-specific model
    CURRICULUM_EMBEDDINGS = "curriculum-embeddings"    # Hypothetical curriculum model


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model_name: EmbeddingModel
    dimension: int
    max_sequence_length: int = 512
    batch_size: int = 32
    normalize_embeddings: bool = True
    cache_embeddings: bool = True
    device: str = "cpu"  # "cpu", "cuda", "mps"
    
    # Performance settings
    use_fp16: bool = False
    enable_pooling: bool = True
    pooling_strategy: str = "mean"  # "mean", "max", "cls"
    
    # Domain-specific settings
    domain_adaptation: bool = False
    fine_tuned_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        return result


@dataclass
class EmbeddingResult:
    """Result of embedding generation."""
    text: str
    embedding: List[float]
    model_name: str
    dimension: int
    
    # Metadata
    token_count: Optional[int] = None
    processing_time: Optional[float] = None
    cached: bool = False
    
    # Quality metrics
    confidence_score: Optional[float] = None
    semantic_density: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "embedding": self.embedding,
            "model_name": self.model_name,
            "dimension": self.dimension,
            "token_count": self.token_count,
            "processing_time": self.processing_time,
            "cached": self.cached,
            "confidence_score": self.confidence_score,
            "semantic_density": self.semantic_density
        }


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[EmbeddingResult]:
        """Generate embeddings for a list of texts."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get model name."""
        pass
    
    @abstractmethod
    async def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate similarity between two embeddings."""
        pass


class SentenceTransformerProvider(EmbeddingProvider):
    """Sentence Transformers embedding provider."""
    
    def __init__(self, config: EmbeddingConfig):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("SentenceTransformers not available. Install with: pip install sentence-transformers")
        
        self.config = config
        self.model = SentenceTransformer(config.model_name.value)
        
        # Configure device
        if config.device != "cpu" and torch.cuda.is_available():
            self.model = self.model.to(config.device)
        
        self.logger = logging.getLogger("sentence_transformer_provider")
    
    async def generate_embeddings(self, texts: List[str]) -> List[EmbeddingResult]:
        """Generate embeddings using SentenceTransformers."""
        
        start_time = datetime.now()
        
        # Generate embeddings in batches
        all_embeddings = []
        batch_size = self.config.batch_size
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Generate embeddings for batch
            batch_embeddings = self.model.encode(
                batch_texts,
                batch_size=len(batch_texts),
                show_progress_bar=False,
                convert_to_tensor=False,
                normalize_embeddings=self.config.normalize_embeddings
            )
            
            all_embeddings.extend(batch_embeddings)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Create results
        results = []
        for text, embedding in zip(texts, all_embeddings):
            result = EmbeddingResult(
                text=text,
                embedding=embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
                model_name=self.config.model_name.value,
                dimension=len(embedding),
                token_count=len(text.split()),  # Rough approximation
                processing_time=processing_time / len(texts),
                cached=False
            )
            results.append(result)
        
        return results
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()
    
    def get_model_name(self) -> str:
        """Get model name."""
        return self.config.model_name.value
    
    async def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider."""
    
    def __init__(self, config: EmbeddingConfig, api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI not available. Install with: pip install openai")
        
        self.config = config
        if api_key:
            openai.api_key = api_key
        
        self.logger = logging.getLogger("openai_embedding_provider")
    
    async def generate_embeddings(self, texts: List[str]) -> List[EmbeddingResult]:
        """Generate embeddings using OpenAI API."""
        
        start_time = datetime.now()
        
        try:
            response = await openai.Embedding.acreate(
                input=texts,
                model=self.config.model_name.value
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            results = []
            for i, text in enumerate(texts):
                embedding_data = response['data'][i]
                
                result = EmbeddingResult(
                    text=text,
                    embedding=embedding_data['embedding'],
                    model_name=self.config.model_name.value,
                    dimension=len(embedding_data['embedding']),
                    token_count=None,  # OpenAI doesn't return token count in embedding response
                    processing_time=processing_time / len(texts),
                    cached=False
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"OpenAI embedding generation failed: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension for OpenAI models."""
        if self.config.model_name == EmbeddingModel.OPENAI_ADA_002:
            return 1536
        return 1536  # Default
    
    def get_model_name(self) -> str:
        """Get model name."""
        return self.config.model_name.value
    
    async def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)


class MockEmbeddingProvider(EmbeddingProvider):
    """Mock embedding provider for testing."""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.dimension = config.dimension
        
    async def generate_embeddings(self, texts: List[str]) -> List[EmbeddingResult]:
        """Generate mock embeddings."""
        
        results = []
        for text in texts:
            # Generate deterministic but pseudo-random embeddings
            text_hash = hashlib.md5(text.encode()).hexdigest()
            np.random.seed(int(text_hash[:8], 16))
            
            embedding = np.random.normal(0, 1, self.dimension)
            if self.config.normalize_embeddings:
                embedding = embedding / np.linalg.norm(embedding)
            
            result = EmbeddingResult(
                text=text,
                embedding=embedding.tolist(),
                model_name=self.config.model_name.value,
                dimension=self.dimension,
                token_count=len(text.split()),
                processing_time=0.01,  # Mock fast processing
                cached=False
            )
            results.append(result)
        
        return results
    
    def get_dimension(self) -> int:
        return self.dimension
    
    def get_model_name(self) -> str:
        return self.config.model_name.value
    
    async def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)


class EmbeddingCache:
    """Cache for storing and retrieving embeddings."""
    
    def __init__(self, cache_dir: str = "./embedding_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # In-memory cache for quick access
        self.memory_cache: Dict[str, EmbeddingResult] = {}
        self.max_memory_cache_size = 10000
        
        self.logger = logging.getLogger("embedding_cache")
    
    def _get_cache_key(self, text: str, model_name: str) -> str:
        """Generate cache key for text and model."""
        combined = f"{text}::{model_name}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    async def get(self, text: str, model_name: str) -> Optional[EmbeddingResult]:
        """Retrieve cached embedding."""
        
        cache_key = self._get_cache_key(text, model_name)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            result = self.memory_cache[cache_key]
            result.cached = True
            return result
        
        # Check disk cache
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    result = pickle.load(f)
                    result.cached = True
                    
                    # Add to memory cache if space available
                    if len(self.memory_cache) < self.max_memory_cache_size:
                        self.memory_cache[cache_key] = result
                    
                    return result
            except Exception as e:
                self.logger.warning(f"Failed to load cached embedding: {e}")
        
        return None
    
    async def store(self, result: EmbeddingResult):
        """Store embedding in cache."""
        
        cache_key = self._get_cache_key(result.text, result.model_name)
        
        # Store in memory cache
        if len(self.memory_cache) < self.max_memory_cache_size:
            self.memory_cache[cache_key] = result
        
        # Store on disk
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
        except Exception as e:
            self.logger.warning(f"Failed to cache embedding: {e}")
    
    async def clear_cache(self):
        """Clear all cached embeddings."""
        
        # Clear memory cache
        self.memory_cache.clear()
        
        # Clear disk cache
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                cache_file.unlink()
            except Exception as e:
                self.logger.warning(f"Failed to delete cache file {cache_file}: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        
        disk_files = list(self.cache_dir.glob("*.pkl"))
        total_disk_size = sum(f.stat().st_size for f in disk_files)
        
        return {
            "memory_cache_size": len(self.memory_cache),
            "disk_cache_files": len(disk_files),
            "total_disk_size_mb": total_disk_size / (1024 * 1024),
            "cache_directory": str(self.cache_dir)
        }


class EmbeddingManager:
    """Main manager for embedding operations."""
    
    def __init__(self, 
                 config: EmbeddingConfig,
                 provider: Optional[EmbeddingProvider] = None,
                 enable_cache: bool = True):
        
        self.config = config
        self.enable_cache = enable_cache
        
        # Initialize cache
        if enable_cache:
            self.cache = EmbeddingCache()
        else:
            self.cache = None
        
        # Initialize provider
        if provider:
            self.provider = provider
        else:
            self.provider = self._create_default_provider()
        
        self.logger = logging.getLogger("embedding_manager")
        
        # Performance tracking
        self.stats = {
            "total_embeddings_generated": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_processing_time": 0.0
        }
    
    def _create_default_provider(self) -> EmbeddingProvider:
        """Create default embedding provider based on availability."""
        
        if self.config.model_name == EmbeddingModel.OPENAI_ADA_002:
            if OPENAI_AVAILABLE:
                return OpenAIEmbeddingProvider(self.config)
            else:
                self.logger.warning("OpenAI not available, falling back to mock provider")
                return MockEmbeddingProvider(self.config)
        
        else:
            # Try SentenceTransformers first
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                return SentenceTransformerProvider(self.config)
            else:
                self.logger.warning("SentenceTransformers not available, using mock provider")
                return MockEmbeddingProvider(self.config)
    
    async def generate_embeddings(self, texts: List[str]) -> List[EmbeddingResult]:
        """Generate embeddings with caching support."""
        
        start_time = datetime.now()
        
        results = []
        texts_to_process = []
        cached_results = {}
        
        # Check cache for existing embeddings
        if self.cache:
            for i, text in enumerate(texts):
                cached_result = await self.cache.get(text, self.provider.get_model_name())
                if cached_result:
                    cached_results[i] = cached_result
                    self.stats["cache_hits"] += 1
                else:
                    texts_to_process.append((i, text))
                    self.stats["cache_misses"] += 1
        else:
            texts_to_process = list(enumerate(texts))
        
        # Generate embeddings for uncached texts
        if texts_to_process:
            uncached_texts = [text for _, text in texts_to_process]
            new_results = await self.provider.generate_embeddings(uncached_texts)
            
            # Cache new results
            if self.cache:
                for result in new_results:
                    await self.cache.store(result)
            
            # Map results back to original indices
            for (original_index, _), result in zip(texts_to_process, new_results):
                cached_results[original_index] = result
        
        # Assemble final results in original order
        for i in range(len(texts)):
            results.append(cached_results[i])
        
        # Update stats
        processing_time = (datetime.now() - start_time).total_seconds()
        self.stats["total_embeddings_generated"] += len(texts)
        self.stats["total_processing_time"] += processing_time
        
        return results
    
    async def generate_single_embedding(self, text: str) -> EmbeddingResult:
        """Generate embedding for a single text."""
        
        results = await self.generate_embeddings([text])
        return results[0]
    
    async def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        
        results = await self.generate_embeddings([text1, text2])
        embedding1 = results[0].embedding
        embedding2 = results[1].embedding
        
        return await self.provider.similarity(embedding1, embedding2)
    
    async def find_most_similar(self, query_text: str, candidate_texts: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """Find most similar texts to a query."""
        
        # Generate embeddings
        all_texts = [query_text] + candidate_texts
        results = await self.generate_embeddings(all_texts)
        
        query_embedding = results[0].embedding
        candidate_embeddings = [result.embedding for result in results[1:]]
        
        # Calculate similarities
        similarities = []
        for i, candidate_embedding in enumerate(candidate_embeddings):
            similarity = await self.provider.similarity(query_embedding, candidate_embedding)
            similarities.append((candidate_texts[i], similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    async def cluster_texts(self, texts: List[str], num_clusters: int = 5) -> Dict[int, List[str]]:
        """Cluster texts based on semantic similarity."""
        
        # Generate embeddings
        results = await self.generate_embeddings(texts)
        embeddings = np.array([result.embedding for result in results])
        
        # Simple k-means clustering (could be enhanced with sklearn)
        from sklearn.cluster import KMeans
        
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(embeddings)
        
        # Group texts by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(texts[i])
        
        return clusters
    
    async def get_text_diversity_score(self, texts: List[str]) -> float:
        """Calculate diversity score for a collection of texts."""
        
        if len(texts) < 2:
            return 0.0
        
        # Generate embeddings
        results = await self.generate_embeddings(texts)
        embeddings = [result.embedding for result in results]
        
        # Calculate pairwise similarities
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = await self.provider.similarity(embeddings[i], embeddings[j])
                similarities.append(similarity)
        
        # Diversity is inverse of average similarity
        avg_similarity = sum(similarities) / len(similarities)
        diversity_score = 1.0 - avg_similarity
        
        return max(0.0, diversity_score)
    
    async def enhance_query(self, original_query: str, context_texts: List[str]) -> str:
        """Enhance query based on semantic context."""
        
        if not context_texts:
            return original_query
        
        # Find most relevant context
        similar_contexts = await self.find_most_similar(original_query, context_texts, top_k=3)
        
        # Extract key terms from similar contexts
        key_terms = []
        for context, similarity in similar_contexts:
            if similarity > 0.7:  # High similarity threshold
                # Simple term extraction (could be enhanced with NLP)
                words = context.split()
                important_words = [w for w in words if len(w) > 4 and w.lower() not in ['the', 'and', 'for', 'with']]
                key_terms.extend(important_words[:3])  # Top 3 words per context
        
        # Enhance query with key terms
        if key_terms:
            unique_terms = list(set(key_terms))[:5]  # Max 5 additional terms
            enhanced_query = f"{original_query} {' '.join(unique_terms)}"
            return enhanced_query
        
        return original_query
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        
        return {
            "model_name": self.provider.get_model_name(),
            "dimension": self.provider.get_dimension(),
            "config": self.config.to_dict(),
            "cache_enabled": self.enable_cache,
            "provider_type": type(self.provider).__name__
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        
        stats = self.stats.copy()
        
        if stats["total_embeddings_generated"] > 0:
            stats["avg_processing_time"] = stats["total_processing_time"] / stats["total_embeddings_generated"]
            stats["cache_hit_rate"] = stats["cache_hits"] / (stats["cache_hits"] + stats["cache_misses"])
        else:
            stats["avg_processing_time"] = 0.0
            stats["cache_hit_rate"] = 0.0
        
        if self.cache:
            stats["cache_stats"] = self.cache.get_cache_stats()
        
        return stats
    
    async def benchmark_model(self, test_texts: List[str]) -> Dict[str, Any]:
        """Benchmark the embedding model performance."""
        
        if not test_texts:
            test_texts = [
                "Introduction to elementary mathematics",
                "Science experiments for middle school students",
                "Advanced robotics programming tutorial",
                "Assessment rubrics for project-based learning",
                "Curriculum standards alignment guide"
            ]
        
        start_time = datetime.now()
        
        # Generate embeddings
        results = await self.generate_embeddings(test_texts)
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Calculate metrics
        avg_dimension = sum(result.dimension for result in results) / len(results)
        avg_processing_time = total_time / len(results)
        
        # Test similarity calculation
        similarity_start = datetime.now()
        similarities = []
        for i in range(min(3, len(results))):
            for j in range(i + 1, min(3, len(results))):
                sim = await self.provider.similarity(results[i].embedding, results[j].embedding)
                similarities.append(sim)
        
        similarity_time = (datetime.now() - similarity_start).total_seconds()
        
        return {
            "model_name": self.provider.get_model_name(),
            "test_text_count": len(test_texts),
            "total_embedding_time": total_time,
            "avg_embedding_time": avg_processing_time,
            "embedding_dimension": int(avg_dimension),
            "similarity_calculations": len(similarities),
            "avg_similarity_time": similarity_time / max(1, len(similarities)),
            "sample_similarities": similarities[:5],
            "throughput_texts_per_second": len(test_texts) / total_time if total_time > 0 else 0
        }


# Example usage and testing
async def main():
    """Example usage of the embedding manager."""
    print("=== Embedding Manager Demo ===")
    
    # Create configuration
    config = EmbeddingConfig(
        model_name=EmbeddingModel.ALL_MINILM_L6_V2,
        dimension=384,
        batch_size=16,
        normalize_embeddings=True,
        cache_embeddings=True
    )
    
    # Initialize manager
    try:
        manager = EmbeddingManager(config)
        print(f"Initialized with model: {manager.get_model_info()['model_name']}")
    except ImportError as e:
        print(f"Using mock provider due to missing dependencies: {e}")
        config.model_name = EmbeddingModel.ALL_MINILM_L6_V2  # Will fall back to mock
        config.dimension = 384
        manager = EmbeddingManager(config)
    
    # Test texts
    educational_texts = [
        "Grade 3 students learn about fractions using visual models and manipulatives",
        "Middle school science curriculum includes hands-on experiments and inquiry-based learning",
        "High school robotics competition requires advanced programming and engineering skills",
        "Elementary mathematics focuses on number sense and basic operations",
        "STEM education integrates science, technology, engineering, and mathematics"
    ]
    
    print(f"\n--- Generating Embeddings for {len(educational_texts)} texts ---")
    
    # Generate embeddings
    embedding_results = await manager.generate_embeddings(educational_texts)
    
    for i, result in enumerate(embedding_results):
        print(f"Text {i+1}: {result.text[:50]}...")
        print(f"  Dimension: {result.dimension}")
        print(f"  Cached: {result.cached}")
        print(f"  Processing time: {result.processing_time:.4f}s")
    
    print(f"\n--- Testing Similarity ---")
    
    # Test similarity
    query = "robotics programming for students"
    similarities = await manager.find_most_similar(query, educational_texts, top_k=3)
    
    print(f"Query: {query}")
    print("Most similar texts:")
    for text, similarity in similarities:
        print(f"  Similarity {similarity:.3f}: {text[:50]}...")
    
    print(f"\n--- Performance Statistics ---")
    stats = manager.get_performance_stats()
    print(f"Total embeddings generated: {stats['total_embeddings_generated']}")
    print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")
    print(f"Average processing time: {stats['avg_processing_time']:.4f}s")
    
    print(f"\n--- Model Benchmark ---")
    benchmark = await manager.benchmark_model(educational_texts[:3])  # Smaller set for demo
    print(f"Model: {benchmark['model_name']}")
    print(f"Throughput: {benchmark['throughput_texts_per_second']:.1f} texts/second")
    print(f"Embedding dimension: {benchmark['embedding_dimension']}")
    print(f"Sample similarities: {[f'{s:.3f}' for s in benchmark['sample_similarities']]}")
    
    print(f"\n--- Text Diversity Analysis ---")
    diversity_score = await manager.get_text_diversity_score(educational_texts)
    print(f"Text diversity score: {diversity_score:.3f}")
    print("(Higher scores indicate more diverse content)")
    
    print(f"\n--- Query Enhancement ---")
    original_query = "math lesson"
    enhanced_query = await manager.enhance_query(original_query, educational_texts)
    print(f"Original query: {original_query}")
    print(f"Enhanced query: {enhanced_query}")
    
    print("\n=== Embedding Manager Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())