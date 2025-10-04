"""
STEAM Project Generator System

AI-powered system to generate comprehensive STEAM projects with specific topics,
modules, and learning outcomes based on educational frameworks, learner profiles,
and real-world relevance.
"""

import json
import uuid
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from datetime import datetime, timedelta

# Import our educational framework components
from learning_instance_manager import (
    LearnerProfile, STEAMProject, LearningOutcome, EducationalFramework,
    DifficultyLevel, LearningStyle, MultipleIntelligence
)

class ProjectTheme(Enum):
    ENVIRONMENTAL_SUSTAINABILITY = "Environmental Sustainability"
    SPACE_EXPLORATION = "Space Exploration"
    SMART_CITIES = "Smart Cities"
    RENEWABLE_ENERGY = "Renewable Energy"
    OCEAN_CONSERVATION = "Ocean Conservation"
    BIOTECHNOLOGY = "Biotechnology Innovation"
    ARTIFICIAL_INTELLIGENCE = "Artificial Intelligence"
    ROBOTICS_AUTOMATION = "Robotics and Automation"
    DIGITAL_ARTS_MEDIA = "Digital Arts and Media"
    MATHEMATICAL_MODELING = "Mathematical Modeling"
    HEALTHCARE_INNOVATION = "Healthcare Innovation"
    FOOD_SECURITY = "Global Food Security"
    CLIMATE_SCIENCE = "Climate Science and Adaptation"
    TRANSPORTATION_FUTURE = "Future of Transportation"
    CYBERSECURITY = "Cybersecurity and Digital Privacy"

class ProjectType(Enum):
    INVESTIGATION = "scientific_investigation"
    DESIGN_CHALLENGE = "engineering_design"
    CREATIVE_PROJECT = "artistic_creation"
    DATA_ANALYSIS = "data_science"
    INVENTION = "innovation_project"
    SOCIAL_IMPACT = "community_solution"
    RESEARCH = "scholarly_research"

@dataclass
class ProjectTemplate:
    """Template for generating customized STEAM projects"""
    theme: ProjectTheme
    project_type: ProjectType
    base_title: str
    description_template: str
    essential_questions: List[str]
    steam_integrations: Dict[str, List[str]]
    learning_outcomes_templates: List[Dict[str, Any]]
    assessment_strategies: List[str]
    materials_base: List[str]
    duration_range: Tuple[int, int]  # min, max hours
    difficulty_adaptations: Dict[DifficultyLevel, Dict[str, Any]]
    age_adaptations: Dict[str, Dict[str, Any]]  # age ranges
    framework_alignments: Dict[EducationalFramework, List[str]]

