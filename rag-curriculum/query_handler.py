"""
Query Handler
Intelligent query processing and context generation for educational RAG system
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
from datetime import datetime
import re
from collections import Counter

from .rag_engine import RAGEngine
from .curriculum_indexer import CurriculumIndexer, LearningLevel, SubjectArea
from .resource_processor import ResourceProcessor, ResourceType


class QueryIntent(Enum):
    """Different types of query intents."""
    CURRICULUM_SEARCH = "curriculum_search"
    RESOURCE_LOOKUP = "resource_lookup"
    LESSON_PLANNING = "lesson_planning"
    STANDARDS_ALIGNMENT = "standards_alignment"
    ASSESSMENT_HELP = "assessment_help"
    TROUBLESHOOTING = "troubleshooting"
    COMPARISON = "comparison"
    EXPLANATION = "explanation"
    EXAMPLE_REQUEST = "example_request"
    GENERAL_INQUIRY = "general_inquiry"


class QueryComplexity(Enum):
    """Query complexity levels."""
    SIMPLE = "simple"          # Single topic, direct answer
    MODERATE = "moderate"      # Multiple topics, some analysis needed
    COMPLEX = "complex"        # Multi-faceted, requires synthesis
    RESEARCH = "research"      # Deep analysis, multiple sources needed


@dataclass
class QueryContext:
    """Context information for processing queries."""
    # Query identification
    query_id: str
    original_query: str
    processed_query: str
    
    # Intent and complexity
    intent: QueryIntent
    complexity: QueryComplexity
    confidence_score: float
    
    # Educational context
    target_audience: List[str] = field(default_factory=list)  # students, teachers, parents
    learning_levels: List[LearningLevel] = field(default_factory=list)
    subject_areas: List[SubjectArea] = field(default_factory=list)
    grade_levels: List[Union[int, str]] = field(default_factory=list)
    
    # Query characteristics
    keywords: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    
    # Resource preferences
    preferred_resource_types: List[ResourceType] = field(default_factory=list)
    content_formats: List[str] = field(default_factory=list)
    
    # Contextual constraints
    time_constraint: Optional[str] = None  # "quick answer", "detailed analysis"
    depth_preference: str = "moderate"     # "brief", "moderate", "comprehensive"
    
    # User context
    user_role: Optional[str] = None        # "teacher", "student", "parent", "administrator"
    experience_level: str = "intermediate" # "beginner", "intermediate", "advanced"
    
    # Processing metadata
    timestamp: datetime = field(default_factory=datetime.now)
    processing_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, list):
                result[key] = [
                    item.value if isinstance(item, Enum) else item 
                    for item in value
                ]
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result


@dataclass
class QueryResponse:
    """Response to a user query."""
    # Response identification
    response_id: str
    query_context: QueryContext
    
    # Main response content
    primary_answer: str
    supporting_information: List[str] = field(default_factory=list)
    
    # Source information
    sources_used: List[Dict[str, Any]] = field(default_factory=list)
    total_sources: int = 0
    source_quality_score: float = 0.0
    
    # Response characteristics
    confidence_score: float = 0.0
    completeness_score: float = 0.0
    relevance_score: float = 0.0
    
    # Educational value
    learning_objectives_addressed: List[str] = field(default_factory=list)
    standards_alignment: List[str] = field(default_factory=list)
    suggested_follow_ups: List[str] = field(default_factory=list)
    
    # Additional resources
    related_resources: List[Dict[str, Any]] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    
    # Response metadata
    generation_time: float = 0.0
    total_processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "response_id": self.response_id,
            "query_context": self.query_context.to_dict(),
            "primary_answer": self.primary_answer,
            "supporting_information": self.supporting_information,
            "sources_used": self.sources_used,
            "confidence_score": self.confidence_score,
            "completeness_score": self.completeness_score,
            "learning_objectives_addressed": self.learning_objectives_addressed,
            "standards_alignment": self.standards_alignment,
            "suggested_follow_ups": self.suggested_follow_ups,
            "related_resources": self.related_resources,
            "next_steps": self.next_steps,
            "generation_time": self.generation_time,
            "total_processing_time": self.total_processing_time
        }


class QueryAnalyzer:
    """Analyzes queries to extract intent, context, and requirements."""
    
    def __init__(self):
        self.logger = logging.getLogger("query_analyzer")
        
        # Intent classification patterns
        self.intent_patterns = {
            QueryIntent.CURRICULUM_SEARCH: [
                r'curriculum', r'standards?', r'grade \d+', r'learning objectives?',
                r'scope and sequence', r'pacing guide'
            ],
            QueryIntent.RESOURCE_LOOKUP: [
                r'resources?', r'materials?', r'documents?', r'guides?',
                r'templates?', r'examples?', r'activities?'
            ],
            QueryIntent.LESSON_PLANNING: [
                r'lesson plan', r'teaching', r'activities?', r'projects?',
                r'how to teach', r'classroom', r'instruction'
            ],
            QueryIntent.STANDARDS_ALIGNMENT: [
                r'standards?', r'ccss', r'ngss', r'alignment', r'meets standards?',
                r'common core', r'state standards?'
            ],
            QueryIntent.ASSESSMENT_HELP: [
                r'assess', r'rubric', r'grading', r'evaluation', r'test',
                r'quiz', r'assignment', r'scoring'
            ],
            QueryIntent.TROUBLESHOOTING: [
                r'problem', r'issue', r'error', r'fix', r'troubleshoot',
                r'not working', r'help with', r'debugging'
            ],
            QueryIntent.COMPARISON: [
                r'compare', r'versus', r'vs', r'difference', r'similar',
                r'contrast', r'better', r'which'
            ],
            QueryIntent.EXPLANATION: [
                r'what is', r'explain', r'how does', r'why', r'concept',
                r'definition', r'meaning', r'understand'
            ],
            QueryIntent.EXAMPLE_REQUEST: [
                r'example', r'sample', r'instance', r'case study',
                r'show me', r'demonstrate'
            ]
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            QueryComplexity.SIMPLE: [
                r'^what is', r'^define', r'^explain', r'simple',
                r'basic', r'quick'
            ],
            QueryComplexity.COMPLEX: [
                r'compare and contrast', r'analyze', r'evaluate',
                r'synthesize', r'comprehensive', r'detailed analysis'
            ],
            QueryComplexity.RESEARCH: [
                r'research', r'in-depth', r'thorough', r'extensive',
                r'multiple perspectives', r'literature review'
            ]
        }
        
        # Subject area keywords
        self.subject_keywords = {
            SubjectArea.MATHEMATICS: [
                'math', 'mathematics', 'algebra', 'geometry', 'calculus',
                'statistics', 'probability', 'arithmetic', 'fractions'
            ],
            SubjectArea.SCIENCE: [
                'science', 'biology', 'chemistry', 'physics', 'earth science',
                'life science', 'physical science', 'experiments'
            ],
            SubjectArea.TECHNOLOGY: [
                'technology', 'computer', 'digital', 'coding', 'programming',
                'software', 'hardware', 'IT'
            ],
            SubjectArea.ENGINEERING: [
                'engineering', 'design', 'build', 'construction', 'mechanical',
                'electrical', 'civil', 'aerospace'
            ],
            SubjectArea.ROBOTICS: [
                'robot', 'robotics', 'automation', 'sensors', 'actuators',
                'programming robots', 'robotics competition'
            ]
        }
        
        # Audience indicators
        self.audience_keywords = {
            'students': ['student', 'learner', 'kids', 'children'],
            'teachers': ['teacher', 'instructor', 'educator', 'teaching'],
            'parents': ['parent', 'family', 'home', 'guardian'],
            'administrators': ['administrator', 'principal', 'district']
        }
    
    async def analyze_query(self, query: str, user_context: Optional[Dict[str, Any]] = None) -> QueryContext:
        """Analyze a query and extract context information."""
        
        start_time = datetime.now()
        query_id = f"query_{start_time.timestamp()}"
        
        # Basic preprocessing
        processed_query = self._preprocess_query(query)
        
        # Extract intent
        intent, intent_confidence = self._classify_intent(processed_query)
        
        # Determine complexity
        complexity = self._determine_complexity(processed_query)
        
        # Extract educational context
        learning_levels = self._extract_learning_levels(processed_query)
        subject_areas = self._extract_subject_areas(processed_query)
        grade_levels = self._extract_grade_levels(processed_query)
        
        # Extract query characteristics
        keywords = self._extract_keywords(processed_query)
        entities = self._extract_entities(processed_query)
        topics = self._extract_topics(processed_query)
        
        # Determine target audience
        target_audience = self._identify_target_audience(processed_query, user_context)
        
        # Extract preferences
        preferred_resource_types = self._identify_preferred_resource_types(processed_query)
        
        # Create context
        context = QueryContext(
            query_id=query_id,
            original_query=query,
            processed_query=processed_query,
            intent=intent,
            complexity=complexity,
            confidence_score=intent_confidence,
            target_audience=target_audience,
            learning_levels=learning_levels,
            subject_areas=subject_areas,
            grade_levels=grade_levels,
            keywords=keywords,
            entities=entities,
            topics=topics,
            preferred_resource_types=preferred_resource_types
        )
        
        # Add user context if provided
        if user_context:
            context.user_role = user_context.get('role')
            context.experience_level = user_context.get('experience_level', 'intermediate')
            context.time_constraint = user_context.get('time_constraint')
            context.depth_preference = user_context.get('depth_preference', 'moderate')
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        context.processing_time = processing_time
        
        return context
    
    def _preprocess_query(self, query: str) -> str:
        """Preprocess query text."""
        
        # Basic cleaning
        processed = query.lower().strip()
        
        # Remove extra whitespace
        processed = re.sub(r'\s+', ' ', processed)
        
        # Expand common abbreviations
        abbreviations = {
            'k-12': 'kindergarten through grade 12',
            'elem': 'elementary',
            'ms': 'middle school',
            'hs': 'high school',
            'ccss': 'common core state standards',
            'ngss': 'next generation science standards',
            'stem': 'science technology engineering mathematics'
        }
        
        for abbrev, expansion in abbreviations.items():
            processed = processed.replace(abbrev, expansion)
        
        return processed
    
    def _classify_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """Classify query intent with confidence score."""
        
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches
            
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            max_score = intent_scores[best_intent]
            total_score = sum(intent_scores.values())
            confidence = max_score / total_score
            
            return best_intent, confidence
        
        # Default to general inquiry
        return QueryIntent.GENERAL_INQUIRY, 0.5
    
    def _determine_complexity(self, query: str) -> QueryComplexity:
        """Determine query complexity."""
        
        # Check for explicit complexity indicators
        for complexity, patterns in self.complexity_indicators.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return complexity
        
        # Analyze query characteristics
        word_count = len(query.split())
        question_words = len(re.findall(r'\b(what|how|why|when|where|which|who)\b', query, re.IGNORECASE))
        
        # Simple heuristics
        if word_count < 5 or query.startswith(('what is', 'define')):
            return QueryComplexity.SIMPLE
        elif word_count > 20 or question_words > 2:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.MODERATE
    
    def _extract_learning_levels(self, query: str) -> List[LearningLevel]:
        """Extract learning levels from query."""
        
        levels = []
        
        # Grade level indicators
        if any(term in query for term in ['grade', 'elementary', 'k-12', 'primary', 'secondary']):
            levels.append(LearningLevel.GRADE_LEVEL)
        
        # Global learning indicators
        if any(term in query for term in ['international', 'global', 'cross-cultural', 'worldwide']):
            levels.append(LearningLevel.GLOBAL_LEARNING)
        
        # Competition indicators
        if any(term in query for term in ['competition', 'contest', 'olympiad', 'championship', 'advanced']):
            levels.append(LearningLevel.GLOBAL_COMPETITION)
        
        # Default to grade level if none found
        return levels if levels else [LearningLevel.GRADE_LEVEL]
    
    def _extract_subject_areas(self, query: str) -> List[SubjectArea]:
        """Extract subject areas from query."""
        
        found_subjects = []
        
        for subject, keywords in self.subject_keywords.items():
            if any(keyword in query for keyword in keywords):
                found_subjects.append(subject)
        
        return found_subjects
    
    def _extract_grade_levels(self, query: str) -> List[Union[int, str]]:
        """Extract specific grade levels from query."""
        
        grade_levels = []
        
        # Pattern matching for grades
        grade_patterns = [
            r'grade (\d+)',
            r'(\d+)(?:st|nd|rd|th) grade',
            r'kindergarten',
            r'k-(\d+)',
            r'grades? (\d+)-(\d+)'
        ]
        
        for pattern in grade_patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                if 'kindergarten' in match.group().lower():
                    grade_levels.append('K')
                elif match.lastindex == 2:  # Range pattern
                    start_grade = int(match.group(1))
                    end_grade = int(match.group(2))
                    grade_levels.extend(list(range(start_grade, end_grade + 1)))
                else:
                    try:
                        grade = int(match.group(1))
                        grade_levels.append(grade)
                    except ValueError:
                        continue
        
        return list(set(grade_levels))  # Remove duplicates
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query."""
        
        # Remove common stop words
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'how', 'what', 'when', 'where',
            'why', 'who', 'which', 'can', 'could', 'should', 'would', 'do', 'does'
        }
        
        words = query.split()
        keywords = []
        
        for word in words:
            # Clean word
            clean_word = re.sub(r'[^\w]', '', word).lower()
            
            # Keep if not stop word and length > 2
            if clean_word not in stop_words and len(clean_word) > 2:
                keywords.append(clean_word)
        
        return keywords
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract named entities from query."""
        
        entities = []
        
        # Simple pattern-based entity extraction
        # Capitalized words (potential proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', query)
        entities.extend(capitalized)
        
        # Standards and frameworks
        standards = re.findall(r'\b(?:CCSS|NGSS|CSTA|ISTE)\b', query, re.IGNORECASE)
        entities.extend(standards)
        
        # Grade specifications
        grades = re.findall(r'\b(?:Grade \d+|K-\d+|\d+(?:st|nd|rd|th) Grade)\b', query, re.IGNORECASE)
        entities.extend(grades)
        
        return list(set(entities))  # Remove duplicates
    
    def _extract_topics(self, query: str) -> List[str]:
        """Extract main topics from query."""
        
        # Look for noun phrases and important terms
        # This is a simplified approach - could be enhanced with NLP libraries
        
        topics = []
        
        # Multi-word topics (simple patterns)
        multi_word_patterns = [
            r'\b(?:lesson plan|classroom management|student engagement)\b',
            r'\b(?:learning objectives?|teaching strategies?|assessment methods?)\b',
            r'\b(?:curriculum design|instructional design|educational technology)\b'
        ]
        
        for pattern in multi_word_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            topics.extend(matches)
        
        # Single important words
        keywords = self._extract_keywords(query)
        
        # Filter for educational topics
        educational_terms = [
            'curriculum', 'lesson', 'teaching', 'learning', 'assessment',
            'instruction', 'education', 'classroom', 'student', 'teacher'
        ]
        
        for keyword in keywords:
            if keyword in educational_terms or len(keyword) > 6:
                topics.append(keyword)
        
        return topics[:10]  # Limit to top 10 topics
    
    def _identify_target_audience(self, query: str, user_context: Optional[Dict[str, Any]]) -> List[str]:
        """Identify target audience for the query."""
        
        audiences = []
        
        # Check explicit mentions
        for audience, keywords in self.audience_keywords.items():
            if any(keyword in query for keyword in keywords):
                audiences.append(audience)
        
        # Use user context if available
        if user_context and 'role' in user_context:
            role = user_context['role']
            if role not in audiences:
                audiences.append(role)
        
        # Default based on query type
        if not audiences:
            if any(term in query for term in ['teach', 'instruction', 'classroom']):
                audiences.append('teachers')
            elif any(term in query for term in ['learn', 'study', 'homework']):
                audiences.append('students')
            else:
                audiences.append('teachers')  # Default
        
        return audiences
    
    def _identify_preferred_resource_types(self, query: str) -> List[ResourceType]:
        """Identify preferred resource types from query."""
        
        resource_types = []
        
        type_keywords = {
            ResourceType.USER_GUIDE: ['guide', 'instructions', 'how to'],
            ResourceType.TUTORIAL: ['tutorial', 'walkthrough', 'learn'],
            ResourceType.LESSON_PLAN: ['lesson plan', 'lesson', 'teaching plan'],
            ResourceType.ACTIVITY_GUIDE: ['activity', 'activities', 'hands-on'],
            ResourceType.ASSESSMENT_RUBRIC: ['rubric', 'assessment', 'grading'],
            ResourceType.WORKSHEET: ['worksheet', 'practice', 'exercises'],
            ResourceType.REFERENCE_MANUAL: ['reference', 'manual', 'documentation'],
            ResourceType.FAQ: ['faq', 'questions', 'common questions'],
            ResourceType.TROUBLESHOOTING_GUIDE: ['troubleshoot', 'problems', 'issues']
        }
        
        for resource_type, keywords in type_keywords.items():
            if any(keyword in query for keyword in keywords):
                resource_types.append(resource_type)
        
        return resource_types


class QueryHandler:
    """Main query handler that coordinates analysis, retrieval, and response generation."""
    
    def __init__(self, 
                 rag_engine: RAGEngine,
                 curriculum_indexer: CurriculumIndexer,
                 resource_processor: ResourceProcessor):
        
        self.rag_engine = rag_engine
        self.curriculum_indexer = curriculum_indexer
        self.resource_processor = resource_processor
        self.analyzer = QueryAnalyzer()
        
        self.logger = logging.getLogger("query_handler")
        
        # Response generation settings
        self.max_context_length = 4000
        self.max_sources = 10
        self.relevance_threshold = 0.6
    
    async def handle_query(self, query: str, user_context: Optional[Dict[str, Any]] = None) -> QueryResponse:
        """Handle a complete query from analysis to response generation."""
        
        start_time = datetime.now()
        
        # Step 1: Analyze query
        query_context = await self.analyzer.analyze_query(query, user_context)
        
        # Step 2: Retrieve relevant information
        search_results = await self._retrieve_information(query_context)
        
        # Step 3: Generate response
        response = await self._generate_response(query_context, search_results)
        
        # Calculate total processing time
        total_time = (datetime.now() - start_time).total_seconds()
        response.total_processing_time = total_time
        
        return response
    
    async def _retrieve_information(self, context: QueryContext) -> Dict[str, Any]:
        """Retrieve relevant information based on query context."""
        
        search_results = {
            "curriculum": [],
            "resources": [],
            "context_info": {}
        }
        
        # Curriculum search
        if context.intent in [QueryIntent.CURRICULUM_SEARCH, QueryIntent.STANDARDS_ALIGNMENT, QueryIntent.LESSON_PLANNING]:
            curriculum_results = await self.curriculum_indexer.search_curriculum(
                context.processed_query,
                learning_levels=context.learning_levels,
                top_k=self.max_sources // 2
            )
            
            # Flatten curriculum results
            for level, results in curriculum_results.items():
                for result in results:
                    result['source_type'] = 'curriculum'
                    result['learning_level'] = level
                    search_results["curriculum"].append(result)
        
        # Resource search
        if context.intent in [QueryIntent.RESOURCE_LOOKUP, QueryIntent.LESSON_PLANNING, QueryIntent.ASSESSMENT_HELP]:
            resource_results = await self.resource_processor.search_resources(
                context.processed_query,
                resource_types=context.preferred_resource_types if context.preferred_resource_types else None,
                learning_levels=context.learning_levels
            )
            
            # Flatten resource results
            for level, results in resource_results.items():
                for result in results:
                    result['source_type'] = 'resource'
                    result['learning_level'] = level
                    search_results["resources"].append(result)
        
        # General RAG search if no specific results
        if not search_results["curriculum"] and not search_results["resources"]:
            general_context = await self.rag_engine.get_context_for_query(
                context.processed_query,
                max_context_length=self.max_context_length
            )
            search_results["context_info"] = general_context
        
        return search_results
    
    async def _generate_response(self, context: QueryContext, search_results: Dict[str, Any]) -> QueryResponse:
        """Generate a comprehensive response based on context and search results."""
        
        response_start = datetime.now()
        response_id = f"response_{response_start.timestamp()}"
        
        # Combine and rank all results
        all_results = []
        all_results.extend(search_results.get("curriculum", []))
        all_results.extend(search_results.get("resources", []))
        
        # Add context info results if available
        context_info = search_results.get("context_info", {})
        if context_info.get("context_chunks"):
            for chunk in context_info["context_chunks"]:
                all_results.append({
                    "text": chunk["text"],
                    "metadata": {"source": chunk["source"]},
                    "distance": 1.0 - chunk["relevance_score"],
                    "source_type": "general"
                })
        
        # Sort by relevance (lower distance = higher relevance)
        all_results.sort(key=lambda x: x.get("distance", 1.0))
        
        # Filter by relevance threshold
        relevant_results = [
            result for result in all_results 
            if (1.0 - result.get("distance", 1.0)) >= self.relevance_threshold
        ]
        
        # Limit number of sources
        top_results = relevant_results[:self.max_sources]
        
        # Generate primary answer
        primary_answer = await self._generate_primary_answer(context, top_results)
        
        # Generate supporting information
        supporting_info = await self._generate_supporting_information(context, top_results)
        
        # Extract standards alignment
        standards_alignment = self._extract_standards_alignment(top_results)
        
        # Generate follow-up suggestions
        follow_ups = await self._generate_follow_ups(context, top_results)
        
        # Find related resources
        related_resources = await self._find_related_resources(context, top_results)
        
        # Calculate quality scores
        confidence_score = self._calculate_confidence_score(context, top_results)
        completeness_score = self._calculate_completeness_score(context, top_results)
        relevance_score = self._calculate_relevance_score(top_results)
        
        # Create response
        response = QueryResponse(
            response_id=response_id,
            query_context=context,
            primary_answer=primary_answer,
            supporting_information=supporting_info,
            sources_used=self._format_sources(top_results),
            total_sources=len(top_results),
            confidence_score=confidence_score,
            completeness_score=completeness_score,
            relevance_score=relevance_score,
            standards_alignment=standards_alignment,
            suggested_follow_ups=follow_ups,
            related_resources=related_resources,
            generation_time=(datetime.now() - response_start).total_seconds()
        )
        
        return response
    
    async def _generate_primary_answer(self, context: QueryContext, results: List[Dict[str, Any]]) -> str:
        """Generate the primary answer based on query context and results."""
        
        if not results:
            return self._generate_fallback_answer(context)
        
        # Build answer based on intent
        if context.intent == QueryIntent.EXPLANATION:
            return self._generate_explanation_answer(context, results)
        elif context.intent == QueryIntent.CURRICULUM_SEARCH:
            return self._generate_curriculum_answer(context, results)
        elif context.intent == QueryIntent.RESOURCE_LOOKUP:
            return self._generate_resource_answer(context, results)
        elif context.intent == QueryIntent.LESSON_PLANNING:
            return self._generate_lesson_planning_answer(context, results)
        elif context.intent == QueryIntent.ASSESSMENT_HELP:
            return self._generate_assessment_answer(context, results)
        else:
            return self._generate_general_answer(context, results)
    
    def _generate_fallback_answer(self, context: QueryContext) -> str:
        """Generate fallback answer when no relevant results found."""
        
        base_answer = f"I understand you're asking about {' '.join(context.keywords[:3])}. "
        
        if context.subject_areas:
            subject_names = [subject.value.replace('_', ' ').title() for subject in context.subject_areas]
            base_answer += f"This relates to {', '.join(subject_names)}. "
        
        if context.grade_levels:
            grade_text = ', '.join([f"Grade {g}" if isinstance(g, int) else str(g) for g in context.grade_levels])
            base_answer += f"For {grade_text} students, "
        
        base_answer += "I'd recommend exploring curriculum standards, educational resources, and best practices in this area. "
        base_answer += "Consider checking with your local education standards and professional development resources."
        
        return base_answer
    
    def _generate_explanation_answer(self, context: QueryContext, results: List[Dict[str, Any]]) -> str:
        """Generate explanation-focused answer."""
        
        answer_parts = []
        
        # Start with direct explanation
        if results:
            first_result = results[0]
            text = first_result.get("text", "")
            
            # Extract key concepts
            sentences = text.split('.')
            relevant_sentences = []
            
            for sentence in sentences[:5]:  # First 5 sentences
                sentence = sentence.strip()
                if any(keyword in sentence.lower() for keyword in context.keywords[:3]):
                    relevant_sentences.append(sentence)
            
            if relevant_sentences:
                answer_parts.append(' '.join(relevant_sentences) + '.')
        
        # Add context if available
        if context.subject_areas:
            subject_names = [subject.value.replace('_', ' ').title() for subject in context.subject_areas]
            answer_parts.append(f"This concept is important in {', '.join(subject_names)}.")
        
        # Add grade-level context
        if context.grade_levels:
            grade_text = ', '.join([f"Grade {g}" if isinstance(g, int) else str(g) for g in context.grade_levels])
            answer_parts.append(f"For {grade_text} students, this topic is typically introduced with hands-on activities and visual examples.")
        
        return ' '.join(answer_parts) if answer_parts else self._generate_fallback_answer(context)
    
    def _generate_curriculum_answer(self, context: QueryContext, results: List[Dict[str, Any]]) -> str:
        """Generate curriculum-focused answer."""
        
        answer_parts = []
        
        # Identify curriculum content
        curriculum_results = [r for r in results if r.get("source_type") == "curriculum"]
        
        if curriculum_results:
            # Summarize learning objectives
            all_objectives = []
            for result in curriculum_results[:3]:
                metadata = result.get("metadata", {})
                objectives = metadata.get("learning_objectives", [])
                all_objectives.extend(objectives)
            
            if all_objectives:
                answer_parts.append("Key learning objectives include:")
                for obj in all_objectives[:5]:  # Top 5 objectives
                    answer_parts.append(f"• {obj}")
        
        # Add standards information
        standards = self._extract_standards_alignment(results)
        if standards:
            answer_parts.append(f"This aligns with standards: {', '.join(standards[:3])}")
        
        # Add grade level information
        if context.grade_levels:
            grade_text = ', '.join([f"Grade {g}" if isinstance(g, int) else str(g) for g in context.grade_levels])
            answer_parts.append(f"Appropriate for {grade_text} students.")
        
        return '\n'.join(answer_parts) if answer_parts else self._generate_fallback_answer(context)
    
    def _generate_resource_answer(self, context: QueryContext, results: List[Dict[str, Any]]) -> str:
        """Generate resource-focused answer."""
        
        answer_parts = []
        
        # Categorize resources
        resource_types = {}
        for result in results:
            if result.get("source_type") == "resource":
                metadata = result.get("metadata", {})
                res_type = metadata.get("resource_type", "general")
                if res_type not in resource_types:
                    resource_types[res_type] = []
                resource_types[res_type].append(result)
        
        # Describe available resources
        if resource_types:
            answer_parts.append("Available resources include:")
            
            for res_type, resources in resource_types.items():
                type_name = res_type.replace('_', ' ').title()
                count = len(resources)
                
                answer_parts.append(f"• {type_name}: {count} resource{'s' if count > 1 else ''}")
                
                # Add details for top resources
                for resource in resources[:2]:
                    metadata = resource.get("metadata", {})
                    title = metadata.get("title", "Untitled Resource")
                    answer_parts.append(f"  - {title}")
        
        return '\n'.join(answer_parts) if answer_parts else self._generate_fallback_answer(context)
    
    def _generate_lesson_planning_answer(self, context: QueryContext, results: List[Dict[str, Any]]) -> str:
        """Generate lesson planning focused answer."""
        
        answer_parts = []
        
        # Structure as lesson planning guidance
        answer_parts.append("For lesson planning, consider these key elements:")
        
        # Learning objectives
        objectives = []
        for result in results[:3]:
            metadata = result.get("metadata", {})
            result_objectives = metadata.get("learning_objectives", [])
            objectives.extend(result_objectives)
        
        if objectives:
            answer_parts.append("\nLearning Objectives:")
            for obj in objectives[:3]:
                answer_parts.append(f"• {obj}")
        
        # Materials and resources
        materials = []
        for result in results:
            metadata = result.get("metadata", {})
            result_materials = metadata.get("materials_needed", [])
            materials.extend(result_materials)
        
        if materials:
            unique_materials = list(set(materials))
            answer_parts.append(f"\nMaterials Needed: {', '.join(unique_materials[:5])}")
        
        # Duration
        durations = []
        for result in results:
            metadata = result.get("metadata", {})
            duration = metadata.get("estimated_duration")
            if duration:
                durations.append(duration)
        
        if durations:
            answer_parts.append(f"\nEstimated Duration: {durations[0]}")
        
        return '\n'.join(answer_parts) if answer_parts else self._generate_fallback_answer(context)
    
    def _generate_assessment_answer(self, context: QueryContext, results: List[Dict[str, Any]]) -> str:
        """Generate assessment-focused answer."""
        
        answer_parts = []
        
        # Look for assessment-related content
        assessment_results = [
            r for r in results 
            if 'assessment' in r.get("metadata", {}).get("resource_type", "").lower() or
               'rubric' in r.get("text", "").lower()
        ]
        
        if assessment_results:
            answer_parts.append("Assessment approaches include:")
            
            for result in assessment_results[:3]:
                text = result.get("text", "")
                # Extract assessment methods
                if "criteria" in text.lower():
                    sentences = text.split('.')
                    criteria_sentences = [s for s in sentences if "criteria" in s.lower()]
                    if criteria_sentences:
                        answer_parts.append(f"• {criteria_sentences[0].strip()}")
        
        # Add general assessment guidance
        if context.subject_areas:
            subject_names = [subject.value.replace('_', ' ').title() for subject in context.subject_areas]
            answer_parts.append(f"\nFor {', '.join(subject_names)}, consider both formative and summative assessments.")
        
        return '\n'.join(answer_parts) if answer_parts else self._generate_fallback_answer(context)
    
    def _generate_general_answer(self, context: QueryContext, results: List[Dict[str, Any]]) -> str:
        """Generate general answer from results."""
        
        if not results:
            return self._generate_fallback_answer(context)
        
        # Combine information from top results
        answer_parts = []
        
        for result in results[:3]:
            text = result.get("text", "")
            
            # Extract relevant sentences
            sentences = text.split('.')
            relevant_sentences = []
            
            for sentence in sentences[:3]:
                sentence = sentence.strip()
                if any(keyword in sentence.lower() for keyword in context.keywords[:3]):
                    relevant_sentences.append(sentence)
            
            if relevant_sentences:
                answer_parts.extend(relevant_sentences)
        
        if answer_parts:
            return '. '.join(answer_parts[:5]) + '.'  # Limit to 5 sentences
        else:
            return self._generate_fallback_answer(context)
    
    async def _generate_supporting_information(self, context: QueryContext, results: List[Dict[str, Any]]) -> List[str]:
        """Generate supporting information."""
        
        supporting_info = []
        
        # Add context about learning levels
        if context.learning_levels:
            level_names = [level.value.replace('_', ' ').title() for level in context.learning_levels]
            supporting_info.append(f"This information applies to: {', '.join(level_names)}")
        
        # Add subject area context
        if context.subject_areas:
            subject_names = [subject.value.replace('_', ' ').title() for subject in context.subject_areas]
            supporting_info.append(f"Subject areas covered: {', '.join(subject_names)}")
        
        # Add source variety information
        source_types = set(result.get("source_type", "unknown") for result in results)
        if len(source_types) > 1:
            supporting_info.append(f"Information gathered from {len(source_types)} different source types")
        
        # Add complexity context
        if context.complexity != QueryComplexity.SIMPLE:
            complexity_text = context.complexity.value.replace('_', ' ').title()
            supporting_info.append(f"Query complexity level: {complexity_text}")
        
        return supporting_info
    
    def _extract_standards_alignment(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract standards alignment from results."""
        
        all_standards = []
        
        for result in results:
            metadata = result.get("metadata", {})
            standards = metadata.get("standards", [])
            if isinstance(standards, str):
                standards = [standards]
            all_standards.extend(standards)
        
        # Remove duplicates and return top standards
        unique_standards = list(set(all_standards))
        return unique_standards[:5]
    
    async def _generate_follow_ups(self, context: QueryContext, results: List[Dict[str, Any]]) -> List[str]:
        """Generate follow-up questions and suggestions."""
        
        follow_ups = []
        
        # Based on intent
        if context.intent == QueryIntent.EXPLANATION:
            follow_ups.extend([
                "Would you like specific examples or applications?",
                "Are you interested in teaching strategies for this concept?",
                "Do you need assessment ideas for this topic?"
            ])
        
        elif context.intent == QueryIntent.CURRICULUM_SEARCH:
            follow_ups.extend([
                "Would you like lesson plan suggestions for this curriculum?",
                "Do you need alignment with other grade levels?",
                "Are you interested in assessment rubrics?"
            ])
        
        elif context.intent == QueryIntent.RESOURCE_LOOKUP:
            follow_ups.extend([
                "Would you like resources for different learning styles?",
                "Do you need materials for different grade levels?",
                "Are you interested in digital or printable resources?"
            ])
        
        # Based on subject areas
        if SubjectArea.MATHEMATICS in context.subject_areas:
            follow_ups.append("Would you like math manipulatives or visual aids suggestions?")
        
        if SubjectArea.SCIENCE in context.subject_areas:
            follow_ups.append("Are you interested in hands-on science experiments?")
        
        if SubjectArea.ROBOTICS in context.subject_areas:
            follow_ups.append("Would you like programming examples or hardware recommendations?")
        
        return follow_ups[:5]  # Limit to 5 follow-ups
    
    async def _find_related_resources(self, context: QueryContext, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find related resources based on context and results."""
        
        related = []
        
        # Extract topics from results
        result_topics = []
        for result in results:
            metadata = result.get("metadata", {})
            topics = metadata.get("topics", [])
            result_topics.extend(topics)
        
        # Find resources with similar topics
        if result_topics:
            # This could be enhanced with actual similarity search
            for topic in result_topics[:3]:
                related.append({
                    "title": f"Additional resources on {topic}",
                    "type": "topic_related",
                    "relevance": "high"
                })
        
        # Add standard related resources
        if context.subject_areas:
            for subject in context.subject_areas:
                subject_name = subject.value.replace('_', ' ').title()
                related.append({
                    "title": f"{subject_name} Teaching Resources",
                    "type": "subject_related",
                    "relevance": "medium"
                })
        
        return related[:5]  # Limit to 5 related resources
    
    def _calculate_confidence_score(self, context: QueryContext, results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for the response."""
        
        # Base confidence from query analysis
        base_confidence = context.confidence_score
        
        # Adjust based on number and quality of results
        if not results:
            return base_confidence * 0.3
        
        # More results generally increase confidence
        result_factor = min(1.0, len(results) / 5.0)
        
        # Check relevance of results
        relevance_scores = []
        for result in results:
            distance = result.get("distance", 1.0)
            relevance = 1.0 - distance
            relevance_scores.append(relevance)
        
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.5
        
        # Combine factors
        final_confidence = base_confidence * 0.4 + result_factor * 0.3 + avg_relevance * 0.3
        
        return min(1.0, final_confidence)
    
    def _calculate_completeness_score(self, context: QueryContext, results: List[Dict[str, Any]]) -> float:
        """Calculate completeness score for the response."""
        
        completeness_factors = []
        
        # Check if we have curriculum content (if requested)
        if context.intent in [QueryIntent.CURRICULUM_SEARCH, QueryIntent.STANDARDS_ALIGNMENT]:
            curriculum_results = [r for r in results if r.get("source_type") == "curriculum"]
            completeness_factors.append(1.0 if curriculum_results else 0.3)
        
        # Check if we have resource content (if requested)
        if context.intent in [QueryIntent.RESOURCE_LOOKUP, QueryIntent.LESSON_PLANNING]:
            resource_results = [r for r in results if r.get("source_type") == "resource"]
            completeness_factors.append(1.0 if resource_results else 0.3)
        
        # Check coverage of subject areas
        if context.subject_areas:
            subject_coverage = 0
            for subject in context.subject_areas:
                subject_name = subject.value
                for result in results:
                    metadata = result.get("metadata", {})
                    result_subjects = metadata.get("subject_areas", [])
                    if subject_name in result_subjects:
                        subject_coverage += 1
                        break
            
            coverage_ratio = subject_coverage / len(context.subject_areas)
            completeness_factors.append(coverage_ratio)
        
        # Default factors
        if not completeness_factors:
            completeness_factors = [0.7]  # Moderate completeness as default
        
        return sum(completeness_factors) / len(completeness_factors)
    
    def _calculate_relevance_score(self, results: List[Dict[str, Any]]) -> float:
        """Calculate overall relevance score for results."""
        
        if not results:
            return 0.0
        
        relevance_scores = []
        for result in results:
            distance = result.get("distance", 1.0)
            relevance = 1.0 - distance
            relevance_scores.append(relevance)
        
        return sum(relevance_scores) / len(relevance_scores)
    
    def _format_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format source information for response."""
        
        sources = []
        
        for i, result in enumerate(results):
            metadata = result.get("metadata", {})
            
            source = {
                "source_id": f"source_{i+1}",
                "title": metadata.get("title", "Untitled Source"),
                "type": result.get("source_type", "unknown"),
                "relevance": 1.0 - result.get("distance", 1.0),
                "learning_level": result.get("learning_level", "unknown")
            }
            
            # Add additional metadata if available
            if "author" in metadata:
                source["author"] = metadata["author"]
            if "publication_date" in metadata:
                source["publication_date"] = metadata["publication_date"]
            if "subject_area" in metadata:
                source["subject_area"] = metadata["subject_area"]
            
            sources.append(source)
        
        return sources


# Example usage and testing
async def main():
    """Example usage of the query handler."""
    print("=== Query Handler Demo ===")
    
    # Initialize components
    from .rag_engine import RAGEngine
    from .curriculum_indexer import CurriculumIndexer
    from .resource_processor import ResourceProcessor
    
    rag = RAGEngine()
    curriculum_indexer = CurriculumIndexer(rag)
    resource_processor = ResourceProcessor(rag)
    
    # Initialize collections
    await curriculum_indexer.initialize_collections()
    await resource_processor.initialize_resource_collections()
    
    # Create query handler
    query_handler = QueryHandler(rag, curriculum_indexer, resource_processor)
    
    # Test queries
    test_queries = [
        "What are the learning objectives for Grade 3 mathematics fractions?",
        "I need lesson plan resources for elementary robotics",
        "How do I assess student understanding of engineering design process?",
        "What NGSS standards align with middle school science projects?",
        "Find tutorial resources for advanced robotics competition preparation"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test Query {i} ---")
        print(f"Query: {query}")
        
        # Analyze query
        context = await query_handler.analyzer.analyze_query(query)
        print(f"Intent: {context.intent.value}")
        print(f"Complexity: {context.complexity.value}")
        print(f"Subject Areas: {[s.value for s in context.subject_areas]}")
        print(f"Learning Levels: {[l.value for l in context.learning_levels]}")
        
        # Handle full query (would need actual data for complete response)
        try:
            response = await query_handler.handle_query(query)
            print(f"Confidence Score: {response.confidence_score:.2f}")
            print(f"Sources Used: {response.total_sources}")
            print(f"Primary Answer: {response.primary_answer[:100]}...")
        except Exception as e:
            print(f"Full query handling failed (expected without data): {e}")
    
    print("\n=== Query Handler Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())