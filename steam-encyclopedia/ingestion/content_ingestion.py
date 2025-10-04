"""
Content Ingestion Pipeline for STEAM Encyclopedia
Automated system for collecting, processing, and routing content from various sources
"""

import asyncio
import aiohttp
import feedparser
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import re
from urllib.parse import urlparse
import hashlib


class SourceType(Enum):
    JOURNAL = "journal"
    NEWS = "news"
    RESEARCH_PAPER = "research_paper"
    ANNOUNCEMENT = "announcement"
    CONFERENCE = "conference"
    PATENT = "patent"
    EDUCATIONAL = "educational"


class Priority(Enum):
    URGENT = "urgent"          # Breaking news, critical discoveries
    HIGH = "high"              # Recent important research
    MEDIUM = "medium"          # Regular updates
    LOW = "low"                # Background information


@dataclass
class ContentSource:
    """Configuration for a content source."""
    source_id: str
    name: str
    url: str
    source_type: SourceType
    domains: List[str]  # STEAM domains this source covers
    update_frequency: int  # Hours between checks
    priority_level: Priority
    api_key: Optional[str] = None
    custom_parser: Optional[str] = None
    last_checked: Optional[datetime] = None
    success_rate: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "name": self.name,
            "url": self.url,
            "source_type": self.source_type.value,
            "domains": self.domains,
            "update_frequency": self.update_frequency,
            "priority_level": self.priority_level.value,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "success_rate": self.success_rate
        }


@dataclass
class RawContent:
    """Raw content item from a source before processing."""
    content_id: str
    source_id: str
    title: str
    content: str
    url: str
    publish_date: datetime
    authors: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    doi: Optional[str] = None
    citation_count: int = 0
    detected_domains: List[str] = field(default_factory=list)
    priority_score: float = 0.5
    ingestion_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_id": self.content_id,
            "source_id": self.source_id,
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "publish_date": self.publish_date.isoformat(),
            "authors": self.authors,
            "keywords": self.keywords,
            "doi": self.doi,
            "citation_count": self.citation_count,
            "detected_domains": self.detected_domains,
            "priority_score": self.priority_score,
            "ingestion_timestamp": self.ingestion_timestamp.isoformat()
        }


