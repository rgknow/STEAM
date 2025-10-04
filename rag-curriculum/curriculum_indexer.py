"""
Curriculum Indexer
Specialized indexing for curriculum standards, learning objectives, and educational resources
"""

from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
from datetime import datetime
import re
from pathlib import Path

from .rag_engine import RAGEngine, DocumentCollection


class LearningLevel(Enum):
    """Different levels of learning organization."""
    GRADE_LEVEL = "grade_level"           # K-12 grade-specific content
    GLOBAL_LEARNING = "global_learning"   # International/cross-cultural learning standards
    GLOBAL_COMPETITION = "global_competition"  # Competition-level advanced content


class SubjectArea(Enum):
    """Subject areas for curriculum organization."""
    MATHEMATICS = "mathematics"
    SCIENCE = "science"
    TECHNOLOGY = "technology"
    ENGINEERING = "engineering"
    ARTS = "arts"
    LANGUAGE_ARTS = "language_arts"
    SOCIAL_STUDIES = "social_studies"
    COMPUTER_SCIENCE = "computer_science"
    ROBOTICS = "robotics"
    INTERDISCIPLINARY = "interdisciplinary"


class CurriculumStandard(Enum):
    """Major curriculum standards."""
    COMMON_CORE = "common_core"
    NGSS = "ngss"  # Next Generation Science Standards
    CSTA = "csta"  # Computer Science Teachers Association
    ISTE = "iste"  # International Society for Technology in Education
    IB = "ib"      # International Baccalaureate
    CAMBRIDGE = "cambridge"
    AUSTRALIAN = "australian"
    BRITISH = "british"
    CUSTOM = "custom"


