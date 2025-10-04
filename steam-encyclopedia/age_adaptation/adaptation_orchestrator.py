"""
Age Adaptation Orchestrator
Main orchestrator that coordinates all age adaptation components
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

from agents.base_agent import ContentItem, AgeGroup
from .age_adaptation_engine import AgeAdaptationEngine, AgeGroupProfile
from .difficulty_analyzer import ContentDifficultyAnalyzer, DifficultyMetrics
from .learning_progression_mapper import LearningProgressionMapper, ConceptNode, MasteryLevel


@dataclass
class AdaptationRequest:
    """Request for content adaptation."""
    content: ContentItem
    target_age_groups: List[AgeGroup]
    user_context: Optional[Dict[str, Any]] = None
    adaptation_preferences: Optional[Dict[str, Any]] = None
    priority_level: str = "normal"  # low, normal, high, urgent


@dataclass
class AdaptationResult:
    """Result of content adaptation process."""
    original_content: ContentItem
    adapted_contents: Dict[AgeGroup, ContentItem]
    difficulty_analysis: DifficultyMetrics
    appropriateness_scores: Dict[AgeGroup, Dict[str, float]]
    learning_recommendations: Dict[AgeGroup, Dict[str, Any]]
    adaptation_metadata: Dict[str, Any]
    processing_time: float
    success: bool
    errors: List[str] = None


class AgeAdaptationOrchestrator:
    """Main orchestrator for age adaptation system."""
    
    def __init__(self):
        self.adaptation_engine = AgeAdaptationEngine()
        self.difficulty_analyzer = ContentDifficultyAnalyzer()
        self.progression_mapper = LearningProgressionMapper()
        
        self.logger = logging.getLogger(__name__)
        self.stats = {
            "total_adaptations": 0,
            "successful_adaptations": 0,
            "failed_adaptations": 0,
            "average_processing_time": 0.0,
            "adaptations_by_age": {age: 0 for age in AgeGroup}
        }
    
    async def adapt_content(self, request: AdaptationRequest) -> AdaptationResult:
        """Main method to adapt content for target age groups."""
        start_time = datetime.now()
        errors = []
        adapted_contents = {}
        appropriateness_scores = {}
        learning_recommendations = {}
        
        try:
            # Step 1: Analyze original content difficulty
            self.logger.info(f"Analyzing difficulty for content: {request.content.id}")
            difficulty_analysis = await self.difficulty_analyzer.analyze_difficulty(request.content)
            
            # Step 2: Determine optimal age groups if not specified
            if not request.target_age_groups:
                recommended_ages = self.difficulty_analyzer.recommend_age_groups(difficulty_analysis)
                request.target_age_groups = recommended_ages
            
            # Step 3: Adapt content for each target age group
            for age_group in request.target_age_groups:
                try:
                    # Assess appropriateness
                    appropriateness = self.adaptation_engine.assess_content_appropriateness(
                        request.content, age_group
                    )
                    appropriateness_scores[age_group] = appropriateness
                    
                    # Adapt content
                    adapted_content = await self.adaptation_engine.adapt_content(
                        request.content, age_group
                    )
                    adapted_contents[age_group] = adapted_content
                    
                    # Generate learning recommendations
                    recommendations = await self._generate_learning_recommendations(
                        adapted_content, age_group, request.user_context
                    )
                    learning_recommendations[age_group] = recommendations
                    
                    self.stats["adaptations_by_age"][age_group] += 1
                    
                except Exception as e:
                    error_msg = f"Failed to adapt content for {age_group.value}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
            # Step 4: Generate adaptation metadata
            adaptation_metadata = await self._generate_adaptation_metadata(
                request, difficulty_analysis, appropriateness_scores
            )
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.stats["total_adaptations"] += 1
            
            success = len(adapted_contents) > 0
            if success:
                self.stats["successful_adaptations"] += 1
                self._update_average_processing_time(processing_time)
            else:
                self.stats["failed_adaptations"] += 1
            
            return AdaptationResult(
                original_content=request.content,
                adapted_contents=adapted_contents,
                difficulty_analysis=difficulty_analysis,
                appropriateness_scores=appropriateness_scores,
                learning_recommendations=learning_recommendations,
                adaptation_metadata=adaptation_metadata,
                processing_time=processing_time,
                success=success,
                errors=errors if errors else None
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.stats["total_adaptations"] += 1
            self.stats["failed_adaptations"] += 1
            
            error_msg = f"Critical error in adaptation process: {str(e)}"
            self.logger.error(error_msg)
            
            return AdaptationResult(
                original_content=request.content,
                adapted_contents={},
                difficulty_analysis=None,
                appropriateness_scores={},
                learning_recommendations={},
                adaptation_metadata={},
                processing_time=processing_time,
                success=False,
                errors=[error_msg]
            )
    
    async def batch_adapt_content(self, requests: List[AdaptationRequest]) -> List[AdaptationResult]:
        """Adapt multiple content items in batch."""
        self.logger.info(f"Starting batch adaptation of {len(requests)} items")
        
        # Sort requests by priority
        prioritized_requests = sorted(
            requests, 
            key=lambda r: {"urgent": 0, "high": 1, "normal": 2, "low": 3}.get(r.priority_level, 2)
        )
        
        # Process in parallel with concurrency limit
        semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent adaptations
        
        async def process_request(request):
            async with semaphore:
                return await self.adapt_content(request)
        
        results = await asyncio.gather(
            *[process_request(request) for request in prioritized_requests],
            return_exceptions=True
        )
        
        # Handle any exceptions that occurred
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = AdaptationResult(
                    original_content=prioritized_requests[i].content,
                    adapted_contents={},
                    difficulty_analysis=None,
                    appropriateness_scores={},
                    learning_recommendations={},
                    adaptation_metadata={},
                    processing_time=0.0,
                    success=False,
                    errors=[f"Exception during processing: {str(result)}"]
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _generate_learning_recommendations(
        self, 
        content: ContentItem, 
        age_group: AgeGroup, 
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate personalized learning recommendations."""
        profile = self.adaptation_engine.get_age_profile(age_group)
        
        recommendations = {
            "prerequisite_concepts": [],
            "follow_up_concepts": [],
            "related_activities": [],
            "assessment_suggestions": [],
            "learning_path": [],
            "estimated_learning_time": profile.attention_span_minutes
        }
        
        # Get prerequisite and follow-up concepts from progression mapper
        if content.related_concepts:
            mastered_concepts = user_context.get("mastered_concepts", []) if user_context else []
            
            for concept in content.related_concepts:
                # Check if this is a prerequisite
                prerequisites = self.progression_mapper.get_prerequisites(concept, age_group)
                if prerequisites:
                    recommendations["prerequisite_concepts"].extend(prerequisites)
                
                # Get suggestions for next concepts
                if concept in mastered_concepts:
                    next_concepts = self.progression_mapper.suggest_next_concepts(
                        mastered_concepts + [concept], age_group
                    )
                    recommendations["follow_up_concepts"].extend(next_concepts)
        
        # Generate activity recommendations based on learning styles
        recommendations["related_activities"] = self._generate_activity_recommendations(
            content, profile
        )
        
        # Generate assessment suggestions
        recommendations["assessment_suggestions"] = self._generate_assessment_suggestions(
            content, profile
        )
        
        # Create learning path
        if content.prerequisites:
            learning_path = []
            for prereq in content.prerequisites:
                path = self.progression_mapper.get_learning_path(prereq, age_group)
                learning_path.extend(path)
            
            recommendations["learning_path"] = list(dict.fromkeys(learning_path))  # Remove duplicates
        
        return recommendations
    
    def _generate_activity_recommendations(self, content: ContentItem, profile: AgeGroupProfile) -> List[str]:
        """Generate activity recommendations based on learning preferences."""
        activities = []
        
        # Activities based on preferred learning styles
        for learning_style in profile.preferred_learning_styles:
            if learning_style.value == "visual":
                activities.extend([
                    "Create a visual diagram or infographic",
                    "Draw or sketch key concepts",
                    "Use color coding for different ideas",
                    "Create a concept map"
                ])
            elif learning_style.value == "auditory":
                activities.extend([
                    "Discuss concepts with others",
                    "Listen to related podcasts or videos",
                    "Explain concepts out loud",
                    "Create songs or mnemonics"
                ])
            elif learning_style.value == "kinesthetic":
                activities.extend([
                    "Build physical models or demonstrations",
                    "Conduct hands-on experiments",
                    "Use manipulatives or tactile materials",
                    "Act out processes or concepts"
                ])
            elif learning_style.value == "reading_writing":
                activities.extend([
                    "Write summaries or explanations",
                    "Create lists and outlines",
                    "Research and read related materials",
                    "Keep a learning journal"
                ])
        
        # Domain-specific activities
        if content.domain == "science":
            activities.extend([
                "Design and conduct experiments",
                "Observe phenomena in nature",
                "Collect and analyze data",
                "Create scientific drawings"
            ])
        elif content.domain == "technology":
            activities.extend([
                "Build simple programs or apps",
                "Explore coding concepts",
                "Create digital presentations",
                "Design user interfaces"
            ])
        elif content.domain == "engineering":
            activities.extend([
                "Design and build prototypes",
                "Test different solutions",
                "Identify and solve problems",
                "Create technical drawings"
            ])
        elif content.domain == "mathematics":
            activities.extend([
                "Solve practice problems",
                "Create mathematical models",
                "Explore patterns and relationships",
                "Apply concepts to real-world situations"
            ])
        elif content.domain == "arts":
            activities.extend([
                "Create original artworks",
                "Experiment with different techniques",
                "Analyze existing artworks",
                "Express ideas through art"
            ])
        
        # Remove duplicates and limit to reasonable number
        unique_activities = list(dict.fromkeys(activities))
        return unique_activities[:8]  # Limit to 8 activities
    
    def _generate_assessment_suggestions(self, content: ContentItem, profile: AgeGroupProfile) -> List[str]:
        """Generate assessment suggestions appropriate for age group."""
        assessments = []
        
        # Age-appropriate assessment methods
        if profile.age_group == AgeGroup.EARLY_YEARS:
            assessments = [
                "Observe child's play and interactions",
                "Simple show-and-tell activities",
                "Picture identification tasks",
                "Basic demonstration of concepts"
            ]
        elif profile.age_group == AgeGroup.ELEMENTARY:
            assessments = [
                "Short quizzes with pictures",
                "Hands-on demonstrations",
                "Simple project presentations",
                "Peer teaching activities",
                "Drawing or modeling concepts"
            ]
        elif profile.age_group == AgeGroup.MIDDLE_SCHOOL:
            assessments = [
                "Written explanations",
                "Lab report completion",
                "Group project presentations",
                "Problem-solving challenges",
                "Concept mapping exercises"
            ]
        elif profile.age_group == AgeGroup.HIGH_SCHOOL:
            assessments = [
                "Research project completion",
                "Analytical essays",
                "Peer review activities",
                "Independent investigations",
                "Presentation to younger students"
            ]
        elif profile.age_group == AgeGroup.HIGHER_ED:
            assessments = [
                "Critical analysis papers",
                "Independent research projects",
                "Peer-reviewed presentations",
                "Professional portfolio development",
                "Publication or conference submission"
            ]
        
        return assessments
    
    async def _generate_adaptation_metadata(
        self, 
        request: AdaptationRequest,
        difficulty_analysis: DifficultyMetrics,
        appropriateness_scores: Dict[AgeGroup, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Generate metadata about the adaptation process."""
        
        metadata = {
            "original_content_id": request.content.id,
            "adaptation_timestamp": datetime.now().isoformat(),
            "target_age_groups": [age.value for age in request.target_age_groups],
            "original_difficulty": {
                "overall_score": difficulty_analysis.overall_difficulty if difficulty_analysis else 0,
                "reading_level": difficulty_analysis.flesch_kincaid_grade if difficulty_analysis else 0,
                "vocabulary_complexity": difficulty_analysis.academic_word_percentage if difficulty_analysis else 0
            },
            "adaptation_strategies_used": [],
            "quality_metrics": {},
            "recommendations": {
                "optimal_age_groups": [],
                "prerequisite_content": [],
                "follow_up_content": []
            }
        }
        
        # Analyze adaptation strategies used
        if difficulty_analysis:
            if difficulty_analysis.average_sentence_length > 20:
                metadata["adaptation_strategies_used"].append("sentence_shortening")
            if difficulty_analysis.academic_word_percentage > 15:
                metadata["adaptation_strategies_used"].append("vocabulary_simplification")
            if difficulty_analysis.abstract_concept_ratio > 20:
                metadata["adaptation_strategies_used"].append("concrete_examples_added")
            if difficulty_analysis.example_ratio < 10:
                metadata["adaptation_strategies_used"].append("more_examples_added")
        
        # Calculate quality metrics
        if appropriateness_scores:
            all_scores = []
            for age_scores in appropriateness_scores.values():
                all_scores.extend(age_scores.values())
            
            if all_scores:
                metadata["quality_metrics"] = {
                    "average_appropriateness": sum(all_scores) / len(all_scores),
                    "min_appropriateness": min(all_scores),
                    "max_appropriateness": max(all_scores),
                    "consistency_score": 1.0 - (max(all_scores) - min(all_scores))  # Higher = more consistent
                }
        
        # Generate recommendations
        if difficulty_analysis:
            recommended_ages = self.difficulty_analyzer.recommend_age_groups(difficulty_analysis)
            metadata["recommendations"]["optimal_age_groups"] = [age.value for age in recommended_ages]
        
        return metadata
    
    def _update_average_processing_time(self, new_time: float):
        """Update running average of processing time."""
        current_avg = self.stats["average_processing_time"]
        successful_count = self.stats["successful_adaptations"]
        
        if successful_count == 1:
            self.stats["average_processing_time"] = new_time
        else:
            # Running average formula
            self.stats["average_processing_time"] = (
                (current_avg * (successful_count - 1) + new_time) / successful_count
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        success_rate = 0.0
        if self.stats["total_adaptations"] > 0:
            success_rate = self.stats["successful_adaptations"] / self.stats["total_adaptations"]
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "failure_rate": 1.0 - success_rate
        }
    
    def reset_statistics(self):
        """Reset system statistics."""
        self.stats = {
            "total_adaptations": 0,
            "successful_adaptations": 0,
            "failed_adaptations": 0,
            "average_processing_time": 0.0,
            "adaptations_by_age": {age: 0 for age in AgeGroup}
        }
    
    async def validate_adaptation_quality(self, result: AdaptationResult) -> Dict[str, float]:
        """Validate the quality of adaptation results."""
        quality_scores = {}
        
        for age_group, adapted_content in result.adapted_contents.items():
            # Re-analyze adapted content
            adapted_difficulty = await self.difficulty_analyzer.analyze_difficulty(adapted_content)
            
            # Calculate quality metrics
            profile = self.adaptation_engine.get_age_profile(age_group)
            
            # Length appropriateness
            word_count = len(adapted_content.content.split())
            min_words, max_words = profile.content_length_words
            length_score = 1.0 if min_words <= word_count <= max_words else 0.5
            
            # Reading level appropriateness
            target_grade = {
                AgeGroup.EARLY_YEARS: 2,
                AgeGroup.ELEMENTARY: 5,
                AgeGroup.MIDDLE_SCHOOL: 8,
                AgeGroup.HIGH_SCHOOL: 12,
                AgeGroup.HIGHER_ED: 16
            }.get(age_group, 12)
            
            grade_diff = abs(adapted_difficulty.flesch_kincaid_grade - target_grade)
            reading_score = max(0.0, 1.0 - (grade_diff / 5.0))
            
            # Vocabulary appropriateness
            vocab_score = 1.0 - min(1.0, adapted_difficulty.academic_word_percentage / 20.0)
            
            # Overall quality score
            overall_quality = (length_score + reading_score + vocab_score) / 3.0
            
            quality_scores[age_group.value] = {
                "length_appropriateness": length_score,
                "reading_level_appropriateness": reading_score,
                "vocabulary_appropriateness": vocab_score,
                "overall_quality": overall_quality
            }
        
        return quality_scores
    
    async def get_adaptation_recommendations(self, content: ContentItem) -> Dict[str, Any]:
        """Get recommendations for how to adapt content."""
        # Analyze content first
        difficulty_analysis = await self.difficulty_analyzer.analyze_difficulty(content)
        
        recommendations = {
            "suggested_age_groups": [],
            "adaptation_strategies": [],
            "estimated_effort": "low",
            "potential_challenges": [],
            "success_probability": 0.8
        }
        
        # Suggest appropriate age groups
        recommended_ages = self.difficulty_analyzer.recommend_age_groups(difficulty_analysis)
        recommendations["suggested_age_groups"] = [age.value for age in recommended_ages]
        
        # Suggest adaptation strategies
        if difficulty_analysis.flesch_kincaid_grade > 12:
            recommendations["adaptation_strategies"].append("Simplify sentence structure")
            recommendations["estimated_effort"] = "high"
        
        if difficulty_analysis.academic_word_percentage > 20:
            recommendations["adaptation_strategies"].append("Replace academic vocabulary")
            recommendations["estimated_effort"] = "medium"
        
        if difficulty_analysis.abstract_concept_ratio > 30:
            recommendations["adaptation_strategies"].append("Add concrete examples")
            recommendations["potential_challenges"].append("Maintaining conceptual accuracy")
        
        if difficulty_analysis.example_ratio < 5:
            recommendations["adaptation_strategies"].append("Add more examples and illustrations")
        
        # Estimate success probability based on content characteristics
        if difficulty_analysis.overall_difficulty > 80:
            recommendations["success_probability"] = 0.6
            recommendations["potential_challenges"].append("Very high complexity")
        elif difficulty_analysis.overall_difficulty > 60:
            recommendations["success_probability"] = 0.7
        
        if len(content.content.split()) > 2000:
            recommendations["potential_challenges"].append("Very long content")
            recommendations["estimated_effort"] = "high"
        
        return recommendations


# Example usage and testing
async def main():
    """Example usage of the age adaptation orchestrator."""
    orchestrator = AgeAdaptationOrchestrator()
    
    # Sample content
    sample_content = ContentItem(
        id="sample_orchestrator_001",
        title="Advanced Photosynthesis Mechanisms",
        content="""
        Photosynthesis is a sophisticated biological process involving complex biochemical pathways.
        The light-dependent reactions occur in the thylakoid membranes, where photosystem II and
        photosystem I work in tandem to generate ATP and NADPH through the electron transport chain.
        Subsequently, the Calvin cycle utilizes these energy-rich molecules in the stroma to fix
        carbon dioxide into glucose through a series of enzymatic reactions involving RuBisCO
        and other critical enzymes.
        """,
        content_type="explanation",
        domain="science",
        age_groups=[AgeGroup.HIGHER_ED],
        sources=["advanced_biology_textbook"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        version=1,
        tags=["photosynthesis", "biochemistry", "cellular_biology"],
        prerequisites=["cell_structure", "chemistry_basics", "energy_concepts"],
        related_concepts=["cellular_respiration", "chloroplast_structure", "enzyme_function"]
    )
    
    # Create adaptation request
    request = AdaptationRequest(
        content=sample_content,
        target_age_groups=[AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL],
        user_context={"mastered_concepts": ["observation", "plants", "energy"]},
        priority_level="normal"
    )
    
    print("=== Age Adaptation Orchestrator Demo ===")
    
    # Get adaptation recommendations
    recommendations = await orchestrator.get_adaptation_recommendations(sample_content)
    print(f"\nAdaptation Recommendations:")
    print(f"- Suggested age groups: {recommendations['suggested_age_groups']}")
    print(f"- Adaptation strategies: {recommendations['adaptation_strategies']}")
    print(f"- Estimated effort: {recommendations['estimated_effort']}")
    print(f"- Success probability: {recommendations['success_probability']}")
    
    # Perform adaptation
    print(f"\nStarting adaptation process...")
    result = await orchestrator.adapt_content(request)
    
    print(f"\nAdaptation Results:")
    print(f"- Success: {result.success}")
    print(f"- Processing time: {result.processing_time:.2f} seconds")
    print(f"- Adapted for {len(result.adapted_contents)} age groups")
    
    if result.success:
        for age_group, adapted_content in result.adapted_contents.items():
            print(f"\n--- {age_group.value} ---")
            print(f"Title: {adapted_content.title}")
            print(f"Content length: {len(adapted_content.content.split())} words")
            print(f"Sample: {adapted_content.content[:100]}...")
    
    if result.errors:
        print(f"\nErrors: {result.errors}")
    
    # Get system statistics
    stats = orchestrator.get_statistics()
    print(f"\nSystem Statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())