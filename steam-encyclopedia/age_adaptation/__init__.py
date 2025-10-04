"""
Age Adaptation Module
Comprehensive system for adapting STEAM content to different age groups and developmental stages
"""

from .age_adaptation_engine import AgeAdaptationEngine, AgeGroupProfile, CognitiveStage, LearningStyle
from .difficulty_analyzer import ContentDifficultyAnalyzer, DifficultyMetrics
from .learning_progression_mapper import (
    LearningProgressionMapper, ConceptNode, LearningProgression, 
    ProgressionType, MasteryLevel
)
from .adaptation_orchestrator import (
    AgeAdaptationOrchestrator, AdaptationRequest, AdaptationResult
)

__version__ = "1.0.0"
__author__ = "STEAM Encyclopedia Team"
__description__ = "Age-appropriate content adaptation system for STEAM education"

# Main classes for external use
__all__ = [
    # Core engines
    "AgeAdaptationEngine",
    "ContentDifficultyAnalyzer", 
    "LearningProgressionMapper",
    "AgeAdaptationOrchestrator",
    
    # Data models
    "AgeGroupProfile",
    "DifficultyMetrics",
    "ConceptNode", 
    "LearningProgression",
    "AdaptationRequest",
    "AdaptationResult",
    
    # Enums
    "CognitiveStage",
    "LearningStyle", 
    "ProgressionType",
    "MasteryLevel"
]


def create_age_adaptation_system():
    """
    Factory function to create a complete age adaptation system.
    
    Returns:
        AgeAdaptationOrchestrator: Fully configured orchestrator
    """
    return AgeAdaptationOrchestrator()


def get_age_recommendations(content_text: str, domain: str = "science"):
    """
    Quick utility function to get age group recommendations for content.
    
    Args:
        content_text: The content to analyze
        domain: Content domain (science, technology, engineering, mathematics, arts)
        
    Returns:
        List of recommended age groups
    """
    import asyncio
    from datetime import datetime
    from agents.base_agent import ContentItem, AgeGroup
    
    # Create temporary content item
    content = ContentItem(
        id="temp_analysis",
        title="Temporary Content",
        content=content_text,
        content_type="analysis",
        domain=domain,
        age_groups=[],
        sources=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        version=1
    )
    
    # Analyze and get recommendations
    analyzer = ContentDifficultyAnalyzer()
    
    async def analyze():
        difficulty = await analyzer.analyze_difficulty(content)
        return analyzer.recommend_age_groups(difficulty)
    
    return asyncio.run(analyze())


# Version info
def get_version_info():
    """Get version information for the age adaptation module."""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": {
            "age_adaptation_engine": "Content adaptation with age-specific transformations",
            "difficulty_analyzer": "Linguistic and cognitive difficulty analysis", 
            "learning_progression_mapper": "Learning pathways and prerequisite mapping",
            "adaptation_orchestrator": "Coordinated adaptation workflow management"
        },
        "features": [
            "Multi-dimensional difficulty analysis",
            "Age-appropriate vocabulary substitution", 
            "Sentence structure simplification",
            "Learning progression mapping",
            "Prerequisite identification",
            "Interactive element suggestions",
            "Safety content filtering",
            "Cognitive load optimization",
            "Personalized learning recommendations"
        ]
    }


# Example usage patterns
USAGE_EXAMPLES = {
    "basic_adaptation": """
# Basic content adaptation
from age_adaptation import create_age_adaptation_system
from agents.base_agent import ContentItem, AgeGroup

orchestrator = create_age_adaptation_system()

# Adapt content for multiple age groups
result = await orchestrator.adapt_content(AdaptationRequest(
    content=your_content_item,
    target_age_groups=[AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL]
))

# Access adapted content
elementary_content = result.adapted_contents[AgeGroup.ELEMENTARY]
middle_school_content = result.adapted_contents[AgeGroup.MIDDLE_SCHOOL]
""",
    
    "difficulty_analysis": """
# Analyze content difficulty
from age_adaptation import ContentDifficultyAnalyzer

analyzer = ContentDifficultyAnalyzer()
metrics = await analyzer.analyze_difficulty(content_item)

print(f"Reading level: {metrics.flesch_kincaid_grade}")
print(f"Difficulty: {analyzer.get_difficulty_level(metrics.overall_difficulty)}")
""",
    
    "learning_progression": """
# Work with learning progressions
from age_adaptation import LearningProgressionMapper

mapper = LearningProgressionMapper()

# Get learning path for a concept
path = mapper.get_learning_path("photosynthesis", AgeGroup.HIGH_SCHOOL)

# Check if student is ready for a concept
readiness = mapper.assess_readiness("calculus", mastered_concepts, AgeGroup.HIGH_SCHOOL)
""",
    
    "quick_recommendations": """
# Quick age group recommendations
from age_adaptation import get_age_recommendations

recommended_ages = get_age_recommendations(
    "Your content text here...",
    domain="science"
)
print(f"Recommended for: {[age.value for age in recommended_ages]}")
"""
}


def print_usage_examples():
    """Print usage examples for the age adaptation system."""
    print("=== Age Adaptation System Usage Examples ===\n")
    
    for example_name, example_code in USAGE_EXAMPLES.items():
        print(f"## {example_name.replace('_', ' ').title()}")
        print(example_code)
        print()