class STEAMProjectGenerator:
    """
    Advanced AI-powered project generator that creates personalized
    STEAM learning experiences aligned with multiple educational frameworks.
    """
    
    def __init__(self):
        self.project_templates = self._initialize_project_templates()
        self.real_world_contexts = self._load_real_world_contexts()
        self.framework_standards = self._load_framework_standards()
        self.robotics_integrations = self._load_robotics_integrations()
        self.coding_progressions = self._load_coding_progressions()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('STEAMProjectGenerator')
    
    def generate_personalized_project(self,
                                    learner_profile: LearnerProfile,
                                    theme: Optional[ProjectTheme] = None,
                                    frameworks: List[EducationalFramework] = None,
                                    difficulty_override: Optional[DifficultyLevel] = None,
                                    duration_preference: Optional[int] = None,
                                    include_robotics: bool = True,
                                    include_coding: bool = True,
                                    real_world_connection: bool = True) -> STEAMProject:
        """
        Generate a fully personalized STEAM project based on learner profile
        and educational requirements.
        """
        
        # Select appropriate theme
        if not theme:
            theme = self._select_optimal_theme(learner_profile)
        
        # Determine frameworks if not specified
        if not frameworks:
            frameworks = self._recommend_frameworks(learner_profile, theme)
        
        # Select project template
        template = self._select_project_template(theme, learner_profile)
        
        # Generate project specification
        project_spec = self._generate_project_specification(
            template, learner_profile, frameworks, difficulty_override,
            duration_preference, include_robotics, include_coding, real_world_connection
        )
        
        # Create comprehensive learning outcomes
        learning_outcomes = self._generate_learning_outcomes(
            project_spec, frameworks, learner_profile
        )
        
        # Generate STEAM integration components
        steam_components = self._generate_steam_components(
            project_spec, learner_profile, template
        )
        
        # Add robotics integration
        robotics_components = []
        if include_robotics and learner_profile.age >= 8:
            robotics_components = self._generate_robotics_integration(
                project_spec, learner_profile
            )
        
        # Add coding elements
        coding_elements = []
        if include_coding and learner_profile.age >= 10:
            coding_elements = self._generate_coding_integration(
                project_spec, learner_profile
            )
        
        # Generate assessment rubric
        assessment_rubric = self._generate_comprehensive_rubric(
            learning_outcomes, learner_profile, frameworks
        )
        
        # Add real-world connections
        if real_world_connection:
            project_spec = self._enhance_real_world_connections(
                project_spec, theme, learner_profile
            )
        
        # Create final project
        project = STEAMProject(
            project_id=str(uuid.uuid4()),
            title=project_spec['title'],
            description=project_spec['description'],
            theme=theme.value,
            learning_outcomes=learning_outcomes,
            steam_components=steam_components,
            frameworks=frameworks,
            difficulty_level=project_spec['difficulty_level'],
            estimated_duration_hours=project_spec['duration'],
            robotics_components=robotics_components,
            coding_elements=coding_elements,
            required_materials=project_spec['materials'],
            prerequisites=project_spec['prerequisites'],
            extensions=project_spec['extensions'],
            assessment_rubric=assessment_rubric
        )
        
        self.logger.info(f"Generated personalized project: {project.title} for learner {learner_profile.name}")
        
        return project
    
    def _initialize_project_templates(self) -> Dict[ProjectTheme, List[ProjectTemplate]]:
        """Initialize comprehensive project templates for all themes"""
        
        templates = {}
        
        # Environmental Sustainability Templates
        templates[ProjectTheme.ENVIRONMENTAL_SUSTAINABILITY] = [
            ProjectTemplate(
                theme=ProjectTheme.ENVIRONMENTAL_SUSTAINABILITY,
                project_type=ProjectType.INVESTIGATION,
                base_title="Eco-Detective: Local Environmental Investigation",
                description_template="Investigate environmental challenges in your community and design data-driven solutions that combine scientific inquiry, technological tools, engineering design, creative communication, and mathematical analysis.",
                essential_questions=[
                    "How do human activities impact local ecosystems?",
                    "What data do we need to understand environmental problems?",
                    "How can we design solutions that are both effective and sustainable?",
                    "What role does community engagement play in environmental solutions?"
                ],
                steam_integrations={
                    'Science': ['Environmental monitoring', 'Ecosystem analysis', 'Chemical testing', 'Biodiversity assessment'],
                    'Technology': ['Data collection sensors', 'GIS mapping', 'Environmental modeling software', 'Mobile apps for data tracking'],
                    'Engineering': ['Pollution control systems', 'Renewable energy devices', 'Water filtration design', 'Sustainable architecture'],
                    'Arts': ['Environmental awareness campaigns', 'Data visualization', 'Documentary creation', 'Community presentations'],
                    'Mathematics': ['Statistical analysis', 'Trend identification', 'Cost-benefit calculations', 'Predictive modeling']
                },
                learning_outcomes_templates=[
                    {
                        'description': 'Conduct scientific investigations using environmental monitoring techniques',
                        'framework': EducationalFramework.NGSS,
                        'cognitive_level': 'Analyze'
                    },
                    {
                        'description': 'Use digital tools to collect, analyze, and visualize environmental data',
                        'framework': EducationalFramework.ISTE,
                        'cognitive_level': 'Apply'
                    }
                ],
                assessment_strategies=['Portfolio assessment', 'Peer review', 'Community presentation', 'Data analysis report'],
                materials_base=['pH testing kit', 'Digital thermometer', 'Camera/smartphone', 'Computer/tablet', 'Graph paper'],
                duration_range=(15, 25),
                difficulty_adaptations={
                    DifficultyLevel.BEGINNER: {
                        'focus': 'Simple observations and measurements',
                        'support': 'Guided data collection sheets',
                        'complexity': 'Single environmental factor'
                    },
                    DifficultyLevel.INTERMEDIATE: {
                        'focus': 'Multi-factor analysis and basic solutions',
                        'support': 'Semi-structured investigation guides',
                        'complexity': 'Multiple interacting factors'
                    },
                    DifficultyLevel.ADVANCED: {
                        'focus': 'Comprehensive system analysis and innovation',
                        'support': 'Independent research methodology',
                        'complexity': 'Complex environmental systems'
                    }
                },
                age_adaptations={
                    '8-12': {'vocabulary': 'elementary', 'duration': 'shorter', 'collaboration': 'high'},
                    '13-16': {'vocabulary': 'intermediate', 'duration': 'standard', 'collaboration': 'balanced'},
                    '17+': {'vocabulary': 'advanced', 'duration': 'extended', 'collaboration': 'independent'}
                },
                framework_alignments={
                    EducationalFramework.NGSS: ['5-ESS3-1', 'MS-ESS3-3', 'HS-ESS3-2'],
                    EducationalFramework.ISTE: ['1.1.1', '1.3.1', '1.6.1'],
                    EducationalFramework.OECD: ['Critical thinking', 'Systems thinking', 'Creativity']
                }
            ),
            ProjectTemplate(
                theme=ProjectTheme.ENVIRONMENTAL_SUSTAINABILITY,
                project_type=ProjectType.DESIGN_CHALLENGE,
                base_title="Green Innovation Lab: Sustainable Solutions Design",
                description_template="Design and prototype innovative solutions to environmental challenges using engineering design principles, sustainable materials, and creative problem-solving approaches.",
                essential_questions=[
                    "How can we design products that minimize environmental impact?",
                    "What makes a solution truly sustainable?",
                    "How do we balance human needs with environmental protection?",
                    "What role does innovation play in sustainability?"
                ],
                steam_integrations={
                    'Science': ['Materials science', 'Energy efficiency', 'Life cycle analysis', 'Environmental chemistry'],
                    'Technology': ['CAD design software', '3D printing', 'Renewable energy systems', 'Smart sensors'],
                    'Engineering': ['Design thinking process', 'Prototyping', 'Systems optimization', 'Sustainable engineering'],
                    'Arts': ['Product design aesthetics', 'User experience design', 'Marketing materials', 'Public awareness campaigns'],
                    'Mathematics': ['Efficiency calculations', 'Cost analysis', 'Optimization algorithms', 'Statistical validation']
                },
                learning_outcomes_templates=[
                    {
                        'description': 'Apply engineering design process to develop sustainable solutions',
                        'framework': EducationalFramework.NGSS,
                        'cognitive_level': 'Create'
                    }
                ],
                assessment_strategies=['Design portfolio', 'Prototype testing', 'Pitch presentation', 'Peer feedback'],
                materials_base=['Recycled materials', 'Basic tools', '3D printer access', 'Design software', 'Testing equipment'],
                duration_range=(20, 35),
                difficulty_adaptations={
                    DifficultyLevel.BEGINNER: {
                        'focus': 'Simple product improvements',
                        'support': 'Design templates and guides',
                        'complexity': 'Single function products'
                    },
                    DifficultyLevel.INTERMEDIATE: {
                        'focus': 'Multi-functional sustainable designs',
                        'support': 'Design process scaffolding',
                        'complexity': 'Integrated system solutions'
                    },
                    DifficultyLevel.ADVANCED: {
                        'focus': 'Innovative sustainable technologies',
                        'support': 'Independent research and development',
                        'complexity': 'Market-ready solutions'
                    }
                },
                age_adaptations={
                    '8-12': {'materials': 'safe, simple', 'tools': 'basic', 'concepts': 'concrete'},
                    '13-16': {'materials': 'varied', 'tools': 'intermediate', 'concepts': 'abstract'},
                    '17+': {'materials': 'professional', 'tools': 'advanced', 'concepts': 'theoretical'}
                },
                framework_alignments={
                    EducationalFramework.NGSS: ['3-5-ETS1-1', 'MS-ETS1-2', 'HS-ETS1-3'],
                    EducationalFramework.ISTE: ['1.4.1', '1.5.1', '1.7.1'],
                    EducationalFramework.PBL: ['Authentic assessment', 'Real-world connections', 'Student choice']
                }
            )
        ]
        
        # Space Exploration Templates
        templates[ProjectTheme.SPACE_EXPLORATION] = [
            ProjectTemplate(
                theme=ProjectTheme.SPACE_EXPLORATION,
                project_type=ProjectType.DESIGN_CHALLENGE,
                base_title="Mission to Mars: Engineering Space Solutions",
                description_template="Design and test solutions for space exploration challenges, combining physics principles, engineering design, technology integration, creative problem-solving, and mathematical modeling.",
                essential_questions=[
                    "What are the unique challenges of space exploration?",
                    "How do we design systems that work in extreme environments?",
                    "What role does robotics play in space exploration?",
                    "How do we ensure crew safety during long-duration missions?"
                ],
                steam_integrations={
                    'Science': ['Physics of space', 'Astronomy', 'Materials science', 'Life support systems'],
                    'Technology': ['Robotics programming', 'Communication systems', 'Navigation software', 'Simulation tools'],
                    'Engineering': ['Aerospace engineering', 'Systems design', 'Mission planning', 'Risk assessment'],
                    'Arts': ['Mission patch design', 'Technical illustration', 'Public engagement materials', 'Documentary creation'],
                    'Mathematics': ['Orbital mechanics', 'Trajectory calculations', 'Resource optimization', 'Statistical analysis']
                },
                learning_outcomes_templates=[
                    {
                        'description': 'Apply physics principles to solve space exploration challenges',
                        'framework': EducationalFramework.NGSS,
                        'cognitive_level': 'Apply'
                    }
                ],
                assessment_strategies=['Mission simulation', 'Design defense', 'Technical documentation', 'Team presentation'],
                materials_base=['Robotics kit', 'Building materials', 'Computer/tablet', 'Mission simulation software', 'Testing apparatus'],
                duration_range=(25, 40),
                difficulty_adaptations={
                    DifficultyLevel.BEGINNER: {
                        'focus': 'Simple rover design and basic mission concepts',
                        'support': 'Step-by-step building guides',
                        'complexity': 'Single mission objective'
                    },
                    DifficultyLevel.INTERMEDIATE: {
                        'focus': 'Multi-system integration and mission planning',
                        'support': 'Design frameworks and checklists',
                        'complexity': 'Multiple interdependent systems'
                    },
                    DifficultyLevel.ADVANCED: {
                        'focus': 'Comprehensive mission architecture and innovation',
                        'support': 'Research methodology and peer review',
                        'complexity': 'Complete mission lifecycle'
                    }
                },
                age_adaptations={
                    '8-12': {'focus': 'rovers and basic exploration', 'math': 'basic calculations', 'science': 'observable phenomena'},
                    '13-16': {'focus': 'mission systems and planning', 'math': 'intermediate calculations', 'science': 'physics principles'},
                    '17+': {'focus': 'advanced engineering and research', 'math': 'advanced modeling', 'science': 'complex systems'}
                },
                framework_alignments={
                    EducationalFramework.NGSS: ['5-ESS1-2', 'MS-ETS1-4', 'HS-PS2-1'],
                    EducationalFramework.ISTE: ['1.4.1', '1.5.1', '1.6.1'],
                    EducationalFramework.OECD: ['Systems thinking', 'Innovation', 'Critical thinking']
                }
            )
        ]
        
        # Add templates for other themes...
        templates[ProjectTheme.SMART_CITIES] = self._create_smart_cities_templates()
        templates[ProjectTheme.ROBOTICS_AUTOMATION] = self._create_robotics_templates()
        templates[ProjectTheme.ARTIFICIAL_INTELLIGENCE] = self._create_ai_templates()
        
        return templates
    
    def _create_smart_cities_templates(self) -> List[ProjectTemplate]:
        """Create Smart Cities project templates"""
        return [
            ProjectTemplate(
                theme=ProjectTheme.SMART_CITIES,
                project_type=ProjectType.DESIGN_CHALLENGE,
                base_title="Future City Architect: Smart Urban Solutions",
                description_template="Design intelligent urban systems that improve quality of life while addressing sustainability, efficiency, and equity challenges through integrated STEAM approaches.",
                essential_questions=[
                    "How can technology improve urban living?",
                    "What makes a city truly 'smart' and sustainable?",
                    "How do we balance efficiency with human needs?",
                    "What role does data play in urban planning?"
                ],
                steam_integrations={
                    'Science': ['Urban ecology', 'Environmental monitoring', 'Energy systems', 'Transportation physics'],
                    'Technology': ['IoT sensors', 'Data analytics', 'Smart grid systems', 'Mobile applications'],
                    'Engineering': ['Urban planning', 'Infrastructure design', 'Systems integration', 'Optimization'],
                    'Arts': ['Urban design aesthetics', 'User interface design', 'Community engagement', 'Public art integration'],
                    'Mathematics': ['Traffic flow modeling', 'Resource optimization', 'Population dynamics', 'Economic analysis']
                },
                learning_outcomes_templates=[
                    {
                        'description': 'Design integrated urban systems using systems thinking principles',
                        'framework': EducationalFramework.OECD,
                        'cognitive_level': 'Create'
                    }
                ],
                assessment_strategies=['City model presentation', 'Data analysis report', 'Stakeholder feedback', 'Sustainability assessment'],
                materials_base=['Building materials', 'Sensors and electronics', 'Computer/tablet', 'Design software', 'Data collection tools'],
                duration_range=(20, 30),
                difficulty_adaptations={
                    DifficultyLevel.BEGINNER: {
                        'focus': 'Single smart system (traffic, lighting)',
                        'support': 'Template-based design',
                        'complexity': 'Linear cause-effect relationships'
                    },
                    DifficultyLevel.INTERMEDIATE: {
                        'focus': 'Integrated neighborhood systems',
                        'support': 'Guided system analysis',
                        'complexity': 'Multiple interacting systems'
                    },
                    DifficultyLevel.ADVANCED: {
                        'focus': 'City-wide integrated infrastructure',
                        'support': 'Independent research and innovation',
                        'complexity': 'Complex adaptive systems'
                    }
                },
                age_adaptations={
                    '8-12': {'scope': 'neighborhood', 'technology': 'simple sensors', 'presentation': 'visual models'},
                    '13-16': {'scope': 'district', 'technology': 'programmable systems', 'presentation': 'digital simulations'},
                    '17+': {'scope': 'city-wide', 'technology': 'advanced analytics', 'presentation': 'professional proposals'}
                },
                framework_alignments={
                    EducationalFramework.ISTE: ['1.1.1', '1.4.1', '1.7.1'],
                    EducationalFramework.DIGICOMP: ['Information literacy', 'Digital content creation', 'Problem solving'],
                    EducationalFramework.OECD: ['Systems thinking', 'Anticipation', 'Normative competency']
                }
            )
        ]
    
    def _create_robotics_templates(self) -> List[ProjectTemplate]:
        """Create Robotics and Automation project templates"""
        return [
            ProjectTemplate(
                theme=ProjectTheme.ROBOTICS_AUTOMATION,
                project_type=ProjectType.INVENTION,
                base_title="Robotics Innovation Lab: Intelligent Automation Solutions",
                description_template="Design, build, and program robotic systems that solve real-world problems through intelligent automation, combining mechanical design, programming, sensor integration, and human-robot interaction principles.",
                essential_questions=[
                    "How can robots enhance human capabilities?",
                    "What makes a robot truly intelligent and useful?",
                    "How do we design robots that are safe and ethical?",
                    "What is the future of human-robot collaboration?"
                ],
                steam_integrations={
                    'Science': ['Physics of motion', 'Sensor technology', 'Materials science', 'Cognitive science'],
                    'Technology': ['Programming languages', 'Computer vision', 'Machine learning', 'Wireless communication'],
                    'Engineering': ['Mechanical design', 'Control systems', 'Electrical circuits', 'System integration'],
                    'Arts': ['Robot aesthetics', 'User interface design', 'Animation and movement', 'Storytelling through robotics'],
                    'Mathematics': ['Kinematics', 'Control algorithms', 'Statistical analysis', 'Optimization']
                },
                learning_outcomes_templates=[
                    {
                        'description': 'Design and program autonomous robotic systems',
                        'framework': EducationalFramework.ISTE,
                        'cognitive_level': 'Create'
                    }
                ],
                assessment_strategies=['Robot demonstration', 'Code portfolio', 'Design documentation', 'Problem-solving showcase'],
                materials_base=['Modi robotics kit', 'Additional sensors', 'Computer/tablet', 'Building materials', 'Programming environment'],
                duration_range=(30, 50),
                difficulty_adaptations={
                    DifficultyLevel.BEGINNER: {
                        'focus': 'Basic robot behaviors and simple tasks',
                        'support': 'Visual programming blocks',
                        'complexity': 'Single-purpose robots'
                    },
                    DifficultyLevel.INTERMEDIATE: {
                        'focus': 'Multi-sensor integration and adaptive behaviors',
                        'support': 'Structured programming tutorials',
                        'complexity': 'Multi-functional robots'
                    },
                    DifficultyLevel.ADVANCED: {
                        'focus': 'AI integration and complex autonomous systems',
                        'support': 'Advanced programming resources',
                        'complexity': 'Intelligent, learning robots'
                    }
                },
                age_adaptations={
                    '8-12': {'programming': 'block-based', 'projects': 'fun and engaging', 'complexity': 'simple behaviors'},
                    '13-16': {'programming': 'hybrid block/text', 'projects': 'practical applications', 'complexity': 'moderate autonomy'},
                    '17+': {'programming': 'text-based', 'projects': 'innovative solutions', 'complexity': 'advanced AI integration'}
                },
                framework_alignments={
                    EducationalFramework.ISTE: ['1.4.1', '1.5.1', '1.7.1'],
                    EducationalFramework.DIGICOMP: ['Programming', 'Computational thinking', 'Digital content creation'],
                    EducationalFramework.NCF: ['Scientific inquiry', 'Design thinking', 'Technology integration']
                }
            )
        ]
    
    def _create_ai_templates(self) -> List[ProjectTemplate]:
        """Create Artificial Intelligence project templates"""
        return [
            ProjectTemplate(
                theme=ProjectTheme.ARTIFICIAL_INTELLIGENCE,
                project_type=ProjectType.DATA_ANALYSIS,
                base_title="AI for Good: Machine Learning Solutions",
                description_template="Explore artificial intelligence and machine learning concepts while developing AI solutions for social good, combining data science, ethical reasoning, programming skills, and creative problem-solving.",
                essential_questions=[
                    "How can AI help solve important social problems?",
                    "What are the ethical considerations in AI development?",
                    "How do machines learn from data?",
                    "What is the responsible way to use AI technology?"
                ],
                steam_integrations={
                    'Science': ['Data science principles', 'Pattern recognition', 'Statistical analysis', 'Research methodology'],
                    'Technology': ['Machine learning algorithms', 'Data visualization tools', 'Programming languages', 'Cloud computing'],
                    'Engineering': ['Algorithm design', 'System architecture', 'Performance optimization', 'User experience design'],
                    'Arts': ['Data storytelling', 'Visualization design', 'Ethical narratives', 'Public communication'],
                    'Mathematics': ['Statistics', 'Linear algebra', 'Probability', 'Optimization']
                },
                learning_outcomes_templates=[
                    {
                        'description': 'Apply machine learning concepts to solve real-world problems',
                        'framework': EducationalFramework.ISTE,
                        'cognitive_level': 'Apply'
                    }
                ],
                assessment_strategies=['AI model presentation', 'Ethics reflection paper', 'Code portfolio', 'Impact assessment'],
                materials_base=['Computer/tablet', 'Python environment', 'Datasets', 'Online learning platforms', 'Presentation tools'],
                duration_range=(25, 40),
                difficulty_adaptations={
                    DifficultyLevel.BEGINNER: {
                        'focus': 'AI concepts and simple applications',
                        'support': 'No-code/low-code AI tools',
                        'complexity': 'Pre-built models and datasets'
                    },
                    DifficultyLevel.INTERMEDIATE: {
                        'focus': 'Custom model training and evaluation',
                        'support': 'Guided programming tutorials',
                        'complexity': 'Supervised learning projects'
                    },
                    DifficultyLevel.ADVANCED: {
                        'focus': 'Advanced AI techniques and research',
                        'support': 'Independent learning resources',
                        'complexity': 'Novel AI applications and research'
                    }
                },
                age_adaptations={
                    '12-14': {'concepts': 'basic AI literacy', 'tools': 'visual AI builders', 'projects': 'image classification'},
                    '15-17': {'concepts': 'ML fundamentals', 'tools': 'beginner programming', 'projects': 'predictive models'},
                    '18+': {'concepts': 'advanced AI/ML', 'tools': 'professional frameworks', 'projects': 'research-level work'}
                },
                framework_alignments={
                    EducationalFramework.ISTE: ['1.1.1', '1.4.1', '1.6.1'],
                    EducationalFramework.DIGICOMP: ['Information literacy', 'Digital content creation', 'Problem solving'],
                    EducationalFramework.OECD: ['Critical thinking', 'Systems thinking', 'Anticipation']
                }
            )
        ]
    
    def _select_optimal_theme(self, learner_profile: LearnerProfile) -> ProjectTheme:
        """Select the most appropriate theme based on learner profile"""
        
        theme_scores = {}
        
        # Score themes based on multiple intelligence
        for theme in ProjectTheme:
            score = 0
            
            # Logical-mathematical intelligence
            if MultipleIntelligence.LOGICAL_MATHEMATICAL in learner_profile.multiple_intelligences:
                if theme in [ProjectTheme.ARTIFICIAL_INTELLIGENCE, ProjectTheme.MATHEMATICAL_MODELING, 
                           ProjectTheme.CYBERSECURITY]:
                    score += 3
                elif theme in [ProjectTheme.SPACE_EXPLORATION, ProjectTheme.ROBOTICS_AUTOMATION]:
                    score += 2
            
            # Spatial intelligence
            if MultipleIntelligence.SPATIAL in learner_profile.multiple_intelligences:
                if theme in [ProjectTheme.SPACE_EXPLORATION, ProjectTheme.SMART_CITIES, 
                           ProjectTheme.DIGITAL_ARTS_MEDIA]:
                    score += 3
                elif theme in [ProjectTheme.ROBOTICS_AUTOMATION, ProjectTheme.BIOTECHNOLOGY]:
                    score += 2
            
            # Naturalistic intelligence
            if MultipleIntelligence.NATURALISTIC in learner_profile.multiple_intelligences:
                if theme in [ProjectTheme.ENVIRONMENTAL_SUSTAINABILITY, ProjectTheme.OCEAN_CONSERVATION, 
                           ProjectTheme.CLIMATE_SCIENCE]:
                    score += 3
                elif theme in [ProjectTheme.FOOD_SECURITY, ProjectTheme.RENEWABLE_ENERGY]:
                    score += 2
            
            # Interest alignment
            for interest in learner_profile.interests:
                if any(word in theme.value.lower() for word in interest.lower().split()):
                    score += 2
            
            # Age appropriateness
            if learner_profile.age < 12:
                if theme in [ProjectTheme.ROBOTICS_AUTOMATION, ProjectTheme.ENVIRONMENTAL_SUSTAINABILITY]:
                    score += 1
            elif learner_profile.age >= 16:
                if theme in [ProjectTheme.ARTIFICIAL_INTELLIGENCE, ProjectTheme.BIOTECHNOLOGY, 
                           ProjectTheme.CYBERSECURITY]:
                    score += 1
            
            theme_scores[theme] = score
        
        # Return highest scoring theme
        return max(theme_scores, key=theme_scores.get)
    
    def _select_project_template(self, 
                               theme: ProjectTheme,
                               learner_profile: LearnerProfile) -> ProjectTemplate:
        """Select the most appropriate template for the theme and learner"""
        
        templates = self.project_templates.get(theme, [])
        if not templates:
            # Fallback to a generic template
            return self._create_generic_template(theme)
        
        # Score templates based on learner profile
        template_scores = []
        for template in templates:
            score = 0
            
            # Project type alignment with learning style
            if learner_profile.learning_style == LearningStyle.KINESTHETIC:
                if template.project_type in [ProjectType.DESIGN_CHALLENGE, ProjectType.INVENTION]:
                    score += 2
            elif learner_profile.learning_style == LearningStyle.VISUAL:
                if template.project_type in [ProjectType.CREATIVE_PROJECT, ProjectType.DATA_ANALYSIS]:
                    score += 2
            
            # Multiple intelligence alignment
            for intelligence in learner_profile.multiple_intelligences:
                if intelligence == MultipleIntelligence.LOGICAL_MATHEMATICAL:
                    if template.project_type in [ProjectType.INVESTIGATION, ProjectType.DATA_ANALYSIS]:
                        score += 1
                elif intelligence == MultipleIntelligence.BODILY_KINESTHETIC:
                    if template.project_type in [ProjectType.DESIGN_CHALLENGE, ProjectType.INVENTION]:
                        score += 1
            
            template_scores.append((template, score))
        
        # Return template with highest score
        best_template = max(template_scores, key=lambda x: x[1])
        return best_template[0]
    
    def _determine_difficulty_level(self, learner_profile: LearnerProfile) -> DifficultyLevel:
        """Determine appropriate difficulty level based on learner profile"""
        age = learner_profile.age
        
        if age <= 10:
            return DifficultyLevel.BEGINNER
        elif age <= 14:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.ADVANCED
    
    def _calculate_optimal_duration(self, learner_profile: LearnerProfile, difficulty: DifficultyLevel) -> int:
        """Calculate optimal project duration in weeks"""
        base_duration = {
            DifficultyLevel.BEGINNER: 2,
            DifficultyLevel.INTERMEDIATE: 4,
            DifficultyLevel.ADVANCED: 6
        }
        
        duration = base_duration[difficulty]
        
        # Adjust based on age
        if learner_profile.age <= 10:
            duration = min(duration, 3)  # Shorter attention span
        elif learner_profile.age >= 16:
            duration += 1  # Can handle longer projects
        
        return duration
    
    def _generate_materials_list(self, template, learner_profile, include_robotics, include_coding):
        """Generate materials list for the project"""
        materials = ["Notebook and pen", "Computer/tablet", "Internet access"]
        
        if include_robotics:
            materials.extend(["Luxrobo Modi kit", "Sensors", "Building materials"])
        
        if include_coding:
            materials.extend(["Python development environment", "Code editor"])
        
        # Add theme-specific materials
        materials.extend(["Research materials", "Presentation tools", "Collaboration platform"])
        
        return materials
    
    def _generate_description(self, template, learner_profile, frameworks):
        """Generate project description"""
        return f"A personalized STEAM project designed for {learner_profile.learning_style.value} learners."
    
    def _generate_prerequisites(self, template, learner_profile, difficulty):
        """Generate prerequisites for the project"""
        prerequisites = ["Basic computer skills", "Curiosity and willingness to learn"]
        
        if difficulty == DifficultyLevel.INTERMEDIATE:
            prerequisites.append("Some experience with technology")
        elif difficulty == DifficultyLevel.ADVANCED:
            prerequisites.extend(["Programming basics", "Advanced problem-solving skills"])
        
        return prerequisites
    
    def _generate_project_specification(self,
                                      template: ProjectTemplate,
                                      learner_profile: LearnerProfile,
                                      frameworks: List[EducationalFramework],
                                      difficulty_override: Optional[DifficultyLevel],
                                      duration_preference: Optional[int],
                                      include_robotics: bool,
                                      include_coding: bool,
                                      real_world_connection: bool) -> Dict[str, Any]:
        """Generate detailed project specification from template"""
        
        # Determine difficulty level
        difficulty = difficulty_override or self._determine_difficulty_level(learner_profile)
        
        # Adapt title based on age and preferences
        title = self._adapt_title(template.base_title, learner_profile)
        
        # Generate description
        description = self._generate_description(template, learner_profile, frameworks)
        
        # Determine duration
        duration = duration_preference or self._calculate_optimal_duration(
            learner_profile, difficulty
        )
        
        # Generate materials list
        materials = self._generate_materials_list(
            template, learner_profile, include_robotics, include_coding
        )
        
        # Generate prerequisites
        prerequisites = self._generate_prerequisites(template, learner_profile, difficulty)
        
        # Generate extensions
        extensions = self._generate_extensions(template, learner_profile, difficulty)
        
        return {
            'title': title,
            'description': description,
            'difficulty_level': difficulty,
            'duration': duration,
            'materials': materials,
            'prerequisites': prerequisites,
            'extensions': extensions,
            'template_source': template.base_title
        }
    
    def _adapt_title(self, base_title: str, learner_profile: LearnerProfile) -> str:
        """Adapt project title for age and interests"""
        
        age_adaptations = {
            'Detective': 'Explorer' if learner_profile.age < 12 else 'Detective',
            'Lab': 'Workshop' if learner_profile.age < 10 else 'Lab',
            'Challenge': 'Adventure' if learner_profile.age < 10 else 'Challenge',
            'Solutions': 'Ideas' if learner_profile.age < 12 else 'Solutions'
        }
        
        adapted_title = base_title
        for old_word, new_word in age_adaptations.items():
            adapted_title = adapted_title.replace(old_word, new_word)
        
        return adapted_title
    
    def _generate_description(self,
                            template: ProjectTemplate,
                            learner_profile: LearnerProfile,
                            frameworks: List[EducationalFramework]) -> str:
        """Generate personalized project description"""
        
        base_description = template.description_template
        
        # Add personalization elements
        learning_style_text = {
            LearningStyle.VISUAL: "Through visual modeling, infographics, and interactive demonstrations, ",
            LearningStyle.AUDITORY: "Through discussions, presentations, and audio resources, ",
            LearningStyle.KINESTHETIC: "Through hands-on building, experimentation, and physical manipulation, ",
            LearningStyle.READING_WRITING: "Through research, documentation, and written reflection, ",
            LearningStyle.MULTIMODAL: "Through diverse learning experiences and multiple modalities, "
        }
        
        style_prefix = learning_style_text.get(learner_profile.learning_style, "")
        
        # Add framework alignment
        framework_text = f"\n\nThis project aligns with {', '.join([f.value for f in frameworks])} standards and emphasizes 21st-century skills development."
        
        # Combine elements
        full_description = style_prefix + base_description + framework_text
        
        return full_description
    
    def _generate_learning_outcomes(self,
                                  project_spec: Dict[str, Any],
                                  frameworks: List[EducationalFramework],
                                  learner_profile: LearnerProfile) -> List[LearningOutcome]:
        """Generate comprehensive learning outcomes"""
        
        outcomes = []
        
        # Framework-specific outcomes
        for framework in frameworks:
            if framework == EducationalFramework.NGSS:
                outcomes.extend(self._generate_ngss_outcomes(project_spec, learner_profile))
            elif framework == EducationalFramework.ISTE:
                outcomes.extend(self._generate_iste_outcomes(project_spec, learner_profile))
            elif framework == EducationalFramework.OECD:
                outcomes.extend(self._generate_oecd_outcomes(project_spec, learner_profile))
            elif framework == EducationalFramework.PBL:
                outcomes.extend(self._generate_pbl_outcomes(project_spec, learner_profile))
        
        # STEAM integration outcomes
        outcomes.extend(self._generate_steam_outcomes(project_spec, learner_profile))
        
        # 21st century skills outcomes
        outcomes.extend(self._generate_21st_century_outcomes(project_spec, learner_profile))
        
        return outcomes
    
    def _generate_ngss_outcomes(self, project_spec: Dict[str, Any], learner_profile: LearnerProfile) -> List[LearningOutcome]:
        """Generate NGSS-aligned learning outcomes"""
        
        outcomes = [
            LearningOutcome(
                outcome_id=str(uuid.uuid4()),
                description="Apply scientific practices to investigate phenomena and solve problems",
                framework=EducationalFramework.NGSS,
                cognitive_level="Apply",
                assessment_criteria=[
                    "Formulates testable questions based on observations",
                    "Designs and conducts controlled investigations",
                    "Analyzes data to identify patterns and relationships",
                    "Constructs explanations based on evidence"
                ],
                steam_integration=["Science", "Mathematics"]
            ),
            LearningOutcome(
                outcome_id=str(uuid.uuid4()),
                description="Use engineering design process to develop solutions to problems",
                framework=EducationalFramework.NGSS,
                cognitive_level="Create",
                assessment_criteria=[
                    "Defines criteria and constraints for design solutions",
                    "Generates and compares multiple design solutions",
                    "Builds and tests prototypes",
                    "Optimizes solutions based on testing results"
                ],
                steam_integration=["Engineering", "Technology"]
            )
        ]
        
        return outcomes
    
    def _generate_iste_outcomes(self, project_spec: Dict[str, Any], learner_profile: LearnerProfile) -> List[LearningOutcome]:
        """Generate ISTE-aligned learning outcomes"""
        
        outcomes = [
            LearningOutcome(
                outcome_id=str(uuid.uuid4()),
                description="Demonstrate digital citizenship and responsible technology use",
                framework=EducationalFramework.ISTE,
                cognitive_level="Apply",
                assessment_criteria=[
                    "Uses technology tools ethically and responsibly",
                    "Protects personal and others' digital privacy",
                    "Demonstrates respectful online communication",
                    "Understands digital footprint implications"
                ],
                steam_integration=["Technology", "Arts"]
            ),
            LearningOutcome(
                outcome_id=str(uuid.uuid4()),
                description="Apply computational thinking to solve problems",
                framework=EducationalFramework.ISTE,
                cognitive_level="Apply",
                assessment_criteria=[
                    "Breaks down complex problems into manageable parts",
                    "Identifies patterns and generalizations",
                    "Develops algorithms and logical sequences",
                    "Tests and debugs solutions systematically"
                ],
                steam_integration=["Technology", "Mathematics"]
            )
        ]
        
        return outcomes
    
    def _generate_comprehensive_rubric(self,
                                     learning_outcomes: List[LearningOutcome],
                                     learner_profile: LearnerProfile,
                                     frameworks: List[EducationalFramework]) -> Dict[str, Any]:
        """Generate comprehensive assessment rubric"""
        
        rubric = {
            'performance_levels': ['Novice', 'Developing', 'Proficient', 'Advanced', 'Expert'],
            'criteria': {},
            'framework_alignment': {f.value: [] for f in frameworks},
            'steam_integration_scoring': {
                'Science': {'weight': 20, 'indicators': []},
                'Technology': {'weight': 20, 'indicators': []},
                'Engineering': {'weight': 20, 'indicators': []},
                'Arts': {'weight': 20, 'indicators': []},
                'Mathematics': {'weight': 20, 'indicators': []}
            },
            'personalized_adaptations': []
        }
        
        # Generate criteria from learning outcomes
        for outcome in learning_outcomes:
            criterion_key = f"{outcome.framework.value[:4]}_{outcome.cognitive_level}"
            
            rubric['criteria'][criterion_key] = {
                'description': outcome.description,
                'assessment_criteria': outcome.assessment_criteria,
                'performance_descriptors': {
                    'Novice': f"Beginning understanding of {outcome.description.lower()} with significant support needed",
                    'Developing': f"Partial demonstration of {outcome.description.lower()} with some support needed",
                    'Proficient': f"Clear demonstration of {outcome.description.lower()} meeting grade-level expectations",
                    'Advanced': f"Sophisticated demonstration of {outcome.description.lower()} exceeding expectations",
                    'Expert': f"Exceptional demonstration of {outcome.description.lower()} with innovation and mastery"
                },
                'steam_connections': outcome.steam_integration
            }
        
        # Add personalized adaptations
        if learner_profile.learning_style == LearningStyle.VISUAL:
            rubric['personalized_adaptations'].append("Visual documentation and presentation options available")
        
        if MultipleIntelligence.INTERPERSONAL in learner_profile.multiple_intelligences:
            rubric['personalized_adaptations'].append("Collaborative assessment opportunities included")
        
        return rubric
    
    def _load_real_world_contexts(self) -> Dict[ProjectTheme, List[Dict[str, Any]]]:
        """Load real-world contexts for project themes"""
        
        return {
            ProjectTheme.ENVIRONMENTAL_SUSTAINABILITY: [
                {
                    'context': 'Local water quality monitoring',
                    'partners': ['Local environmental agencies', 'Water treatment facilities', 'Community groups'],
                    'data_sources': ['EPA databases', 'Local monitoring stations', 'Citizen science platforms'],
                    'impact_potential': 'High - direct community benefit'
                },
                {
                    'context': 'Urban heat island effect study',
                    'partners': ['City planning departments', 'Weather services', 'University researchers'],
                    'data_sources': ['Weather station data', 'Satellite imagery', 'Urban temperature sensors'],
                    'impact_potential': 'Medium - policy influence potential'
                }
            ],
            ProjectTheme.SPACE_EXPLORATION: [
                {
                    'context': 'Mars rover mission simulation',
                    'partners': ['NASA educational programs', 'Space agencies', 'Aerospace companies'],
                    'data_sources': ['NASA mission data', 'Mars weather reports', 'Rover engineering specs'],
                    'impact_potential': 'Medium - STEM inspiration and education'
                }
            ]
        }
    
    def _load_framework_standards(self) -> Dict[EducationalFramework, Dict[str, Any]]:
        """Load detailed standards for each educational framework"""
        
        return {
            EducationalFramework.NGSS: {
                'elementary': {
                    'science_practices': [
                        'Asking questions and defining problems',
                        'Planning and carrying out investigations',
                        'Analyzing and interpreting data',
                        'Constructing explanations and designing solutions'
                    ],
                    'crosscutting_concepts': [
                        'Patterns', 'Cause and effect', 'Systems and system models',
                        'Energy and matter', 'Structure and function'
                    ]
                },
                'middle_school': {
                    'science_practices': [
                        'Asking questions and defining problems',
                        'Developing and using models',
                        'Planning and carrying out investigations',
                        'Analyzing and interpreting data',
                        'Using mathematics and computational thinking',
                        'Constructing explanations and designing solutions',
                        'Engaging in argument from evidence',
                        'Obtaining, evaluating, and communicating information'
                    ],
                    'engineering_practices': [
                        'Define criteria and constraints',
                        'Generate and compare solutions',
                        'Optimize design solutions'
                    ]
                }
            },
            EducationalFramework.ISTE: {
                'student_standards': {
                    'Empowered Learner': 'Students leverage technology to take an active role in choosing, achieving, and demonstrating competency in their learning goals',
                    'Digital Citizen': 'Students recognize the rights, responsibilities and opportunities of living, learning and working in an interconnected digital world',
                    'Knowledge Constructor': 'Students critically curate a variety of resources using digital tools',
                    'Innovative Designer': 'Students use a variety of technologies within a design process',
                    'Computational Thinker': 'Students develop and employ strategies for understanding and solving problems'
                }
            }
        }
    
    def _load_robotics_integrations(self) -> Dict[str, Any]:
        """Load robotics integration possibilities"""
        
        return {
            'modi_modules': {
                'Network': {
                    'capabilities': ['WiFi connectivity', 'Bluetooth communication', 'Data transmission'],
                    'projects': ['IoT data collection', 'Remote monitoring', 'Cloud integration'],
                    'age_range': '10+'
                },
                'Environment': {
                    'capabilities': ['Temperature sensing', 'Humidity monitoring', 'Light detection'],
                    'projects': ['Weather stations', 'Environmental monitoring', 'Greenhouse automation'],
                    'age_range': '8+'
                },
                'Motor': {
                    'capabilities': ['Rotation control', 'Speed variation', 'Direction control'],
                    'projects': ['Rovers', 'Automated systems', 'Mechanical solutions'],
                    'age_range': '8+'
                },
                'Input': {
                    'capabilities': ['Button input', 'Dial control', 'Joystick navigation'],
                    'projects': ['User interfaces', 'Control systems', 'Interactive devices'],
                    'age_range': '6+'
                }
            },
            'programming_concepts': {
                'beginner': ['Sequential commands', 'Basic loops', 'Simple conditionals'],
                'intermediate': ['Functions', 'Variables', 'Sensor integration', 'Decision making'],
                'advanced': ['Object-oriented programming', 'Advanced algorithms', 'Machine learning integration']
            }
        }
    
    def _load_coding_progressions(self) -> Dict[str, Any]:
        """Load coding skill progressions"""
        
        return {
            'python_skills': {
                'elementary': {
                    'concepts': ['Variables', 'Print statements', 'Simple math', 'Basic input'],
                    'projects': ['Calculators', 'Simple games', 'Art with turtle graphics'],
                    'libraries': ['turtle', 'random', 'math']
                },
                'middle_school': {
                    'concepts': ['Lists', 'Loops', 'Functions', 'Conditionals', 'File handling'],
                    'projects': ['Data analysis', 'Text processing', 'Simple simulations'],
                    'libraries': ['matplotlib', 'pandas (basic)', 'requests']
                },
                'high_school': {
                    'concepts': ['Object-oriented programming', 'APIs', 'Data structures', 'Algorithms'],
                    'projects': ['Web scraping', 'Machine learning', 'Data visualization', 'Automation'],
                    'libraries': ['scikit-learn', 'numpy', 'pandas', 'flask', 'tkinter']
                }
            },
            'computational_thinking': {
                'decomposition': 'Breaking down complex problems into smaller, manageable parts',
                'pattern_recognition': 'Identifying similarities and patterns in data or problems',
                'abstraction': 'Focusing on essential features while ignoring irrelevant details',
                'algorithms': 'Creating step-by-step solutions that can be followed or automated'
            }
        }
    
    def generate_project_variations(self, 
                                  base_project: STEAMProject,
                                  num_variations: int = 3) -> List[STEAMProject]:
        """Generate variations of a base project for different learners or contexts"""
        
        variations = []
        
        for i in range(num_variations):
            variation = STEAMProject(
                project_id=str(uuid.uuid4()),
                title=f"{base_project.title} - Variation {i+1}",
                description=base_project.description,
                theme=base_project.theme,
                learning_outcomes=base_project.learning_outcomes.copy(),
                steam_components=base_project.steam_components.copy(),
                frameworks=base_project.frameworks.copy(),
                difficulty_level=base_project.difficulty_level,
                estimated_duration_hours=base_project.estimated_duration_hours,
                robotics_components=base_project.robotics_components.copy(),
                coding_elements=base_project.coding_elements.copy(),
                required_materials=base_project.required_materials.copy(),
                prerequisites=base_project.prerequisites.copy(),
                extensions=base_project.extensions.copy(),
                assessment_rubric=base_project.assessment_rubric.copy()
            )
            
            # Apply variation-specific modifications
            if i == 0:  # More collaborative focus
                variation.title = f"{base_project.title} - Collaborative Edition"
                variation.steam_components['Arts'].append("Team presentation and communication")
                variation.required_materials.append("Collaboration tools")
            elif i == 1:  # More technology-focused
                variation.title = f"{base_project.title} - Tech Innovation Edition"
                variation.steam_components['Technology'].extend(["Advanced sensors", "Data analytics", "Cloud integration"])
                variation.coding_elements.append("Advanced programming techniques")
            elif i == 2:  # More research-focused
                variation.title = f"{base_project.title} - Research Edition"
                variation.steam_components['Science'].append("Literature review and research methodology")
                variation.prerequisites.append("Basic research skills")
            
            variations.append(variation)
        
        return variations

