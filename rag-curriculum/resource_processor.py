"""
Resource Processor
Processes different types of educational resources including documentation, user guides, and resource libraries
"""

from typing import Dict, List, Any, Optional, Union, IO
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import re
import mimetypes
from abc import ABC, abstractmethod

# Document processing dependencies
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

from .rag_engine import RAGEngine
from .curriculum_indexer import LearningLevel, CurriculumMetadata


class ResourceType(Enum):
    """Types of educational resources."""
    # Documentation types
    USER_GUIDE = "user_guide"
    TUTORIAL = "tutorial"
    REFERENCE_MANUAL = "reference_manual"
    API_DOCUMENTATION = "api_documentation"
    
    # Educational content
    LESSON_PLAN = "lesson_plan"
    ACTIVITY_GUIDE = "activity_guide"
    ASSESSMENT_RUBRIC = "assessment_rubric"
    WORKSHEET = "worksheet"
    
    # Multimedia resources
    VIDEO_TRANSCRIPT = "video_transcript"
    AUDIO_TRANSCRIPT = "audio_transcript"
    INTERACTIVE_CONTENT = "interactive_content"
    
    # Library resources
    RESEARCH_PAPER = "research_paper"
    CASE_STUDY = "case_study"
    BEST_PRACTICES = "best_practices"
    STANDARDS_DOCUMENT = "standards_document"
    
    # Tools and utilities
    TEMPLATE = "template"
    CHECKLIST = "checklist"
    TROUBLESHOOTING_GUIDE = "troubleshooting_guide"
    FAQ = "faq"


class ResourceFormat(Enum):
    """Supported resource formats."""
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    DOCX = "docx"
    JSON = "json"
    CSV = "csv"
    XML = "xml"