# Configuration defaults
DEFAULT_CONFIG = {
    "adaptation_engine": {
        "safety_filtering_enabled": True,
        "vocabulary_simplification_enabled": True,
        "sentence_restructuring_enabled": True,
        "interactive_elements_enabled": True,
        "max_content_length_multiplier": 1.5
    },
    "difficulty_analyzer": {
        "flesch_kincaid_weight": 0.3,
        "vocabulary_complexity_weight": 0.2,
        "concept_density_weight": 0.2,
        "sentence_complexity_weight": 0.15,
        "abstract_concept_weight": 0.15
    },
    "progression_mapper": {
        "prerequisite_strictness": "moderate",  # strict, moderate, lenient
        "mastery_threshold": 0.7,
        "recommendation_limit": 5
    },
    "orchestrator": {
        "max_concurrent_adaptations": 5,
        "timeout_seconds": 300,
        "quality_validation_enabled": True,
        "statistics_tracking_enabled": True
    }
}


def get_default_config():
    """Get default configuration for the age adaptation system."""
    return DEFAULT_CONFIG.copy()


# System status and health checks
async def system_health_check():
    """
    Perform a health check on the age adaptation system.
    
    Returns:
        Dict with health status information
    """
    from datetime import datetime
    
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "healthy",
        "components": {},
        "warnings": [],
        "errors": []
    }
    
    try:
        # Test orchestrator creation
        orchestrator = create_age_adaptation_system()
        health_status["components"]["orchestrator"] = "healthy"
        
        # Test basic functionality with sample content
        from agents.base_agent import ContentItem, AgeGroup
        
        sample_content = ContentItem(
            id="health_check",
            title="Test Content",
            content="This is a simple test sentence for health checking.",
            content_type="test",
            domain="science",
            age_groups=[AgeGroup.ELEMENTARY],
            sources=["health_check"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1
        )
        
        # Test difficulty analysis
        difficulty = await orchestrator.difficulty_analyzer.analyze_difficulty(sample_content)
        if difficulty.overall_difficulty >= 0:
            health_status["components"]["difficulty_analyzer"] = "healthy"
        else:
            health_status["components"]["difficulty_analyzer"] = "warning"
            health_status["warnings"].append("Difficulty analyzer returned invalid score")
        
        # Test adaptation engine
        profile = orchestrator.adaptation_engine.get_age_profile(AgeGroup.ELEMENTARY)
        if profile and profile.attention_span_minutes > 0:
            health_status["components"]["adaptation_engine"] = "healthy"
        else:
            health_status["components"]["adaptation_engine"] = "warning"
            health_status["warnings"].append("Adaptation engine profile incomplete")
        
        # Test progression mapper
        concepts = orchestrator.progression_mapper.concepts
        if len(concepts) > 0:
            health_status["components"]["progression_mapper"] = "healthy"
        else:
            health_status["components"]["progression_mapper"] = "warning"
            health_status["warnings"].append("Progression mapper has no concepts loaded")
            
    except Exception as e:
        health_status["overall_status"] = "error"
        health_status["errors"].append(f"System health check failed: {str(e)}")
        
        # Mark all components as unknown
        for component in ["orchestrator", "difficulty_analyzer", "adaptation_engine", "progression_mapper"]:
            health_status["components"][component] = "error"
    
    # Determine overall status
    component_statuses = list(health_status["components"].values())
    if "error" in component_statuses:
        health_status["overall_status"] = "error"
    elif "warning" in component_statuses:
        health_status["overall_status"] = "warning"
    
    return health_status


if __name__ == "__main__":
    # Demo the module
    import asyncio
    
    async def demo():
        print("=== Age Adaptation Module Demo ===")
        
        # Print version info
        version_info = get_version_info()
        print(f"\nVersion: {version_info['version']}")
        print(f"Description: {version_info['description']}")
        
        # Print features
        print(f"\nFeatures:")
        for feature in version_info['features']:
            print(f"  • {feature}")
        
        # Health check
        print(f"\n=== System Health Check ===")
        health = await system_health_check()
        print(f"Overall Status: {health['overall_status']}")
        
        for component, status in health['components'].items():
            print(f"  {component}: {status}")
        
        if health['warnings']:
            print(f"\nWarnings:")
            for warning in health['warnings']:
                print(f"  ⚠️  {warning}")
        
        if health['errors']:
            print(f"\nErrors:")
            for error in health['errors']:
                print(f"  ❌ {error}")
        
        # Quick recommendation demo
        print(f"\n=== Quick Recommendation Demo ===")
        sample_text = """
        Quantum mechanics is a fundamental theory in physics that describes the behavior
        of matter and energy at the atomic and subatomic scale. It introduces concepts
        like wave-particle duality, uncertainty principle, and quantum superposition.
        """
        
        try:
            recommendations = get_age_recommendations(sample_text, "science")
            print(f"Sample text recommended for: {[age.value for age in recommendations]}")
        except Exception as e:
            print(f"Recommendation demo failed: {e}")
        
        print(f"\n=== Usage Examples ===")
        print_usage_examples()
    
    asyncio.run(demo())