class ContentIngestionPipeline:
    """Main pipeline for ingesting content from various sources."""
    
    def __init__(self):
        self.sources: Dict[str, ContentSource] = {}
        self.ingested_content: List[RawContent] = []
        self.domain_classifiers = self._initialize_domain_classifiers()
        self.priority_evaluator = PriorityEvaluator()
        self.deduplication_cache: Set[str] = set()
        self.processing_queue = asyncio.Queue()
        self.stats = {
            "total_ingested": 0,
            "successful_ingestions": 0,
            "failed_ingestions": 0,
            "duplicate_content": 0,
            "processing_time": 0.0
        }
    
    def _initialize_domain_classifiers(self) -> Dict[str, List[str]]:
        """Initialize keyword classifiers for STEAM domains."""
        return {
            "science": [
                "research", "study", "experiment", "hypothesis", "theory", "discovery",
                "biology", "chemistry", "physics", "astronomy", "ecology", "genetics",
                "molecule", "atom", "cell", "organism", "DNA", "protein", "evolution"
            ],
            "technology": [
                "innovation", "device", "digital", "computer", "software", "hardware",
                "artificial intelligence", "machine learning", "robotics", "automation",
                "internet", "cybersecurity", "data", "algorithm", "programming"
            ],
            "engineering": [
                "design", "build", "construct", "manufacture", "prototype", "optimization",
                "mechanical", "electrical", "civil", "chemical", "aerospace", "biomedical",
                "infrastructure", "system", "process", "efficiency", "sustainability"
            ],
            "arts": [
                "creative", "design", "visual", "digital art", "media", "communication",
                "graphics", "animation", "user interface", "user experience", "aesthetic",
                "interactive", "multimedia", "visualization", "artistic", "cultural"
            ],
            "mathematics": [
                "equation", "formula", "calculation", "statistics", "probability", "geometry",
                "algebra", "calculus", "modeling", "algorithm", "analysis", "theorem",
                "mathematical", "numerical", "computational", "optimization", "data analysis"
            ]
        }
    
    def add_source(self, source: ContentSource) -> None:
        """Add a new content source to monitor."""
        self.sources[source.source_id] = source
    
    def remove_source(self, source_id: str) -> bool:
        """Remove a content source."""
        if source_id in self.sources:
            del self.sources[source_id]
            return True
        return False
    
    async def start_monitoring(self) -> None:
        """Start the continuous monitoring process."""
        tasks = []
        
        # Create monitoring tasks for each source
        for source in self.sources.values():
            task = asyncio.create_task(self._monitor_source(source))
            tasks.append(task)
        
        # Start content processing task
        processing_task = asyncio.create_task(self._process_content_queue())
        tasks.append(processing_task)
        
        # Wait for all tasks
        await asyncio.gather(*tasks)
    
    async def _monitor_source(self, source: ContentSource) -> None:
        """Monitor a single source for new content."""
        while True:
            try:
                if self._should_check_source(source):
                    await self._fetch_from_source(source)
                    source.last_checked = datetime.now()
                
                # Wait until next check
                await asyncio.sleep(source.update_frequency * 3600)  # Convert hours to seconds
                
            except Exception as e:
                print(f"Error monitoring source {source.source_id}: {e}")
                source.success_rate *= 0.95  # Reduce success rate on error
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    def _should_check_source(self, source: ContentSource) -> bool:
        """Determine if a source should be checked now."""
        if source.last_checked is None:
            return True
        
        time_since_last_check = datetime.now() - source.last_checked
        required_interval = timedelta(hours=source.update_frequency)
        
        return time_since_last_check >= required_interval
    
    async def _fetch_from_source(self, source: ContentSource) -> None:
        """Fetch content from a specific source."""
        try:
            if source.source_type == SourceType.JOURNAL:
                await self._fetch_journal_content(source)
            elif source.source_type == SourceType.NEWS:
                await self._fetch_news_content(source)
            elif source.source_type == SourceType.RESEARCH_PAPER:
                await self._fetch_research_papers(source)
            elif source.source_type == SourceType.ANNOUNCEMENT:
                await self._fetch_announcements(source)
            else:
                await self._fetch_generic_content(source)
                
            source.success_rate = min(1.0, source.success_rate * 1.01)  # Improve on success
            
        except Exception as e:
            print(f"Failed to fetch from {source.source_id}: {e}")
            source.success_rate *= 0.9
    
    async def _fetch_journal_content(self, source: ContentSource) -> None:
        """Fetch content from academic journals."""
        # This would integrate with journal APIs like PubMed, arXiv, etc.
        # For demonstration, we'll simulate the process
        
        mock_articles = [
            {
                "title": "Novel Approach to Quantum Computing Error Correction",
                "content": "Recent advances in quantum error correction have shown promising results...",
                "authors": ["Dr. Jane Smith", "Dr. John Doe"],
                "doi": "10.1000/journal.2025.001",
                "keywords": ["quantum computing", "error correction", "physics"],
                "publish_date": datetime.now() - timedelta(days=1)
            },
            {
                "title": "CRISPR Applications in Sustainable Agriculture",
                "content": "Gene editing techniques are revolutionizing crop development...",
                "authors": ["Dr. Maria Garcia", "Dr. Chen Wei"],
                "doi": "10.1000/biojournal.2025.002",
                "keywords": ["CRISPR", "agriculture", "biotechnology", "sustainability"],
                "publish_date": datetime.now() - timedelta(hours=12)
            }
        ]
        
        for article in mock_articles:
            raw_content = await self._create_raw_content(article, source)
            await self.processing_queue.put(raw_content)
    
    async def _fetch_news_content(self, source: ContentSource) -> None:
        """Fetch content from news sources and RSS feeds."""
        try:
            # Parse RSS feed
            feed = feedparser.parse(source.url)
            
            for entry in feed.entries[:10]:  # Limit to 10 most recent
                article_data = {
                    "title": entry.title,
                    "content": entry.get('summary', entry.get('description', '')),
                    "url": entry.link,
                    "publish_date": datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    "authors": [entry.get('author', 'Unknown')],
                    "keywords": []
                }
                
                raw_content = await self._create_raw_content(article_data, source)
                await self.processing_queue.put(raw_content)
                
        except Exception as e:
            print(f"Error fetching RSS from {source.url}: {e}")
    
    async def _fetch_research_papers(self, source: ContentSource) -> None:
        """Fetch research papers from repositories like arXiv."""
        # Implementation would integrate with arXiv API, Google Scholar, etc.
        pass
    
    async def _fetch_announcements(self, source: ContentSource) -> None:
        """Fetch announcements from organizations."""
        # Implementation would integrate with NASA, NSF, university press releases, etc.
        pass
    
    async def _fetch_generic_content(self, source: ContentSource) -> None:
        """Fetch content from generic web sources."""
        async with aiohttp.ClientSession() as session:
            async with session.get(source.url) as response:
                if response.status == 200:
                    content = await response.text()
                    # Basic HTML parsing and content extraction would go here
                    # For now, create a placeholder
                    article_data = {
                        "title": "Generic Content",
                        "content": content[:1000],  # First 1000 characters
                        "url": source.url,
                        "publish_date": datetime.now(),
                        "authors": [],
                        "keywords": []
                    }
                    
                    raw_content = await self._create_raw_content(article_data, source)
                    await self.processing_queue.put(raw_content)
    
    async def _create_raw_content(self, article_data: Dict[str, Any], source: ContentSource) -> RawContent:
        """Create RawContent object from article data."""
        content_id = self._generate_content_id(article_data["title"], article_data.get("url", ""))
        
        # Detect domains using keyword classification
        detected_domains = self._classify_domains(article_data["content"])
        
        # Calculate priority score
        priority_score = self.priority_evaluator.evaluate_priority(
            article_data, source, detected_domains
        )
        
        return RawContent(
            content_id=content_id,
            source_id=source.source_id,
            title=article_data["title"],
            content=article_data["content"],
            url=article_data.get("url", ""),
            publish_date=article_data["publish_date"],
            authors=article_data.get("authors", []),
            keywords=article_data.get("keywords", []),
            doi=article_data.get("doi"),
            citation_count=article_data.get("citation_count", 0),
            detected_domains=detected_domains,
            priority_score=priority_score
        )
    
    def _generate_content_id(self, title: str, url: str) -> str:
        """Generate unique content ID."""
        content_string = f"{title}_{url}_{datetime.now().date()}"
        return hashlib.md5(content_string.encode()).hexdigest()[:16]
    
    def _classify_domains(self, content: str) -> List[str]:
        """Classify content into STEAM domains using keyword matching."""
        content_lower = content.lower()
        detected_domains = []
        
        for domain, keywords in self.domain_classifiers.items():
            matches = sum(1 for keyword in keywords if keyword.lower() in content_lower)
            # If more than 2 keywords match, consider it relevant to this domain
            if matches >= 2:
                detected_domains.append(domain)
        
        return detected_domains
    
    async def _process_content_queue(self) -> None:
        """Process the content queue continuously."""
        while True:
            try:
                raw_content = await self.processing_queue.get()
                await self._process_raw_content(raw_content)
                self.processing_queue.task_done()
                
            except Exception as e:
                print(f"Error processing content: {e}")
                await asyncio.sleep(1)
    
    async def _process_raw_content(self, raw_content: RawContent) -> None:
        """Process a raw content item."""
        start_time = datetime.now()
        
        # Check for duplicates
        if self._is_duplicate(raw_content):
            self.stats["duplicate_content"] += 1
            return
        
        # Add to deduplication cache
        self.deduplication_cache.add(raw_content.content_id)
        
        # Add to ingested content
        self.ingested_content.append(raw_content)
        
        # Update statistics
        self.stats["total_ingested"] += 1
        self.stats["successful_ingestions"] += 1
        processing_time = (datetime.now() - start_time).total_seconds()
        self.stats["processing_time"] += processing_time
        
        print(f"Processed content: {raw_content.title[:50]}... (Priority: {raw_content.priority_score:.2f})")
    
    def _is_duplicate(self, raw_content: RawContent) -> bool:
        """Check if content is a duplicate."""
        return raw_content.content_id in self.deduplication_cache
    
    def get_recent_content(self, hours: int = 24, domain: str = None, 
                          min_priority: float = 0.0) -> List[RawContent]:
        """Get recent content matching criteria."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_content = []
        for content in self.ingested_content:
            if content.ingestion_timestamp < cutoff_time:
                continue
            if domain and domain not in content.detected_domains:
                continue
            if content.priority_score < min_priority:
                continue
            
            filtered_content.append(content)
        
        # Sort by priority score and recency
        filtered_content.sort(
            key=lambda x: (x.priority_score, x.ingestion_timestamp), 
            reverse=True
        )
        
        return filtered_content
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get ingestion pipeline statistics."""
        avg_processing_time = (
            self.stats["processing_time"] / max(1, self.stats["successful_ingestions"])
        )
        
        return {
            **self.stats,
            "average_processing_time": avg_processing_time,
            "active_sources": len(self.sources),
            "content_in_queue": self.processing_queue.qsize(),
            "domains_detected": self._get_domain_distribution(),
            "source_performance": self._get_source_performance()
        }
    
    def _get_domain_distribution(self) -> Dict[str, int]:
        """Get distribution of content across STEAM domains."""
        distribution = {}
        for content in self.ingested_content:
            for domain in content.detected_domains:
                distribution[domain] = distribution.get(domain, 0) + 1
        return distribution
    
    def _get_source_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics for each source."""
        performance = {}
        for source_id, source in self.sources.items():
            content_count = sum(1 for c in self.ingested_content if c.source_id == source_id)
            performance[source_id] = {
                "name": source.name,
                "success_rate": source.success_rate,
                "content_ingested": content_count,
                "last_checked": source.last_checked.isoformat() if source.last_checked else None
            }
        return performance


class PriorityEvaluator:
    """Evaluates the priority of content items."""
    
    def __init__(self):
        self.high_priority_keywords = [
            "breakthrough", "discovery", "innovation", "urgent", "critical",
            "revolutionary", "first", "new", "novel", "unprecedented"
        ]
        
        self.domain_weights = {
            "science": 0.9,
            "technology": 0.8,
            "engineering": 0.7,
            "mathematics": 0.7,
            "arts": 0.6
        }
    
    def evaluate_priority(self, article_data: Dict[str, Any], 
                         source: ContentSource, domains: List[str]) -> float:
        """Evaluate the priority score for a content item."""
        base_score = 0.5
        
        # Source priority contribution
        source_multiplier = {
            Priority.URGENT: 1.0,
            Priority.HIGH: 0.8,
            Priority.MEDIUM: 0.6,
            Priority.LOW: 0.4
        }
        base_score += source_multiplier[source.priority_level] * 0.3
        
        # Content freshness
        publish_date = article_data.get("publish_date", datetime.now())
        days_old = (datetime.now() - publish_date).days
        freshness_score = max(0, 1 - days_old / 30)  # Decreases over 30 days
        base_score += freshness_score * 0.2
        
        # High-priority keywords
        content_text = article_data.get("content", "").lower()
        keyword_matches = sum(1 for keyword in self.high_priority_keywords 
                            if keyword in content_text)
        base_score += min(0.3, keyword_matches * 0.1)
        
        # Domain relevance
        if domains:
            domain_score = max(self.domain_weights.get(domain, 0.5) for domain in domains)
            base_score += domain_score * 0.2
        
        # Citation count (if available)
        citation_count = article_data.get("citation_count", 0)
        if citation_count > 0:
            citation_score = min(0.2, citation_count / 100)  # Max 0.2 for high citations
            base_score += citation_score
        
        return min(1.0, base_score)  # Cap at 1.0


def create_default_sources() -> List[ContentSource]:
    """Create default content sources for STEAM encyclopedia."""
    return [
        # Science journals and sources
        ContentSource(
            source_id="nature_rss",
            name="Nature Journal",
            url="https://www.nature.com/nature.rss",
            source_type=SourceType.JOURNAL,
            domains=["science", "technology"],
            update_frequency=4,  # Every 4 hours
            priority_level=Priority.HIGH
        ),
        
        ContentSource(
            source_id="science_mag_rss",
            name="Science Magazine",
            url="https://www.sciencemag.org/rss/current.xml",
            source_type=SourceType.JOURNAL,
            domains=["science", "technology", "engineering"],
            update_frequency=6,
            priority_level=Priority.HIGH
        ),
        
        # Technology sources
        ContentSource(
            source_id="ieee_spectrum",
            name="IEEE Spectrum",
            url="https://spectrum.ieee.org/feeds/blog/tech-talk.rss",
            source_type=SourceType.NEWS,
            domains=["technology", "engineering"],
            update_frequency=8,
            priority_level=Priority.MEDIUM
        ),
        
        # Educational sources
        ContentSource(
            source_id="nasa_news",
            name="NASA News",
            url="https://www.nasa.gov/rss/dyn/breaking_news.rss",
            source_type=SourceType.ANNOUNCEMENT,
            domains=["science", "technology", "engineering"],
            update_frequency=12,
            priority_level=Priority.HIGH
        ),
        
        # Research repositories
        ContentSource(
            source_id="arxiv_cs",
            name="arXiv Computer Science",
            url="http://export.arxiv.org/rss/cs",
            source_type=SourceType.RESEARCH_PAPER,
            domains=["technology", "mathematics"],
            update_frequency=24,
            priority_level=Priority.MEDIUM
        ),
        
        # Mathematics sources
        ContentSource(
            source_id="ams_notices",
            name="AMS Notices",
            url="https://www.ams.org/journals/notices/notices.rss",
            source_type=SourceType.JOURNAL,
            domains=["mathematics"],
            update_frequency=48,
            priority_level=Priority.MEDIUM
        )
    ]


# Example usage and testing
async def main():
    """Example usage of the content ingestion pipeline."""
    pipeline = ContentIngestionPipeline()
    
    # Add default sources
    default_sources = create_default_sources()
    for source in default_sources:
        pipeline.add_source(source)
    
    print("Starting content ingestion pipeline...")
    print(f"Monitoring {len(pipeline.sources)} sources")
    
    # Start monitoring (in a real system, this would run continuously)
    # For demo, we'll run for a short time
    try:
        await asyncio.wait_for(pipeline.start_monitoring(), timeout=30)
    except asyncio.TimeoutError:
        pass
    
    # Show statistics
    stats = pipeline.get_statistics()
    print("\nIngestion Statistics:")
    print(json.dumps(stats, indent=2, default=str))
    
    # Show recent high-priority content
    recent_content = pipeline.get_recent_content(hours=24, min_priority=0.7)
    print(f"\nFound {len(recent_content)} high-priority items:")
    for content in recent_content[:5]:
        print(f"- {content.title} (Priority: {content.priority_score:.2f})")


if __name__ == "__main__":
    asyncio.run(main())