# Example usage and testing
if __name__ == "__main__":
    from learning_instance_manager import LearnerProfile, LearningStyle, MultipleIntelligence, EducationalFramework
    
    # Initialize project generator
    generator = STEAMProjectGenerator()
    
    # Create sample learner profile
    learner = LearnerProfile(
        user_id="test_user",
        name="Maya Explorer",
        age=13,
        learning_style=LearningStyle.VISUAL,
        multiple_intelligences=[MultipleIntelligence.SPATIAL, MultipleIntelligence.NATURALISTIC],
        interests=["environmental science", "technology", "art"]
    )
    
    # Generate personalized project
    project = generator.generate_personalized_project(
        learner_profile=learner,
        theme=ProjectTheme.ENVIRONMENTAL_SUSTAINABILITY,
        frameworks=[EducationalFramework.NGSS, EducationalFramework.ISTE, EducationalFramework.PBL],
        include_robotics=True,
        include_coding=True,
        real_world_connection=True
    )
    
    print(f"Generated Project: {project.title}")
    print(f"Description: {project.description[:200]}...")
    print(f"Duration: {project.estimated_duration_hours} hours")
    print(f"Learning Outcomes: {len(project.learning_outcomes)}")
    print(f"STEAM Components: {list(project.steam_components.keys())}")
    print(f"Robotics Integration: {len(project.robotics_components)} components")
    print(f"Coding Elements: {len(project.coding_elements)} elements")
    
    # Generate variations
    variations = generator.generate_project_variations(project, 2)
    print(f"\nGenerated {len(variations)} project variations:")
    for i, variation in enumerate(variations):
        print(f"  {i+1}. {variation.title}")