@dataclass
class ResourceMetadata:
    """Metadata for educational resources."""
    # Basic identification
    resource_id: str
    title: str
    description: str
    resource_type: ResourceType
    format_type: ResourceFormat
    
    # Content organization
    learning_level: LearningLevel
    subject_areas: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    
    # Educational context
    target_audience: List[str] = field(default_factory=list)  # students, teachers, administrators
    age_range: Optional[str] = None
    grade_levels: List[Union[int, str]] = field(default_factory=list)
    difficulty_level: str = "intermediate"
    
    # Content characteristics
    language: str = "English"
    length: Optional[int] = None  # word count, page count, duration in minutes
    estimated_read_time: Optional[str] = None
    prerequisites: List[str] = field(default_factory=list)
    
    # Quality and validation
    author: Optional[str] = None
    organization: Optional[str] = None
    publication_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    version: Optional[str] = None
    quality_score: Optional[float] = None
    peer_reviewed: bool = False
    
    # Usage and effectiveness
    download_count: int = 0
    view_count: int = 0
    rating: Optional[float] = None
    reviews: List[str] = field(default_factory=list)
    
    # Technical details
    file_size: Optional[int] = None
    file_path: Optional[str] = None
    checksum: Optional[str] = None
    accessibility_features: List[str] = field(default_factory=list)
    
    # Licensing and permissions
    license: Optional[str] = None
    copyright: Optional[str] = None
    usage_rights: List[str] = field(default_factory=list)
    attribution_required: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        result = {}
        
        for key, value in self.__dict__.items():
            if isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, datetime):
                result[key] = value.isoformat() if value else None
            elif isinstance(value, list):
                result[key] = [
                    item.value if isinstance(item, Enum) else item 
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceMetadata':
        """Create from dictionary."""
        # Convert enum fields back
        if 'resource_type' in data:
            data['resource_type'] = ResourceType(data['resource_type'])
        if 'format_type' in data:
            data['format_type'] = ResourceFormat(data['format_type'])
        if 'learning_level' in data:
            data['learning_level'] = LearningLevel(data['learning_level'])
        if 'publication_date' in data and data['publication_date']:
            data['publication_date'] = datetime.fromisoformat(data['publication_date'])
        if 'last_updated' in data and data['last_updated']:
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        
        return cls(**data)


class DocumentParser(ABC):
    """Abstract base class for document parsers."""
    
    @abstractmethod
    async def parse(self, file_path: str) -> str:
        """Parse document and return text content."""
        pass
    
    @abstractmethod
    def supports_format(self, format_type: ResourceFormat) -> bool:
        """Check if parser supports the format."""
        pass


class TextParser(DocumentParser):
    """Parser for plain text files."""
    
    async def parse(self, file_path: str) -> str:
        """Parse text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def supports_format(self, format_type: ResourceFormat) -> bool:
        return format_type == ResourceFormat.TEXT


class MarkdownParser(DocumentParser):
    """Parser for Markdown files."""
    
    async def parse(self, file_path: str) -> str:
        """Parse Markdown file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if MARKDOWN_AVAILABLE:
            # Convert to HTML and extract text
            html = markdown.markdown(content)
            # Simple HTML tag removal
            text = re.sub(r'<[^>]+>', '', html)
            return text
        else:
            # Return raw markdown
            return content
    
    def supports_format(self, format_type: ResourceFormat) -> bool:
        return format_type == ResourceFormat.MARKDOWN


class PDFParser(DocumentParser):
    """Parser for PDF files."""
    
    async def parse(self, file_path: str) -> str:
        """Parse PDF file."""
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 not available. Install with: pip install PyPDF2")
        
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page in pdf_reader.pages:
                try:
                    text += page.extract_text() + "\n"
                except Exception as e:
                    logging.warning(f"Error extracting text from PDF page: {e}")
                    continue
        
        return text
    
    def supports_format(self, format_type: ResourceFormat) -> bool:
        return format_type == ResourceFormat.PDF


class DocxParser(DocumentParser):
    """Parser for DOCX files."""
    
    async def parse(self, file_path: str) -> str:
        """Parse DOCX file."""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx not available. Install with: pip install python-docx")
        
        doc = Document(file_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text
    
    def supports_format(self, format_type: ResourceFormat) -> bool:
        return format_type == ResourceFormat.DOCX


class JSONParser(DocumentParser):
    """Parser for JSON files."""
    
    async def parse(self, file_path: str) -> str:
        """Parse JSON file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Extract text content from JSON structure
        return self._extract_text_from_json(data)
    
    def _extract_text_from_json(self, data: Any, prefix: str = "") -> str:
        """Recursively extract text from JSON data."""
        text = ""
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    text += f"{prefix}{key}: {value}\n"
                elif isinstance(value, (dict, list)):
                    text += self._extract_text_from_json(value, f"{prefix}{key}.")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                text += self._extract_text_from_json(item, f"{prefix}[{i}].")
        elif isinstance(data, str):
            text += f"{prefix}{data}\n"
        
        return text
    
    def supports_format(self, format_type: ResourceFormat) -> bool:
        return format_type == ResourceFormat.JSON


class ResourceProcessor:
    """Main processor for educational resources."""
    
    def __init__(self, rag_engine: RAGEngine):
        self.rag_engine = rag_engine
        self.logger = logging.getLogger("resource_processor")
        
        # Initialize document parsers
        self.parsers = [
            TextParser(),
            MarkdownParser(),
            PDFParser() if PDF_AVAILABLE else None,
            DocxParser() if DOCX_AVAILABLE else None,
            JSONParser()
        ]
        self.parsers = [p for p in self.parsers if p is not None]
        
        # Resource collections by learning level
        self.resource_collections = {}
        
        # Content analysis patterns
        self.content_patterns = self._initialize_content_patterns()
    
    def _initialize_content_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for content analysis."""
        return {
            "user_guide": [
                r"how to", r"step.by.step", r"getting started", r"installation",
                r"setup", r"configuration", r"user manual", r"instructions"
            ],
            "tutorial": [
                r"tutorial", r"learn", r"beginner", r"introduction to",
                r"walkthrough", r"lesson", r"example", r"demonstration"
            ],
            "reference": [
                r"reference", r"api", r"documentation", r"specification",
                r"manual", r"guide", r"handbook", r"glossary"
            ],
            "troubleshooting": [
                r"troubleshoot", r"problem", r"error", r"issue", r"fix",
                r"debug", r"solution", r"resolve", r"common problems"
            ],
            "faq": [
                r"frequently asked", r"faq", r"questions", r"q&a",
                r"common questions", r"help"
            ],
            "assessment": [
                r"rubric", r"assessment", r"evaluation", r"grading",
                r"criteria", r"checklist", r"scoring"
            ]
        }
    
    async def initialize_resource_collections(self):
        """Initialize resource collections for different learning levels."""
        
        # Grade-level resources
        grade_resources_id = await self.rag_engine.create_collection({
            "collection_id": "grade_level_resources",
            "name": "Grade-Level Educational Resources",
            "description": "User guides, documentation, and resources for K-12 education",
            "metadata": {
                "learning_level": LearningLevel.GRADE_LEVEL.value,
                "resource_types": ["user_guide", "lesson_plan", "activity_guide", "worksheet"]
            }
        })
        self.resource_collections[LearningLevel.GRADE_LEVEL] = grade_resources_id
        
        # Global learning resources
        global_resources_id = await self.rag_engine.create_collection({
            "collection_id": "global_learning_resources",
            "name": "Global Learning Resources",
            "description": "International educational resources and documentation",
            "metadata": {
                "learning_level": LearningLevel.GLOBAL_LEARNING.value,
                "resource_types": ["standards_document", "best_practices", "research_paper"]
            }
        })
        self.resource_collections[LearningLevel.GLOBAL_LEARNING] = global_resources_id
        
        # Competition resources
        competition_resources_id = await self.rag_engine.create_collection({
            "collection_id": "global_competition_resources",
            "name": "Global Competition Resources",
            "description": "Advanced resources for educational competitions",
            "metadata": {
                "learning_level": LearningLevel.GLOBAL_COMPETITION.value,
                "resource_types": ["reference_manual", "tutorial", "case_study", "troubleshooting_guide"]
            }
        })
        self.resource_collections[LearningLevel.GLOBAL_COMPETITION] = competition_resources_id
        
        self.logger.info("Initialized resource collections for all learning levels")
    
    async def process_resource_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Process a resource file and add it to appropriate collection."""
        
        # Determine file format
        file_format = self._detect_file_format(file_path)
        
        # Find appropriate parser
        parser = self._get_parser_for_format(file_format)
        if not parser:
            raise ValueError(f"No parser available for format: {file_format}")
        
        # Parse content
        content = await parser.parse(file_path)
        
        # Extract metadata
        resource_metadata = await self._extract_resource_metadata(content, file_path, metadata or {})
        
        # Determine learning level and collection
        learning_level = resource_metadata.learning_level
        if learning_level not in self.resource_collections:
            await self.initialize_resource_collections()
        
        collection_id = self.resource_collections[learning_level]
        
        # Create document for RAG engine
        document = {
            "id": resource_metadata.resource_id,
            "content": content,
            "metadata": resource_metadata.to_dict()
        }
        
        # Add to collection
        await self.rag_engine.add_documents_to_collection(collection_id, [document])
        
        self.logger.info(f"Processed resource: {file_path} -> {resource_metadata.title}")
        return resource_metadata.resource_id
    
    def _detect_file_format(self, file_path: str) -> ResourceFormat:
        """Detect file format from path."""
        
        path = Path(file_path)
        extension = path.suffix.lower()
        
        format_map = {
            '.txt': ResourceFormat.TEXT,
            '.md': ResourceFormat.MARKDOWN,
            '.markdown': ResourceFormat.MARKDOWN,
            '.html': ResourceFormat.HTML,
            '.htm': ResourceFormat.HTML,
            '.pdf': ResourceFormat.PDF,
            '.docx': ResourceFormat.DOCX,
            '.json': ResourceFormat.JSON,
            '.csv': ResourceFormat.CSV,
            '.xml': ResourceFormat.XML
        }
        
        return format_map.get(extension, ResourceFormat.TEXT)
    
    def _get_parser_for_format(self, format_type: ResourceFormat) -> Optional[DocumentParser]:
        """Get parser for format type."""
        
        for parser in self.parsers:
            if parser.supports_format(format_type):
                return parser
        
        return None
    
    async def _extract_resource_metadata(self, content: str, file_path: str, existing_metadata: Dict[str, Any]) -> ResourceMetadata:
        """Extract metadata from resource content."""
        
        # Basic information
        path = Path(file_path)
        resource_id = existing_metadata.get("id", f"resource_{path.stem}_{datetime.now().timestamp()}")
        
        # Extract or default metadata
        metadata = ResourceMetadata(
            resource_id=resource_id,
            title=existing_metadata.get("title", self._extract_title(content, path.stem)),
            description=existing_metadata.get("description", self._extract_description(content)),
            resource_type=ResourceType(existing_metadata.get("resource_type", self._identify_resource_type(content))),
            format_type=self._detect_file_format(file_path),
            learning_level=LearningLevel(existing_metadata.get("learning_level", self._determine_learning_level(content)))
        )
        
        # Extract additional metadata
        metadata.subject_areas = existing_metadata.get("subject_areas", self._extract_subject_areas(content))
        metadata.topics = existing_metadata.get("topics", self._extract_topics(content))
        metadata.keywords = existing_metadata.get("keywords", self._extract_keywords(content))
        metadata.target_audience = existing_metadata.get("target_audience", self._identify_target_audience(content))
        metadata.difficulty_level = existing_metadata.get("difficulty_level", self._determine_difficulty(content))
        metadata.estimated_read_time = self._estimate_read_time(content)
        metadata.length = len(content.split())  # Word count
        
        # File information
        metadata.file_path = file_path
        metadata.file_size = Path(file_path).stat().st_size if Path(file_path).exists() else None
        
        # Set defaults based on resource type
        await self._set_resource_type_defaults(metadata)
        
        return metadata
    
    def _extract_title(self, content: str, filename: str) -> str:
        """Extract title from content or filename."""
        
        # Look for title patterns in content
        title_patterns = [
            r'^#\s+(.*?)$',  # Markdown H1
            r'<h1[^>]*>(.*?)</h1>',  # HTML H1
            r'Title:\s*(.*?)(?:\n|$)',
            r'^(.{1,80}?)(?:\n|$)'  # First line if short
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if title and len(title) > 3:
                    return title
        
        # Fall back to filename
        return filename.replace('_', ' ').replace('-', ' ').title()
    
    def _extract_description(self, content: str) -> str:
        """Extract description from content."""
        
        # Look for description patterns
        desc_patterns = [
            r'Description:\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Summary:\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Abstract:\s*(.*?)(?:\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                desc = match.group(1).strip()
                if desc:
                    return desc[:500]  # Limit length
        
        # Extract first paragraph
        paragraphs = content.split('\n\n')
        if paragraphs:
            first_para = paragraphs[0].strip()
            if len(first_para) > 50 and len(first_para) < 500:
                return first_para
        
        # Extract first few sentences
        sentences = content.split('.')
        if sentences and len(sentences) > 1:
            desc = '. '.join(sentences[:3]) + '.'
            if len(desc) < 500:
                return desc
        
        return "Educational resource content"
    
    def _identify_resource_type(self, content: str) -> str:
        """Identify resource type from content."""
        
        content_lower = content.lower()
        
        # Score each resource type
        type_scores = {}
        
        for resource_type, patterns in self.content_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content_lower))
                score += matches
            
            if score > 0:
                type_scores[resource_type] = score
        
        if type_scores:
            # Return type with highest score
            best_type = max(type_scores, key=type_scores.get)
            
            # Map to ResourceType enum
            type_mapping = {
                "user_guide": ResourceType.USER_GUIDE,
                "tutorial": ResourceType.TUTORIAL,
                "reference": ResourceType.REFERENCE_MANUAL,
                "troubleshooting": ResourceType.TROUBLESHOOTING_GUIDE,
                "faq": ResourceType.FAQ,
                "assessment": ResourceType.ASSESSMENT_RUBRIC
            }
            
            return type_mapping.get(best_type, ResourceType.USER_GUIDE).value
        
        return ResourceType.USER_GUIDE.value
    
    def _determine_learning_level(self, content: str) -> str:
        """Determine learning level from content."""
        
        content_lower = content.lower()
        
        # Grade level indicators
        grade_indicators = [
            'grade', 'elementary', 'middle school', 'high school',
            'kindergarten', 'k-12', 'primary', 'secondary'
        ]
        
        if any(indicator in content_lower for indicator in grade_indicators):
            return LearningLevel.GRADE_LEVEL.value
        
        # Competition indicators
        competition_indicators = [
            'competition', 'olympiad', 'contest', 'championship',
            'advanced', 'expert', 'professional'
        ]
        
        if any(indicator in content_lower for indicator in competition_indicators):
            return LearningLevel.GLOBAL_COMPETITION.value
        
        # International/global indicators
        global_indicators = [
            'international', 'global', 'worldwide', 'cross-cultural',
            'multilingual', 'standards'
        ]
        
        if any(indicator in content_lower for indicator in global_indicators):
            return LearningLevel.GLOBAL_LEARNING.value
        
        # Default to grade level
        return LearningLevel.GRADE_LEVEL.value
    
    def _extract_subject_areas(self, content: str) -> List[str]:
        """Extract subject areas from content."""
        
        subject_keywords = {
            'mathematics': ['math', 'mathematics', 'algebra', 'geometry', 'calculus', 'statistics'],
            'science': ['science', 'biology', 'chemistry', 'physics', 'earth science'],
            'technology': ['technology', 'computer', 'digital', 'software', 'hardware'],
            'engineering': ['engineering', 'design', 'build', 'construct', 'mechanical'],
            'arts': ['art', 'creative', 'design', 'visual', 'music', 'drama'],
            'language_arts': ['reading', 'writing', 'literature', 'language', 'english'],
            'social_studies': ['history', 'geography', 'civics', 'social studies', 'culture'],
            'robotics': ['robot', 'robotics', 'automation', 'programming']
        }
        
        content_lower = content.lower()
        found_subjects = []
        
        for subject, keywords in subject_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                found_subjects.append(subject)
        
        return found_subjects
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract main topics from content."""
        
        # Look for section headers
        header_patterns = [
            r'^##\s+(.*?)$',  # Markdown H2
            r'<h2[^>]*>(.*?)</h2>',  # HTML H2
            r'^([A-Z][^.!?]*[.!?])$'  # All caps sentences
        ]
        
        topics = []
        
        for pattern in header_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                topic = match.strip()
                if topic and len(topic) < 80:
                    topics.append(topic)
        
        return topics[:10]  # Limit to 10 topics
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content."""
        
        # Look for explicit keywords
        keyword_patterns = [
            r'Keywords:\s*(.*?)(?:\n|$)',
            r'Tags:\s*(.*?)(?:\n|$)',
            r'Topics:\s*(.*?)(?:\n|$)'
        ]
        
        keywords = []
        
        for pattern in keyword_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                keyword_text = match.group(1)
                # Split by comma or semicolon
                extracted_keywords = re.split(r'[,;]', keyword_text)
                keywords.extend([kw.strip() for kw in extracted_keywords if kw.strip()])
        
        # Extract important terms (simple approach)
        if not keywords:
            # Find capitalized words that appear multiple times
            capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', content)
            word_counts = {}
            
            for word in capitalized_words:
                if len(word) > 3:  # Ignore short words
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            # Add words that appear more than once
            keywords.extend([word for word, count in word_counts.items() if count > 1])
        
        return keywords[:20]  # Limit to 20 keywords
    
    def _identify_target_audience(self, content: str) -> List[str]:
        """Identify target audience from content."""
        
        audience_keywords = {
            'students': ['student', 'learner', 'pupil'],
            'teachers': ['teacher', 'instructor', 'educator', 'faculty'],
            'administrators': ['administrator', 'principal', 'manager'],
            'parents': ['parent', 'family', 'guardian'],
            'researchers': ['researcher', 'scientist', 'academic']
        }
        
        content_lower = content.lower()
        audiences = []
        
        for audience, keywords in audience_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                audiences.append(audience)
        
        return audiences if audiences else ['students']  # Default to students
    
    def _determine_difficulty(self, content: str) -> str:
        """Determine difficulty level from content."""
        
        difficulty_keywords = {
            'beginner': ['beginner', 'basic', 'introduction', 'simple', 'easy'],
            'intermediate': ['intermediate', 'moderate', 'standard', 'regular'],
            'advanced': ['advanced', 'complex', 'sophisticated', 'challenging'],
            'expert': ['expert', 'professional', 'mastery', 'competition']
        }
        
        content_lower = content.lower()
        
        for level, keywords in difficulty_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return level
        
        return 'intermediate'  # Default
    
    def _estimate_read_time(self, content: str) -> str:
        """Estimate reading time for content."""
        
        word_count = len(content.split())
        
        # Average reading speed: 200-250 words per minute
        reading_speed = 225
        minutes = word_count / reading_speed
        
        if minutes < 1:
            return "< 1 minute"
        elif minutes < 60:
            return f"{int(minutes)} minutes"
        else:
            hours = minutes / 60
            return f"{hours:.1f} hours"
    
    async def _set_resource_type_defaults(self, metadata: ResourceMetadata):
        """Set defaults based on resource type."""
        
        if metadata.resource_type == ResourceType.USER_GUIDE:
            metadata.target_audience = metadata.target_audience or ['teachers', 'students']
            
        elif metadata.resource_type == ResourceType.TUTORIAL:
            metadata.target_audience = metadata.target_audience or ['students']
            metadata.difficulty_level = 'beginner' if metadata.difficulty_level == 'intermediate' else metadata.difficulty_level
            
        elif metadata.resource_type == ResourceType.REFERENCE_MANUAL:
            metadata.target_audience = metadata.target_audience or ['teachers', 'researchers']
            
        elif metadata.resource_type == ResourceType.ASSESSMENT_RUBRIC:
            metadata.target_audience = metadata.target_audience or ['teachers']
            
        elif metadata.resource_type == ResourceType.TROUBLESHOOTING_GUIDE:
            metadata.target_audience = metadata.target_audience or ['teachers', 'administrators']
    
    async def process_resource_directory(self, directory_path: str, recursive: bool = True) -> List[str]:
        """Process all resources in a directory."""
        
        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        processed_resources = []
        
        # Get file pattern for recursive or non-recursive search
        pattern = "**/*" if recursive else "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                try:
                    resource_id = await self.process_resource_file(str(file_path))
                    processed_resources.append(resource_id)
                except Exception as e:
                    self.logger.warning(f"Failed to process {file_path}: {e}")
                    continue
        
        self.logger.info(f"Processed {len(processed_resources)} resources from {directory_path}")
        return processed_resources
    
    async def search_resources(self, 
                             query: str,
                             resource_types: Optional[List[ResourceType]] = None,
                             learning_levels: Optional[List[LearningLevel]] = None,
                             filters: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search educational resources."""
        
        # Determine collections to search
        collection_ids = []
        if learning_levels is None:
            learning_levels = list(LearningLevel)
        
        for level in learning_levels:
            if level in self.resource_collections:
                collection_ids.append(self.resource_collections[level])
        
        # Add resource type filters
        if resource_types:
            if filters is None:
                filters = {}
            filters['resource_type'] = [rt.value for rt in resource_types]
        
        # Search
        if filters:
            results = await self.rag_engine.similarity_search_with_metadata(
                query, filters, collection_ids
            )
        else:
            results = await self.rag_engine.search(query, collection_ids)
        
        # Enhance results with learning level information
        enhanced_results = {}
        for collection_id, collection_results in results.items():
            level_name = "unknown"
            for level, coll_id in self.resource_collections.items():
                if coll_id == collection_id:
                    level_name = level.value
                    break
            
            enhanced_results[level_name] = collection_results
        
        return enhanced_results
    
    async def get_resources_by_type(self, resource_type: ResourceType, learning_level: Optional[LearningLevel] = None) -> List[Dict[str, Any]]:
        """Get resources by type."""
        
        learning_levels = [learning_level] if learning_level else list(LearningLevel)
        
        results = await self.search_resources(
            query=f"{resource_type.value} resources",
            resource_types=[resource_type],
            learning_levels=learning_levels
        )
        
        # Flatten results
        all_results = []
        for level_results in results.values():
            all_results.extend(level_results)
        
        return all_results
    
    def get_supported_formats(self) -> List[ResourceFormat]:
        """Get list of supported resource formats."""
        
        supported_formats = []
        for parser in self.parsers:
            for format_type in ResourceFormat:
                if parser.supports_format(format_type):
                    supported_formats.append(format_type)
        
        return list(set(supported_formats))


# Example usage and testing
async def main():
    """Example usage of the resource processor."""
    print("=== Resource Processor Demo ===")
    
    # Initialize components
    from .rag_engine import RAGEngine
    
    rag = RAGEngine()
    processor = ResourceProcessor(rag)
    
    await processor.initialize_resource_collections()
    
    # Create sample resource files for testing
    sample_resources = [
        {
            "filename": "math_tutorial.md",
            "content": """# Introduction to Fractions
            
This tutorial introduces elementary students to the concept of fractions through visual examples and hands-on activities.

## Learning Objectives
Students will be able to:
- Identify fractions as parts of a whole
- Compare simple fractions
- Use visual models to represent fractions

## Materials Needed
- Fraction bars
- Pie charts
- Worksheets

## Activities
1. Visual fraction exploration
2. Fraction comparison games
3. Real-world fraction examples

Duration: 45 minutes
Grade Level: 3-4
Subject: Mathematics
""",
            "metadata": {
                "resource_type": "tutorial",
                "learning_level": "grade_level",
                "subject_areas": ["mathematics"],
                "grade_levels": [3, 4]
            }
        },
        {
            "filename": "robotics_competition_guide.md",
            "content": """# Advanced Robotics Competition Preparation

This comprehensive guide prepares teams for international robotics competitions including FIRST Robotics Competition and VEX Robotics World Championship.

## Competition Overview
International robotics competitions require advanced programming, mechanical design, and strategic thinking skills.

## Technical Requirements
- Advanced sensor integration
- Autonomous navigation algorithms
- Real-time decision making systems
- Robust mechanical design

## Training Materials
- Programming challenges
- Design case studies
- Competition analysis
- Strategy development

Target audience: High school and college teams
Difficulty: Expert level
Estimated preparation time: 6 months
""",
            "metadata": {
                "resource_type": "reference_manual",
                "learning_level": "global_competition",
                "subject_areas": ["robotics", "engineering"],
                "difficulty_level": "expert"
            }
        }
    ]
    
    # Process sample resources
    processed_ids = []
    for resource in sample_resources:
        # Create temporary file
        temp_file = f"/tmp/{resource['filename']}"
        with open(temp_file, 'w') as f:
            f.write(resource['content'])
        
        try:
            resource_id = await processor.process_resource_file(temp_file, resource['metadata'])
            processed_ids.append(resource_id)
        except Exception as e:
            print(f"Error processing {resource['filename']}: {e}")
    
    print(f"Processed {len(processed_ids)} resources")
    
    # Test searches
    print("\n--- Testing Tutorial Search ---")
    tutorial_results = await processor.search_resources(
        "fractions tutorial for elementary students",
        resource_types=[ResourceType.TUTORIAL],
        learning_levels=[LearningLevel.GRADE_LEVEL]
    )
    
    for level, results in tutorial_results.items():
        print(f"Level: {level}")
        for result in results:
            print(f"  - {result['metadata'].get('title', 'No title')}")
            print(f"    Type: {result['metadata'].get('resource_type', 'Unknown')}")
    
    print("\n--- Testing Competition Resources ---")
    comp_results = await processor.get_resources_by_type(
        ResourceType.REFERENCE_MANUAL,
        LearningLevel.GLOBAL_COMPETITION
    )
    
    for result in comp_results:
        print(f"  - {result['metadata'].get('title', 'No title')}")
        print(f"    Difficulty: {result['metadata'].get('difficulty_level', 'Unknown')}")
    
    print("\n--- Supported Formats ---")
    formats = processor.get_supported_formats()
    print(f"Supported formats: {[f.value for f in formats]}")
    
    print("\n=== Resource Processor Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())