@dataclass
class CurriculumMetadata:
    """Metadata structure for curriculum content."""
    # Basic identification
    content_id: str
    title: str
    description: str
    
    # Learning level classification
    learning_level: LearningLevel
    grade_level: Optional[Union[int, str]] = None  # K, 1-12, or ranges like "3-5"
    age_range: Optional[str] = None  # "8-10 years"
    
    # Subject classification
    subject_area: SubjectArea
    topic: str
    subtopics: List[str] = field(default_factory=list)
    
    # Standards alignment
    standards: List[str] = field(default_factory=list)
    curriculum_standard: Optional[CurriculumStandard] = None
    learning_objectives: List[str] = field(default_factory=list)
    
    # Difficulty and prerequisites
    difficulty_level: str = "beginner"  # beginner, intermediate, advanced, expert
    prerequisites: List[str] = field(default_factory=list)
    estimated_duration: Optional[str] = None  # "45 minutes", "2 weeks", etc.
    
    # Geographic and cultural context
    country: Optional[str] = None
    region: Optional[str] = None
    language: str = "English"
    cultural_context: List[str] = field(default_factory=list)
    
    # Content type and format
    content_type: str = "lesson"  # lesson, activity, assessment, project, resource
    format_type: str = "text"    # text, video, interactive, hands_on, etc.
    materials_needed: List[str] = field(default_factory=list)
    
    # Pedagogical information
    teaching_methods: List[str] = field(default_factory=list)
    assessment_methods: List[str] = field(default_factory=list)
    differentiation_strategies: List[str] = field(default_factory=list)
    
    # Quality and validation
    author: Optional[str] = None
    source: Optional[str] = None
    last_updated: Optional[datetime] = None
    peer_reviewed: bool = False
    quality_score: Optional[float] = None
    
    # Usage and effectiveness
    usage_count: int = 0
    effectiveness_rating: Optional[float] = None
    student_feedback: List[str] = field(default_factory=list)
    teacher_feedback: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        result = {}
        
        for key, value in self.__dict__.items():
            if isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, datetime):
                result[key] = value.isoformat() if value else None
            elif isinstance(value, list):
                # Handle lists that might contain enums
                result[key] = [
                    item.value if isinstance(item, Enum) else item 
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CurriculumMetadata':
        """Create from dictionary."""
        # Convert enum fields back
        if 'learning_level' in data:
            data['learning_level'] = LearningLevel(data['learning_level'])
        if 'subject_area' in data:
            data['subject_area'] = SubjectArea(data['subject_area'])
        if 'curriculum_standard' in data and data['curriculum_standard']:
            data['curriculum_standard'] = CurriculumStandard(data['curriculum_standard'])
        if 'last_updated' in data and data['last_updated']:
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        
        return cls(**data)


class CurriculumIndexer:
    """Specialized indexer for curriculum and educational content."""
    
    def __init__(self, rag_engine: RAGEngine):
        self.rag_engine = rag_engine
        self.logger = logging.getLogger("curriculum_indexer")
        
        # Collection IDs for different learning levels
        self.level_collections = {}
        
        # Standard mappings for parsing curriculum content
        self.standard_patterns = {
            CurriculumStandard.COMMON_CORE: [
                r'CCSS\.MATH\.(\d+|K)\.([A-Z]+)\.([A-Z])\.(\d+)',
                r'CCSS\.ELA-LITERACY\.([A-Z]+)\.(\d+|K)\.(\d+)'
            ],
            CurriculumStandard.NGSS: [
                r'NGSS\s+(\d+|K)-([A-Z]+)(\d+)-(\d+)',
                r'(\d+|K)-([A-Z]+)(\d+)-(\d+)'
            ],
            CurriculumStandard.CSTA: [
                r'CSTA\s+(\d+|K)[A-Z]?-([A-Z]+)-(\d+)',
                r'(\d+|K)[A-Z]?-([A-Z]+)-(\d+)'
            ]
        }
    
    async def initialize_collections(self):
        """Initialize collections for different learning levels."""
        
        # Grade Level Collection
        grade_level_id = await self.rag_engine.create_collection({
            "collection_id": "grade_level_curriculum",
            "name": "Grade-Level Curriculum",
            "description": "K-12 grade-specific curriculum content and standards",
            "metadata": {
                "learning_level": LearningLevel.GRADE_LEVEL.value,
                "scope": "K-12",
                "content_types": ["lessons", "activities", "assessments", "standards"]
            }
        })
        self.level_collections[LearningLevel.GRADE_LEVEL] = grade_level_id
        
        # Global Learning Collection
        global_learning_id = await self.rag_engine.create_collection({
            "collection_id": "global_learning_standards",
            "name": "Global Learning Standards",
            "description": "International and cross-cultural learning standards and curricula",
            "metadata": {
                "learning_level": LearningLevel.GLOBAL_LEARNING.value,
                "scope": "international",
                "content_types": ["standards", "frameworks", "cultural_adaptations"]
            }
        })
        self.level_collections[LearningLevel.GLOBAL_LEARNING] = global_learning_id
        
        # Global Competition Collection
        competition_id = await self.rag_engine.create_collection({
            "collection_id": "global_competition_resources",
            "name": "Global Competition Resources",
            "description": "Advanced competition-level content for international competitions",
            "metadata": {
                "learning_level": LearningLevel.GLOBAL_COMPETITION.value,
                "scope": "competition",
                "content_types": ["problems", "solutions", "training_materials", "past_competitions"]
            }
        })
        self.level_collections[LearningLevel.GLOBAL_COMPETITION] = competition_id
        
        self.logger.info("Initialized curriculum collections for all learning levels")
    
    async def index_curriculum_content(self, content: List[Dict[str, Any]], learning_level: LearningLevel):
        """Index curriculum content with specialized metadata extraction."""
        
        if learning_level not in self.level_collections:
            await self.initialize_collections()
        
        collection_id = self.level_collections[learning_level]
        
        # Process each content item
        processed_documents = []
        
        for item in content:
            # Extract and enhance metadata
            enhanced_item = await self._enhance_curriculum_metadata(item, learning_level)
            processed_documents.append(enhanced_item)
        
        # Add to RAG engine
        await self.rag_engine.add_documents_to_collection(collection_id, processed_documents)
        
        self.logger.info(f"Indexed {len(processed_documents)} items for {learning_level.value}")
    
    async def _enhance_curriculum_metadata(self, item: Dict[str, Any], learning_level: LearningLevel) -> Dict[str, Any]:
        """Enhance curriculum item with extracted metadata."""
        
        content_text = item.get("content", "")
        existing_metadata = item.get("metadata", {})
        
        # Extract curriculum metadata
        curriculum_metadata = await self._extract_curriculum_metadata(content_text, existing_metadata, learning_level)
        
        # Combine with existing metadata
        enhanced_metadata = {
            **existing_metadata,
            **curriculum_metadata.to_dict()
        }
        
        return {
            "id": item.get("id", f"curriculum_{datetime.now().timestamp()}"),
            "content": content_text,
            "metadata": enhanced_metadata
        }
    
    async def _extract_curriculum_metadata(self, content: str, existing_metadata: Dict[str, Any], learning_level: LearningLevel) -> CurriculumMetadata:
        """Extract curriculum metadata from content."""
        
        # Start with existing metadata
        metadata = CurriculumMetadata(
            content_id=existing_metadata.get("id", f"content_{datetime.now().timestamp()}"),
            title=existing_metadata.get("title", "Untitled Content"),
            description=existing_metadata.get("description", ""),
            learning_level=learning_level,
            subject_area=SubjectArea(existing_metadata.get("subject_area", "interdisciplinary"))
        )
        
        # Extract grade level information
        metadata.grade_level = self._extract_grade_level(content, existing_metadata)
        
        # Extract standards
        metadata.standards = self._extract_standards(content, existing_metadata)
        metadata.curriculum_standard = self._identify_curriculum_standard(metadata.standards)
        
        # Extract learning objectives
        metadata.learning_objectives = self._extract_learning_objectives(content)
        
        # Extract difficulty level
        metadata.difficulty_level = self._determine_difficulty_level(content, metadata.grade_level)
        
        # Extract topics and subtopics
        metadata.topic = existing_metadata.get("topic", self._extract_main_topic(content))
        metadata.subtopics = self._extract_subtopics(content)
        
        # Extract duration
        metadata.estimated_duration = self._extract_duration(content)
        
        # Extract materials
        metadata.materials_needed = self._extract_materials(content)
        
        # Extract teaching methods
        metadata.teaching_methods = self._extract_teaching_methods(content)
        
        # Set defaults based on learning level
        await self._set_level_specific_defaults(metadata, learning_level)
        
        return metadata
    
    def _extract_grade_level(self, content: str, metadata: Dict[str, Any]) -> Optional[Union[int, str]]:
        """Extract grade level from content or metadata."""
        
        # Check existing metadata first
        if "grade" in metadata or "grade_level" in metadata:
            return metadata.get("grade") or metadata.get("grade_level")
        
        # Pattern matching in content
        grade_patterns = [
            r'[Gg]rade\s+(\d+|K)',
            r'(\d+)(?:st|nd|rd|th)\s+[Gg]rade',
            r'[Kk]indergarten',
            r'(\d+)-(\d+)\s+[Gg]rades?'
        ]
        
        for pattern in grade_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if 'kindergarten' in match.group().lower():
                    return 'K'
                elif match.lastindex == 2:  # Range pattern
                    return f"{match.group(1)}-{match.group(2)}"
                else:
                    return match.group(1)
        
        return None
    
    def _extract_standards(self, content: str, metadata: Dict[str, Any]) -> List[str]:
        """Extract curriculum standards from content."""
        
        standards = metadata.get("standards", [])
        if isinstance(standards, str):
            standards = [standards]
        
        # Extract standards using patterns
        for standard_type, patterns in self.standard_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        standard_id = '-'.join(match)
                    else:
                        standard_id = match
                    
                    if standard_id not in standards:
                        standards.append(standard_id)
        
        return standards
    
    def _identify_curriculum_standard(self, standards: List[str]) -> Optional[CurriculumStandard]:
        """Identify the primary curriculum standard from a list of standards."""
        
        if not standards:
            return None
        
        # Count occurrences of each standard type
        standard_counts = {}
        
        for standard in standards:
            standard_upper = standard.upper()
            
            if 'CCSS' in standard_upper or 'COMMON CORE' in standard_upper:
                standard_counts[CurriculumStandard.COMMON_CORE] = standard_counts.get(CurriculumStandard.COMMON_CORE, 0) + 1
            elif 'NGSS' in standard_upper:
                standard_counts[CurriculumStandard.NGSS] = standard_counts.get(CurriculumStandard.NGSS, 0) + 1
            elif 'CSTA' in standard_upper:
                standard_counts[CurriculumStandard.CSTA] = standard_counts.get(CurriculumStandard.CSTA, 0) + 1
            elif 'ISTE' in standard_upper:
                standard_counts[CurriculumStandard.ISTE] = standard_counts.get(CurriculumStandard.ISTE, 0) + 1
        
        # Return the most common standard
        if standard_counts:
            return max(standard_counts, key=standard_counts.get)
        
        return CurriculumStandard.CUSTOM
    
    def _extract_learning_objectives(self, content: str) -> List[str]:
        """Extract learning objectives from content."""
        
        objectives = []
        
        # Common objective patterns
        objective_patterns = [
            r'Students will\s+(.*?)(?:\.|$)',
            r'Learners will\s+(.*?)(?:\.|$)',
            r'Objective:\s*(.*?)(?:\n|$)',
            r'Learning Goal:\s*(.*?)(?:\n|$)',
            r'By the end of this lesson.*?students will\s+(.*?)(?:\.|$)'
        ]
        
        for pattern in objective_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if match.strip() and len(match.strip()) > 10:  # Filter out very short matches
                    objectives.append(match.strip())
        
        return objectives[:5]  # Limit to 5 most relevant objectives
    
    def _determine_difficulty_level(self, content: str, grade_level: Optional[Union[int, str]]) -> str:
        """Determine difficulty level based on content and grade level."""
        
        # Check for explicit difficulty mentions
        difficulty_keywords = {
            "beginner": ["beginner", "introductory", "basic", "elementary", "simple"],
            "intermediate": ["intermediate", "moderate", "developing", "applying"],
            "advanced": ["advanced", "complex", "challenging", "sophisticated"],
            "expert": ["expert", "mastery", "professional", "competition"]
        }
        
        content_lower = content.lower()
        
        for level, keywords in difficulty_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return level
        
        # Infer from grade level
        if grade_level:
            if isinstance(grade_level, str):
                if grade_level == 'K' or grade_level.startswith('K'):
                    return "beginner"
                elif '-' in grade_level:  # Range like "3-5"
                    try:
                        start_grade = int(grade_level.split('-')[0])
                        if start_grade <= 2:
                            return "beginner"
                        elif start_grade <= 5:
                            return "intermediate"
                        else:
                            return "advanced"
                    except:
                        return "intermediate"
            elif isinstance(grade_level, int):
                if grade_level <= 2:
                    return "beginner"
                elif grade_level <= 8:
                    return "intermediate"
                else:
                    return "advanced"
        
        return "intermediate"  # Default
    
    def _extract_main_topic(self, content: str) -> str:
        """Extract the main topic from content."""
        
        # Look for topic indicators
        topic_patterns = [
            r'Topic:\s*(.*?)(?:\n|$)',
            r'Subject:\s*(.*?)(?:\n|$)',
            r'Unit:\s*(.*?)(?:\n|$)',
            r'Chapter:\s*(.*?)(?:\n|$)'
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Extract from first sentence or title-like content
        sentences = content.split('.')
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) < 100:  # Likely a title or topic
                return first_sentence
        
        return "General Topic"
    
    def _extract_subtopics(self, content: str) -> List[str]:
        """Extract subtopics from content."""
        
        subtopics = []
        
        # Look for bullet points or numbered lists
        list_patterns = [
            r'^\s*[-•*]\s*(.*?)(?:\n|$)',
            r'^\s*\d+\.\s*(.*?)(?:\n|$)',
            r'^\s*[a-zA-Z]\.\s*(.*?)(?:\n|$)'
        ]
        
        for pattern in list_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                if match.strip() and len(match.strip()) > 5:
                    subtopics.append(match.strip())
        
        return subtopics[:10]  # Limit to 10 subtopics
    
    def _extract_duration(self, content: str) -> Optional[str]:
        """Extract estimated duration from content."""
        
        duration_patterns = [
            r'Duration:\s*(.*?)(?:\n|$)',
            r'Time:\s*(.*?)(?:\n|$)',
            r'(\d+)\s*minutes?',
            r'(\d+)\s*hours?',
            r'(\d+)\s*days?',
            r'(\d+)\s*weeks?'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip() if match.lastindex == 1 else match.group(0)
        
        return None
    
    def _extract_materials(self, content: str) -> List[str]:
        """Extract materials needed from content."""
        
        materials = []
        
        # Look for materials sections
        materials_section_pattern = r'Materials?.*?:(.*?)(?:\n\n|\n[A-Z]|$)'
        match = re.search(materials_section_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if match:
            materials_text = match.group(1)
            
            # Extract individual materials
            material_items = re.findall(r'[-•*]\s*(.*?)(?:\n|$)', materials_text)
            materials.extend([item.strip() for item in material_items if item.strip()])
        
        # Look for specific material mentions
        common_materials = [
            'computer', 'tablet', 'laptop', 'robot', 'sensor', 'motor', 'LED',
            'paper', 'pencil', 'calculator', 'ruler', 'protractor',
            'blocks', 'cards', 'dice', 'timer', 'stopwatch'
        ]
        
        content_lower = content.lower()
        for material in common_materials:
            if material in content_lower and material not in [m.lower() for m in materials]:
                materials.append(material)
        
        return materials[:10]  # Limit to 10 materials
    
    def _extract_teaching_methods(self, content: str) -> List[str]:
        """Extract teaching methods from content."""
        
        methods = []
        
        # Common teaching method keywords
        method_keywords = {
            'hands-on': ['hands-on', 'hands on', 'tactile', 'manipulative'],
            'collaborative': ['collaborative', 'group work', 'team', 'pairs'],
            'inquiry': ['inquiry', 'investigation', 'explore', 'discover'],
            'demonstration': ['demonstrate', 'show', 'model'],
            'discussion': ['discuss', 'talk', 'conversation', 'debate'],
            'practice': ['practice', 'drill', 'repeat', 'exercise'],
            'project-based': ['project', 'build', 'create', 'design'],
            'technology': ['technology', 'digital', 'online', 'computer']
        }
        
        content_lower = content.lower()
        
        for method, keywords in method_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                methods.append(method)
        
        return methods
    
    async def _set_level_specific_defaults(self, metadata: CurriculumMetadata, learning_level: LearningLevel):
        """Set defaults specific to learning level."""
        
        if learning_level == LearningLevel.GRADE_LEVEL:
            # Grade-level specific defaults
            if not metadata.country:
                metadata.country = "United States"  # Default, can be configured
            
            if not metadata.teaching_methods:
                metadata.teaching_methods = ["direct_instruction", "guided_practice"]
        
        elif learning_level == LearningLevel.GLOBAL_LEARNING:
            # Global learning defaults
            metadata.cultural_context = metadata.cultural_context or ["international"]
            
            if not metadata.teaching_methods:
                metadata.teaching_methods = ["inquiry", "collaborative", "multicultural"]
        
        elif learning_level == LearningLevel.GLOBAL_COMPETITION:
            # Competition defaults
            metadata.difficulty_level = "advanced" if metadata.difficulty_level == "intermediate" else metadata.difficulty_level
            
            if not metadata.teaching_methods:
                metadata.teaching_methods = ["problem_solving", "independent_study", "mentorship"]
            
            metadata.assessment_methods = metadata.assessment_methods or ["performance_based", "portfolio"]
    
    async def search_curriculum(self, 
                              query: str, 
                              learning_levels: Optional[List[LearningLevel]] = None,
                              filters: Optional[Dict[str, Any]] = None,
                              top_k: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Search curriculum content with level and filter support."""
        
        # Determine collections to search
        if learning_levels is None:
            learning_levels = list(LearningLevel)
        
        collection_ids = []
        for level in learning_levels:
            if level in self.level_collections:
                collection_ids.append(self.level_collections[level])
        
        # Search with or without filters
        if filters:
            results = await self.rag_engine.similarity_search_with_metadata(
                query, filters, collection_ids
            )
        else:
            results = await self.rag_engine.search(query, collection_ids, top_k)
        
        # Add learning level information to results
        enhanced_results = {}
        for collection_id, collection_results in results.items():
            # Find the learning level for this collection
            level_name = "unknown"
            for level, coll_id in self.level_collections.items():
                if coll_id == collection_id:
                    level_name = level.value
                    break
            
            enhanced_results[level_name] = collection_results
        
        return enhanced_results
    
    async def get_curriculum_by_standard(self, standard: str, learning_levels: Optional[List[LearningLevel]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get curriculum content aligned to a specific standard."""
        
        return await self.search_curriculum(
            query=f"standard {standard}",
            learning_levels=learning_levels,
            filters={"standards": [standard]}
        )
    
    async def get_curriculum_by_grade(self, grade: Union[int, str], subject: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get curriculum content for a specific grade level."""
        
        filters = {"grade_level": grade}
        if subject:
            filters["subject_area"] = subject
        
        query = f"grade {grade}"
        if subject:
            query += f" {subject}"
        
        return await self.search_curriculum(
            query=query,
            learning_levels=[LearningLevel.GRADE_LEVEL],
            filters=filters
        )
    
    async def get_competition_resources(self, competition_type: str, difficulty: str = "advanced") -> List[Dict[str, Any]]:
        """Get resources for specific competition types."""
        
        results = await self.search_curriculum(
            query=f"{competition_type} competition resources",
            learning_levels=[LearningLevel.GLOBAL_COMPETITION],
            filters={"difficulty_level": difficulty}
        )
        
        return results.get("global_competition", [])
    
    def get_collection_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all curriculum collections."""
        
        stats = {}
        
        for level, collection_id in self.level_collections.items():
            collection_stats = asyncio.create_task(
                self.rag_engine.get_collection_statistics(collection_id)
            )
            stats[level.value] = collection_stats
        
        return stats


# Example usage and testing
async def main():
    """Example usage of the curriculum indexer."""
    print("=== Curriculum Indexer Demo ===")
    
    # Initialize components
    from .rag_engine import RAGEngine
    
    rag = RAGEngine()
    indexer = CurriculumIndexer(rag)
    
    await indexer.initialize_collections()
    
    # Sample grade-level curriculum content
    grade_level_content = [
        {
            "id": "grade3_math_fractions",
            "content": "Grade 3 Mathematics: Understanding Fractions. Students will develop understanding of fractions as numbers. CCSS.MATH.3.NF.A.1: Understand a fraction 1/b as the quantity formed by 1 part when a whole is partitioned into b equal parts. Students will use visual models, manipulatives, and real-world examples to explore fractions. Duration: 2 weeks. Materials: fraction bars, pie charts, manipulatives.",
            "metadata": {
                "title": "Understanding Fractions",
                "subject_area": "mathematics",
                "grade": 3,
                "topic": "fractions"
            }
        },
        {
            "id": "grade5_science_ecosystems",
            "content": "Grade 5 Science: Ecosystems and Environment. Students will analyze and interpret data to provide evidence that plants and animals have traits inherited from parents. NGSS 5-LS2-1: Develop a model to describe the movement of matter among plants, animals, decomposers, and the environment. Through hands-on investigation and collaborative inquiry, students will explore food webs and energy transfer. Duration: 3 weeks.",
            "metadata": {
                "title": "Ecosystems and Environment",
                "subject_area": "science",
                "grade": 5,
                "topic": "ecosystems"
            }
        }
    ]
    
    await indexer.index_curriculum_content(grade_level_content, LearningLevel.GRADE_LEVEL)
    
    # Sample global competition content
    competition_content = [
        {
            "id": "robotics_competition_advanced",
            "content": "Advanced Robotics Competition Preparation: Programming autonomous navigation systems using advanced sensor fusion techniques. Teams will implement SLAM (Simultaneous Localization and Mapping) algorithms for complex environment navigation. Requires knowledge of linear algebra, probability theory, and advanced programming concepts. Materials: advanced robotics platform, LIDAR, IMU, computer vision system.",
            "metadata": {
                "title": "Advanced Robotics Navigation",
                "subject_area": "robotics",
                "topic": "autonomous_navigation",
                "difficulty_level": "expert"
            }
        },
        {
            "id": "math_olympiad_prep",
            "content": "International Mathematical Olympiad Preparation: Advanced problem-solving techniques in number theory, combinatorics, and geometry. Students will work through challenging problems requiring creative mathematical thinking and rigorous proof techniques. Focus on developing competition strategies and time management skills.",
            "metadata": {
                "title": "Math Olympiad Preparation",
                "subject_area": "mathematics",
                "topic": "competition_math",
                "difficulty_level": "expert"
            }
        }
    ]
    
    await indexer.index_curriculum_content(competition_content, LearningLevel.GLOBAL_COMPETITION)
    
    # Test searches
    print("\n--- Testing Grade-Level Search ---")
    grade_results = await indexer.get_curriculum_by_grade(3, "mathematics")
    for level, results in grade_results.items():
        print(f"Level: {level}")
        for result in results:
            print(f"  - {result['metadata'].get('title', 'No title')}: {result['text'][:100]}...")
    
    print("\n--- Testing Competition Resources ---")
    comp_results = await indexer.get_competition_resources("robotics")
    for result in comp_results:
        print(f"  - {result['metadata'].get('title', 'No title')}: {result['text'][:100]}...")
    
    print("\n--- Testing Cross-Level Search ---")
    all_results = await indexer.search_curriculum("mathematics problem solving")
    for level, results in all_results.items():
        if results:
            print(f"Level: {level} ({len(results)} results)")
            for result in results[:1]:
                print(f"  - {result['text'][:80]}...")
    
    print("\n=== Curriculum Indexer Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())