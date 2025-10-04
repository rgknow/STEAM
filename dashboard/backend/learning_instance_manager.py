"""
STEAM Learning Instance Manager

This module manages the core functionality for creating, tracking, and adapting 
interdisciplinary project-based learning paths with multiple educational framework 
integration and personalized learning experiences.
"""

import json
import uuid
import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import logging
from pathlib import Path

# Import our existing components
import sys
sys.path.append('/workspaces/STEAM')

try:
    from rag_curriculum.rag_engine import RAGEngine
    from agents.agent_framework import AgentCommunicationHub
    from age_adaptation.adaptation_system import AgeAdaptationSystem
    from robotics_education.robotics_protocol import RoboticsEducationProtocol
except ImportError as e:
    logging.warning(f"Some modules not available: {e}")
    # Create mock classes for development
    class RAGEngine:
        def search(self, query, **kwargs): return []
    class AgentCommunicationHub:
        def get_expert_consultation(self, domain, query): return "Expert consultation not available"
    class AgeAdaptationSystem:
        def adapt_content(self, content, age, **kwargs): return content
    class RoboticsEducationProtocol:
        def generate_robotics_activity(self, **kwargs): return {}

class LearningStyle(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory" 
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MULTIMODAL = "multimodal"

class MultipleIntelligence(Enum):
    LINGUISTIC = "linguistic"
    LOGICAL_MATHEMATICAL = "logical_mathematical"
    SPATIAL = "spatial"
    BODILY_KINESTHETIC = "bodily_kinesthetic"
    MUSICAL = "musical"
    INTERPERSONAL = "interpersonal"
    INTRAPERSONAL = "intrapersonal"
    NATURALISTIC = "naturalistic"
    EXISTENTIAL = "existential"

class EducationalFramework(Enum):
    NGSS = "Next Generation Science Standards"
    ISTE = "International Society for Technology in Education"
    OECD = "OECD Education 2030"
    DIGICOMP = "European Digital Competence Framework"
    NCF = "National Curriculum Framework 2023"
    PBL = "Project-Based Learning"
    STEAM = "Science Technology Engineering Arts Mathematics"

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ProjectStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    ARCHIVED = "archived"

@dataclass
class LearnerProfile:
    """Comprehensive learner profile with personalization data"""
    user_id: str
    name: str
    age: int
    grade_level: Optional[str] = None
    learning_style: LearningStyle = LearningStyle.MULTIMODAL
    multiple_intelligences: List[MultipleIntelligence] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    current_level: int = 1
    streak_days: int = 0
    completed_projects: int = 0
    preferred_frameworks: List[EducationalFramework] = field(default_factory=list)
    accessibility_needs: List[str] = field(default_factory=list)
    language_preference: str = "en"
    timezone: str = "UTC"
    learning_goals: List[str] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    last_active: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class LearningOutcome:
    """Specific learning objective with assessment criteria"""
    outcome_id: str
    description: str
    framework: EducationalFramework
    cognitive_level: str  # Bloom's taxonomy level
    assessment_criteria: List[str] = field(default_factory=list)
    steam_integration: List[str] = field(default_factory=list)
    is_achieved: bool = False
    evidence: List[str] = field(default_factory=list)

@dataclass
class STEAMProject:
    """Comprehensive STEAM project with interdisciplinary elements"""
    project_id: str
    title: str
    description: str
    theme: str
    learning_outcomes: List[LearningOutcome] = field(default_factory=list)
    steam_components: Dict[str, List[str]] = field(default_factory=dict)
    frameworks: List[EducationalFramework] = field(default_factory=list)
    difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    estimated_duration_hours: int = 10
    robotics_components: List[str] = field(default_factory=list)
    coding_elements: List[str] = field(default_factory=list)
    required_materials: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    extensions: List[str] = field(default_factory=list)
    assessment_rubric: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class LearningInstance:
    """Active learning session with progress tracking"""
    instance_id: str
    user_id: str
    project_id: str
    status: ProjectStatus = ProjectStatus.NOT_STARTED
    progress_percentage: float = 0.0
    current_activity: Optional[str] = None
    completed_activities: List[str] = field(default_factory=list)
    time_spent_minutes: int = 0
    engagement_score: float = 0.0
    adaptations_applied: List[str] = field(default_factory=list)
    artifacts_created: List[str] = field(default_factory=list)
    reflection_entries: List[Dict[str, Any]] = field(default_factory=list)
    peer_collaborators: List[str] = field(default_factory=list)
    mentor_feedback: List[Dict[str, Any]] = field(default_factory=list)
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None
    last_activity: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class LearningPath:
    """Sequence of projects forming a coherent learning journey"""
    path_id: str
    title: str
    description: str
    projects: List[str] = field(default_factory=list)  # project_ids
    prerequisites: List[str] = field(default_factory=list)
    target_audience: Dict[str, Any] = field(default_factory=dict)
    estimated_total_hours: int = 40
    competencies_developed: List[str] = field(default_factory=list)
    certification_available: bool = False
    adaptive_sequencing: bool = True
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

class LearningInstanceManager:
    """
    Central manager for STEAM learning instances with comprehensive
    personalization, adaptation, and progress tracking.
    """
    
    def __init__(self, data_file: Optional[str] = None):
        """Initialize the Learning Instance Manager"""
        
        # Initialize logger first
        import logging
        self.logger = logging.getLogger('LearningInstanceManager')
        
        # Core data storage
        self.learners: Dict[str, LearnerProfile] = {}
        self.projects: Dict[str, Project] = {}
        self.instances: Dict[str, LearningInstance] = {}
        
        # Learning frameworks integration
        self._initialize_frameworks()
        
        # Age adaptation system
        try:
            from age_adaptation.adaptation_system import AgeAdaptationSystem
            self.age_adaptation = AgeAdaptationSystem()
        except ImportError:
            self.age_adaptation = None
            print("Warning: Age adaptation system not available")
        
        # RAG curriculum integration
        try:
            from rag_curriculum.rag_engine import RAGEngine
            self.rag_engine = RAGEngine()
        except ImportError:
            self.rag_engine = None
            print("Warning: RAG curriculum system not available")
        
        # Data persistence
        self.data_file = data_file or '/workspaces/STEAM/dashboard/data/learning_data.json'
        self.data_dir = Path('/workspaces/STEAM/dashboard/data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_data()
        
    def _setup_logging(self):
        """Setup comprehensive logging for learning analytics"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.data_dir / 'learning_analytics.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('LearningInstanceManager')
    
    def _load_data(self):
        """Load persistent data from files"""
        try:
            # Load learners
            learners_file = self.data_dir / 'learners.json'
            if learners_file.exists():
                with open(learners_file, 'r') as f:
                    data = json.load(f)
                    self.learners = {
                        uid: LearnerProfile(**profile) 
                        for uid, profile in data.items()
                    }
            
            # Load projects
            projects_file = self.data_dir / 'projects.json'
            if projects_file.exists():
                with open(projects_file, 'r') as f:
                    data = json.load(f)
                    self.projects = {
                        pid: STEAMProject(**project)
                        for pid, project in data.items()
                    }
            
            # Load instances
            instances_file = self.data_dir / 'instances.json'
            if instances_file.exists():
                with open(instances_file, 'r') as f:
                    data = json.load(f)
                    self.instances = {
                        iid: LearningInstance(**instance)
                        for iid, instance in data.items()
                    }
                    
            self.logger.info(f"Loaded {len(self.learners)} learners, {len(self.projects)} projects, {len(self.instances)} instances")
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
    
    def _initialize_frameworks(self):
        """Initialize educational framework mappings"""
        self.framework_mappings = {
            EducationalFramework.NGSS: {
                'name': 'Next Generation Science Standards',
                'focus': 'Science and Engineering Practices'
            },
            EducationalFramework.ISTE: {
                'name': 'International Society for Technology in Education',
                'focus': 'Digital citizenship and technology skills'
            },
            EducationalFramework.PBL: {
                'name': 'Project-Based Learning',
                'focus': 'Real-world problem solving'
            },
            EducationalFramework.OECD: {
                'name': 'OECD Education 2030',
                'focus': '21st century competencies'
            },
            EducationalFramework.DIGICOMP: {
                'name': 'European Digital Competence Framework',
                'focus': 'Digital literacy and skills'
            },
            EducationalFramework.NCF: {
                'name': 'National Curriculum Framework 2023',
                'focus': 'Holistic and multidisciplinary education'
            }
        }
    
    def _save_data(self):
        """Persist data to files"""
        try:
            # Save learners
            with open(self.data_dir / 'learners.json', 'w') as f:
                json.dump({uid: asdict(profile) for uid, profile in self.learners.items()}, f, default=str, indent=2)
            
            # Save projects
            with open(self.data_dir / 'projects.json', 'w') as f:
                json.dump({pid: asdict(project) for pid, project in self.projects.items()}, f, default=str, indent=2)
            
            # Save instances
            with open(self.data_dir / 'instances.json', 'w') as f:
                json.dump({iid: asdict(instance) for iid, instance in self.instances.items()}, f, default=str, indent=2)
                
            self.logger.info("Data saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
    
    def create_learner_profile(self, 
                             name: str, 
                             age: int,
                             learning_style: LearningStyle = LearningStyle.MULTIMODAL,
                             **kwargs) -> str:
        """Create a new learner profile with personalization"""
        user_id = str(uuid.uuid4())
        
        # Determine grade level from age
        grade_level = self._age_to_grade_level(age)
        
        # Create profile
        profile = LearnerProfile(
            user_id=user_id,
            name=name,
            age=age,
            grade_level=grade_level,
            learning_style=learning_style,
            **kwargs
        )
        
        self.learners[user_id] = profile
        self._save_data()
        
        self.logger.info(f"Created learner profile for {name} (ID: {user_id})")
        return user_id
    
    def _age_to_grade_level(self, age: int) -> str:
        """Convert age to approximate grade level"""
        if age <= 5:
            return "Pre-K"
        elif age <= 6:
            return "K"
        elif 7 <= age <= 17:
            return f"Grade {age - 6}"
        elif 18 <= age <= 22:
            return "Undergraduate"
        else:
            return "Adult"
    
    def generate_personalized_project(self, 
                                    user_id: str,
                                    theme: str,
                                    frameworks: List[EducationalFramework],
                                    difficulty_override: Optional[DifficultyLevel] = None) -> str:
        """Generate a personalized STEAM project based on learner profile"""
        
        if user_id not in self.learners:
            raise ValueError(f"Learner {user_id} not found")
        
        learner = self.learners[user_id]
        project_id = str(uuid.uuid4())
        
        # Determine difficulty level
        difficulty = difficulty_override or self._determine_difficulty_level(learner)
        
        # Generate project using RAG and expert agents
        project_spec = self._generate_project_specification(learner, theme, frameworks, difficulty)
        
        # Create learning outcomes
        learning_outcomes = self._generate_learning_outcomes(project_spec, frameworks, learner)
        
        # Generate STEAM components
        steam_components = self._generate_steam_components(project_spec, learner)
        
        # Add robotics integration if appropriate
        robotics_components = []
        if learner.age >= 8 and MultipleIntelligence.BODILY_KINESTHETIC in learner.multiple_intelligences:
            robotics_components = self._generate_robotics_components(project_spec)
        
        # Add coding elements
        coding_elements = self._generate_coding_elements(project_spec, learner)
        
        # Create project
        project = STEAMProject(
            project_id=project_id,
            title=project_spec['title'],
            description=project_spec['description'],
            theme=theme,
            learning_outcomes=learning_outcomes,
            steam_components=steam_components,
            frameworks=frameworks,
            difficulty_level=difficulty,
            estimated_duration_hours=project_spec.get('duration', 10),
            robotics_components=robotics_components,
            coding_elements=coding_elements,
            required_materials=project_spec.get('materials', []),
            prerequisites=project_spec.get('prerequisites', []),
            extensions=project_spec.get('extensions', []),
            assessment_rubric=self._generate_assessment_rubric(learning_outcomes)
        )
        
        self.projects[project_id] = project
        self._save_data()
        
        self.logger.info(f"Generated personalized project '{project.title}' for learner {user_id}")
        return project_id
    
    def _determine_difficulty_level(self, learner: LearnerProfile) -> DifficultyLevel:
        """Determine appropriate difficulty level based on learner profile"""
        if learner.current_level <= 2:
            return DifficultyLevel.BEGINNER
        elif learner.current_level <= 5:
            return DifficultyLevel.INTERMEDIATE
        elif learner.current_level <= 8:
            return DifficultyLevel.ADVANCED
        else:
            return DifficultyLevel.EXPERT
    
    def _generate_project_specification(self, 
                                      learner: LearnerProfile,
                                      theme: str,
                                      frameworks: List[EducationalFramework],
                                      difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate project specification using RAG and expert consultation"""
        
        # Query RAG for curriculum-aligned content
        rag_query = f"{theme} project for {learner.grade_level} {difficulty.value} level"
        rag_results = self.rag_engine.search(rag_query, max_results=5)
        
        # Get expert consultation
        expert_domain = self._determine_primary_domain(theme)
        expert_consultation = self.agent_hub.get_expert_consultation(
            expert_domain, 
            f"Design {theme} project for {learner.age}-year-old with {learner.learning_style.value} learning style"
        )
        
        # Generate project specification
        project_spec = {
            'title': self._generate_project_title(theme, learner),
            'description': self._generate_project_description(theme, learner, frameworks),
            'duration': self._estimate_project_duration(difficulty, learner.age),
            'materials': self._generate_required_materials(theme, difficulty),
            'prerequisites': self._generate_prerequisites(difficulty, learner),
            'extensions': self._generate_extensions(theme, difficulty, learner),
            'rag_insights': rag_results,
            'expert_insights': expert_consultation
        }
        
        return project_spec
    
    def _generate_project_title(self, theme: str, learner: LearnerProfile) -> str:
        """Generate engaging project title"""
        age_appropriate_titles = {
            'Environmental Sustainability': {
                'young': "Eco-Detective Adventure",
                'middle': "Green Innovation Challenge", 
                'older': "Sustainable Solutions Lab"
            },
            'Space Exploration': {
                'young': "Mission to Mars Explorer",
                'middle': "Spacecraft Engineering Challenge",
                'older': "Astrobiology Research Project"
            },
            'Smart Cities': {
                'young': "Future City Builder",
                'middle': "Urban Innovation Lab",
                'older': "Sustainable City Systems Design"
            }
        }
        
        age_category = 'young' if learner.age < 12 else 'middle' if learner.age < 16 else 'older'
        
        if theme in age_appropriate_titles:
            return age_appropriate_titles[theme].get(age_category, f"{theme} Project")
        
        return f"{theme} Challenge"
    
    def _generate_project_description(self, 
                                    theme: str,
                                    learner: LearnerProfile,
                                    frameworks: List[EducationalFramework]) -> str:
        """Generate detailed project description"""
        
        base_descriptions = {
            'Environmental Sustainability': f"""
            Become an environmental scientist and engineer as you investigate real-world sustainability challenges. 
            You'll collect data, design solutions, and create prototypes that address environmental issues in your community.
            This project integrates science investigation, technology tools, engineering design, artistic communication, 
            and mathematical analysis to tackle one of today's most important challenges.
            """,
            'Space Exploration': f"""
            Join the next generation of space explorers! Design, build, and test solutions for space missions.
            You'll apply physics principles, use engineering design processes, create mission protocols, 
            and analyze data to solve real challenges faced by astronauts and mission planners.
            """,
            'Smart Cities': f"""
            Design the cities of the future! Investigate urban challenges and create innovative solutions
            that make cities more sustainable, efficient, and livable. You'll use data analysis,
            engineering design, creative problem-solving, and systems thinking to address real urban issues.
            """
        }
        
        description = base_descriptions.get(theme, f"Explore {theme} through hands-on STEAM investigation.")
        
        # Adapt for learning style
        if learner.learning_style == LearningStyle.VISUAL:
            description += "\n\nThis project emphasizes visual learning through diagrams, infographics, and interactive models."
        elif learner.learning_style == LearningStyle.KINESTHETIC:
            description += "\n\nThis project includes hands-on building, experimentation, and physical manipulation of materials."
        
        # Add framework alignment
        framework_text = ", ".join([f.value for f in frameworks])
        description += f"\n\nAligned with: {framework_text}"
        
        return description.strip()
    
    def _generate_learning_outcomes(self, 
                                  project_spec: Dict[str, Any],
                                  frameworks: List[EducationalFramework],
                                  learner: LearnerProfile) -> List[LearningOutcome]:
        """Generate specific learning outcomes aligned with frameworks"""
        
        outcomes = []
        
        # NGSS-aligned outcomes
        if EducationalFramework.NGSS in frameworks:
            outcomes.extend([
                LearningOutcome(
                    outcome_id=str(uuid.uuid4()),
                    description="Apply scientific practices to investigate real-world phenomena",
                    framework=EducationalFramework.NGSS,
                    cognitive_level="Apply",
                    assessment_criteria=["Formulates testable questions", "Collects and analyzes data", "Draws evidence-based conclusions"],
                    steam_integration=["Science", "Mathematics"]
                ),
                LearningOutcome(
                    outcome_id=str(uuid.uuid4()),
                    description="Use engineering design process to develop solutions",
                    framework=EducationalFramework.NGSS,
                    cognitive_level="Create",
                    assessment_criteria=["Identifies design constraints", "Develops multiple solutions", "Tests and refines designs"],
                    steam_integration=["Engineering", "Technology"]
                )
            ])
        
        # ISTE-aligned outcomes
        if EducationalFramework.ISTE in frameworks:
            outcomes.extend([
                LearningOutcome(
                    outcome_id=str(uuid.uuid4()),
                    description="Demonstrate computational thinking and digital citizenship",
                    framework=EducationalFramework.ISTE,
                    cognitive_level="Apply",
                    assessment_criteria=["Uses technology tools effectively", "Shows digital responsibility", "Applies computational thinking"],
                    steam_integration=["Technology", "Mathematics"]
                )
            ])
        
        # PBL-aligned outcomes
        if EducationalFramework.PBL in frameworks:
            outcomes.extend([
                LearningOutcome(
                    outcome_id=str(uuid.uuid4()),
                    description="Collaborate effectively to solve authentic problems",
                    framework=EducationalFramework.PBL,
                    cognitive_level="Evaluate",
                    assessment_criteria=["Contributes meaningfully to team", "Communicates ideas clearly", "Reflects on learning process"],
                    steam_integration=["Arts", "Engineering"]
                )
            ])
        
        return outcomes
    
    def _generate_steam_components(self, 
                                 project_spec: Dict[str, Any],
                                 learner: LearnerProfile) -> Dict[str, List[str]]:
        """Generate specific STEAM integration components"""
        
        components = {
            'Science': [
                "Scientific inquiry and investigation",
                "Data collection and analysis",
                "Hypothesis formation and testing",
                "Evidence-based reasoning"
            ],
            'Technology': [
                "Digital tools for research and analysis",
                "Data visualization software",
                "Simulation and modeling tools",
                "Presentation technology"
            ],
            'Engineering': [
                "Engineering design process",
                "Problem identification and constraints",
                "Solution design and prototyping",
                "Testing and iteration"
            ],
            'Arts': [
                "Creative communication of findings",
                "Visual design and infographics",
                "Storytelling and presentation",
                "Aesthetic considerations in design"
            ],
            'Mathematics': [
                "Data analysis and statistics",
                "Measurement and calculation",
                "Pattern recognition",
                "Mathematical modeling"
            ]
        }
        
        # Adapt components based on learner profile
        if MultipleIntelligence.LINGUISTIC in learner.multiple_intelligences:
            components['Arts'].append("Written communication and documentation")
        
        if MultipleIntelligence.SPATIAL in learner.multiple_intelligences:
            components['Arts'].append("3D modeling and spatial design")
            components['Technology'].append("CAD and design software")
        
        return components
    
    def _generate_robotics_components(self, project_spec: Dict[str, Any]) -> List[str]:
        """Generate robotics integration using Modi kit"""
        
        robotics_activity = self.robotics_protocol.generate_robotics_activity(
            theme=project_spec.get('title', ''),
            difficulty='intermediate'
        )
        
        return [
            "Modi Network Module for data transmission",
            "Environment sensors for real-world data collection",
            "Motor modules for mechanical solutions",
            "Programming modules for autonomous behavior",
            "Input/output modules for user interaction"
        ]
    
    def _generate_coding_elements(self, 
                                project_spec: Dict[str, Any],
                                learner: LearnerProfile) -> List[str]:
        """Generate Python coding integration"""
        
        base_elements = [
            "Data collection and processing scripts",
            "Statistical analysis and visualization",
            "Algorithm development for problem-solving",
            "Automation of repetitive tasks"
        ]
        
        # Age-appropriate additions
        if learner.age >= 12:
            base_elements.extend([
                "Machine learning for pattern recognition",
                "API integration for real-world data",
                "Web scraping for research data"
            ])
        
        if learner.age >= 15:
            base_elements.extend([
                "Advanced data science libraries (pandas, numpy, sklearn)",
                "Database management and queries",
                "GUI development for user interfaces"
            ])
        
        return base_elements
    
    def _generate_assessment_rubric(self, learning_outcomes: List[LearningOutcome]) -> Dict[str, Any]:
        """Generate comprehensive assessment rubric"""
        
        rubric = {
            'performance_levels': ['Novice', 'Developing', 'Proficient', 'Advanced'],
            'criteria': {}
        }
        
        for outcome in learning_outcomes:
            criteria_key = outcome.description[:50] + "..."
            rubric['criteria'][criteria_key] = {
                'Novice': 'Beginning understanding with significant support needed',
                'Developing': 'Partial understanding with some support needed',
                'Proficient': 'Clear understanding meeting expectations',
                'Advanced': 'Deep understanding exceeding expectations'
            }
        
        return rubric
    
    def create_learning_instance(self, user_id: str, project_id: str) -> str:
        """Create a new learning instance for active project engagement"""
        
        if user_id not in self.learners:
            raise ValueError(f"Learner {user_id} not found")
        
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        
        instance_id = str(uuid.uuid4())
        
        instance = LearningInstance(
            instance_id=instance_id,
            user_id=user_id,
            project_id=project_id,
            status=ProjectStatus.NOT_STARTED,
            started_at=datetime.datetime.now()
        )
        
        self.instances[instance_id] = instance
        self._save_data()
        
        self.logger.info(f"Created learning instance {instance_id} for user {user_id}, project {project_id}")
        return instance_id
    
    def start_learning_instance(self, instance_id: str) -> Dict[str, Any]:
        """Start a learning instance with personalized adaptation"""
        
        if instance_id not in self.instances:
            raise ValueError(f"Learning instance {instance_id} not found")
        
        instance = self.instances[instance_id]
        learner = self.learners[instance.user_id]
        project = self.projects[instance.project_id]
        
        # Update instance status
        instance.status = ProjectStatus.IN_PROGRESS
        instance.started_at = datetime.datetime.now()
        
        # Apply personalized adaptations
        adaptations = self._apply_personalized_adaptations(learner, project)
        instance.adaptations_applied = adaptations
        
        # Generate first activity
        first_activity = self._generate_next_activity(instance, learner, project)
        instance.current_activity = first_activity['activity_id']
        
        self._save_data()
        
        self.logger.info(f"Started learning instance {instance_id}")
        
        return {
            'instance_id': instance_id,
            'status': 'started',
            'first_activity': first_activity,
            'adaptations': adaptations,
            'estimated_duration': project.estimated_duration_hours
        }
    
    def _apply_personalized_adaptations(self, 
                                      learner: LearnerProfile,
                                      project: STEAMProject) -> List[str]:
        """Apply personalized adaptations based on learner profile"""
        
        adaptations = []
        
        # Age-appropriate adaptations
        if learner.age < 10:
            adaptations.extend([
                "Simplified vocabulary and concepts",
                "Visual step-by-step guides",
                "Shorter activity segments (15-20 minutes)",
                "Immediate feedback and encouragement"
            ])
        elif learner.age < 14:
            adaptations.extend([
                "Age-appropriate examples and contexts",
                "Scaffolded complex concepts",
                "Peer collaboration opportunities",
                "Choice in presentation formats"
            ])
        else:
            adaptations.extend([
                "Advanced challenge extensions",
                "Independent research components",
                "Real-world application emphasis",
                "Mentor connection opportunities"
            ])
        
        # Learning style adaptations
        if learner.learning_style == LearningStyle.VISUAL:
            adaptations.extend([
                "Infographics and visual organizers",
                "Video demonstrations",
                "Mind mapping tools",
                "Color-coded information"
            ])
        elif learner.learning_style == LearningStyle.KINESTHETIC:
            adaptations.extend([
                "Hands-on manipulation activities",
                "Movement-based learning",
                "Physical building and creating",
                "Tactile materials and tools"
            ])
        elif learner.learning_style == LearningStyle.AUDITORY:
            adaptations.extend([
                "Audio instructions and explanations",
                "Discussion and verbal processing",
                "Music and sound integration",
                "Verbal presentation opportunities"
            ])
        
        # Multiple intelligence adaptations
        for intelligence in learner.multiple_intelligences:
            if intelligence == MultipleIntelligence.LOGICAL_MATHEMATICAL:
                adaptations.append("Pattern recognition and logical sequence activities")
            elif intelligence == MultipleIntelligence.SPATIAL:
                adaptations.append("3D visualization and spatial reasoning tasks")
            elif intelligence == MultipleIntelligence.LINGUISTIC:
                adaptations.append("Written reflection and communication emphasis")
            elif intelligence == MultipleIntelligence.INTERPERSONAL:
                adaptations.append("Collaborative group work and peer teaching")
        
        return adaptations
    
    def _generate_next_activity(self, 
                              instance: LearningInstance,
                              learner: LearnerProfile,
                              project: STEAMProject) -> Dict[str, Any]:
        """Generate the next appropriate activity for the learner"""
        
        activity_id = str(uuid.uuid4())
        
        # Determine activity type based on progress and learner profile
        if not instance.completed_activities:
            # First activity: Project introduction and goal setting
            activity = {
                'activity_id': activity_id,
                'title': f"Welcome to {project.title}!",
                'type': 'introduction',
                'description': "Let's explore your project and set learning goals together.",
                'instructions': self._generate_intro_instructions(project, learner),
                'estimated_duration': 15,
                'materials_needed': [],
                'assessment_type': 'self_reflection',
                'adaptations': instance.adaptations_applied
            }
        else:
            # Subsequent activities based on project structure
            activity = self._generate_progressive_activity(instance, learner, project)
        
        return activity
    
    def _generate_intro_instructions(self, 
                                   project: STEAMProject,
                                   learner: LearnerProfile) -> List[str]:
        """Generate personalized introduction instructions"""
        
        instructions = [
            f"Welcome to your {project.theme} project!",
            f"This project is designed specifically for your {learner.learning_style.value} learning style.",
            "Let's start by exploring what you'll learn and create.",
            "Take a moment to think about what you already know about this topic.",
            "Set 2-3 personal learning goals for this project."
        ]
        
        # Add age-appropriate elements
        if learner.age < 12:
            instructions.insert(1, "Get ready for an exciting learning adventure!")
        else:
            instructions.insert(1, "You'll be working on real-world challenges that matter.")
        
        return instructions
    
    def update_learning_progress(self, 
                               instance_id: str,
                               activity_completed: str,
                               time_spent: int,
                               engagement_score: float,
                               artifacts: List[str] = None) -> Dict[str, Any]:
        """Update learning progress with comprehensive tracking"""
        
        if instance_id not in self.instances:
            raise ValueError(f"Learning instance {instance_id} not found")
        
        instance = self.instances[instance_id]
        learner = self.learners[instance.user_id]
        project = self.projects[instance.project_id]
        
        # Update instance progress
        instance.completed_activities.append(activity_completed)
        instance.time_spent_minutes += time_spent
        instance.engagement_score = (instance.engagement_score + engagement_score) / 2
        instance.last_activity = datetime.datetime.now()
        
        if artifacts:
            instance.artifacts_created.extend(artifacts)
        
        # Calculate progress percentage
        total_activities = len(project.learning_outcomes) * 3  # Rough estimate
        instance.progress_percentage = min(100, (len(instance.completed_activities) / total_activities) * 100)
        
        # Check for completion
        if instance.progress_percentage >= 100:
            instance.status = ProjectStatus.COMPLETED
            instance.completed_at = datetime.datetime.now()
            self._handle_project_completion(instance, learner, project)
        
        # Generate next activity
        next_activity = None
        if instance.status == ProjectStatus.IN_PROGRESS:
            next_activity = self._generate_next_activity(instance, learner, project)
            instance.current_activity = next_activity['activity_id']
        
        # Update learner stats
        if instance.status == ProjectStatus.COMPLETED:
            learner.completed_projects += 1
            learner.current_level = min(10, learner.current_level + 0.5)
        
        learner.last_active = datetime.datetime.now()
        
        self._save_data()
        
        return {
            'instance_id': instance_id,
            'progress_percentage': instance.progress_percentage,
            'status': instance.status.value,
            'next_activity': next_activity,
            'engagement_score': instance.engagement_score,
            'time_spent_total': instance.time_spent_minutes,
            'level_progress': learner.current_level
        }
    
    def _handle_project_completion(self, 
                                 instance: LearningInstance,
                                 learner: LearnerProfile,
                                 project: STEAMProject):
        """Handle project completion with celebration and next steps"""
        
        completion_data = {
            'completed_at': instance.completed_at,
            'total_time': instance.time_spent_minutes,
            'engagement_score': instance.engagement_score,
            'artifacts_created': len(instance.artifacts_created),
            'learning_outcomes_achieved': len([o for o in project.learning_outcomes if o.is_achieved])
        }
        
        # Generate completion certificate data
        certificate_data = {
            'learner_name': learner.name,
            'project_title': project.title,
            'completion_date': instance.completed_at.strftime('%B %d, %Y'),
            'frameworks_completed': [f.value for f in project.frameworks],
            'skills_demonstrated': [outcome.description for outcome in project.learning_outcomes if outcome.is_achieved]
        }
        
        # Log achievement
        self.logger.info(f"Project completed: {project.title} by {learner.name} in {instance.time_spent_minutes} minutes")
        
        return completion_data, certificate_data
    
    def get_personalized_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Generate personalized learning recommendations"""
        
        if user_id not in self.learners:
            raise ValueError(f"Learner {user_id} not found")
        
        learner = self.learners[user_id]
        
        # Get learner's project history
        learner_instances = [i for i in self.instances.values() if i.user_id == user_id]
        completed_projects = [i.project_id for i in learner_instances if i.status == ProjectStatus.COMPLETED]
        
        # Generate recommendations based on:
        # 1. Learning style and multiple intelligences
        # 2. Previous project themes and success
        # 3. Current level and challenge readiness
        # 4. Educational framework alignment
        
        recommendations = {
            'suggested_themes': self._recommend_themes(learner, completed_projects),
            'difficulty_progression': self._recommend_difficulty_progression(learner),
            'learning_paths': self._recommend_learning_paths(learner),
            'skill_development': self._recommend_skill_development(learner, learner_instances),
            'collaboration_opportunities': self._recommend_collaborations(learner),
            'extension_activities': self._recommend_extensions(learner, completed_projects)
        }
        
        return recommendations
    
    def _recommend_themes(self, learner: LearnerProfile, completed_projects: List[str]) -> List[Dict[str, Any]]:
        """Recommend project themes based on learner profile and history"""
        
        all_themes = [
            'Environmental Sustainability',
            'Space Exploration', 
            'Smart Cities',
            'Renewable Energy',
            'Ocean Conservation',
            'Biotechnology Innovation',
            'Artificial Intelligence',
            'Robotics and Automation',
            'Digital Arts and Media',
            'Mathematical Modeling'
        ]
        
        # Filter out completed themes
        completed_themes = [self.projects[pid].theme for pid in completed_projects if pid in self.projects]
        available_themes = [t for t in all_themes if t not in completed_themes]
        
        # Score themes based on learner profile
        theme_scores = {}
        for theme in available_themes:
            score = 0
            
            # Multiple intelligence alignment
            if theme in ['Mathematical Modeling', 'Artificial Intelligence'] and MultipleIntelligence.LOGICAL_MATHEMATICAL in learner.multiple_intelligences:
                score += 3
            if theme in ['Digital Arts and Media', 'Biotechnology Innovation'] and MultipleIntelligence.SPATIAL in learner.multiple_intelligences:
                score += 3
            if theme in ['Environmental Sustainability', 'Ocean Conservation'] and MultipleIntelligence.NATURALISTIC in learner.multiple_intelligences:
                score += 3
            
            # Interest alignment
            for interest in learner.interests:
                if any(word in theme.lower() for word in interest.lower().split()):
                    score += 2
            
            theme_scores[theme] = score
        
        # Return top recommendations
        sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'theme': theme,
                'relevance_score': score,
                'reason': self._generate_theme_recommendation_reason(theme, learner)
            }
            for theme, score in sorted_themes[:5]
        ]
    
    def _generate_theme_recommendation_reason(self, theme: str, learner: LearnerProfile) -> str:
        """Generate explanation for theme recommendation"""
        
        reasons = {
            'Environmental Sustainability': f"Perfect for your {learner.learning_style.value} learning style with hands-on investigation and visual data analysis.",
            'Space Exploration': f"Combines your interests with engineering design and mathematical modeling challenges.",
            'Smart Cities': f"Integrates technology and creative problem-solving aligned with your intelligence strengths.",
            'Artificial Intelligence': f"Builds on logical-mathematical thinking with real-world applications."
        }
        
        return reasons.get(theme, f"Expands your STEAM knowledge in an engaging new direction.")
    
    def get_learning_analytics(self, user_id: str, time_period: int = 30) -> Dict[str, Any]:
        """Generate comprehensive learning analytics for the user"""
        
        if user_id not in self.learners:
            raise ValueError(f"Learner {user_id} not found")
        
        learner = self.learners[user_id]
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=time_period)
        
        # Get recent instances
        recent_instances = [
            i for i in self.instances.values() 
            if i.user_id == user_id and i.last_activity >= cutoff_date
        ]
        
        analytics = {
            'learning_summary': {
                'total_projects': len([i for i in self.instances.values() if i.user_id == user_id]),
                'completed_projects': len([i for i in recent_instances if i.status == ProjectStatus.COMPLETED]),
                'in_progress_projects': len([i for i in recent_instances if i.status == ProjectStatus.IN_PROGRESS]),
                'total_learning_time': sum(i.time_spent_minutes for i in recent_instances),
                'average_engagement': sum(i.engagement_score for i in recent_instances) / len(recent_instances) if recent_instances else 0,
                'current_level': learner.current_level,
                'streak_days': learner.streak_days
            },
            'progress_trends': self._calculate_progress_trends(recent_instances),
            'skill_development': self._analyze_skill_development(user_id, recent_instances),
            'framework_coverage': self._analyze_framework_coverage(user_id, recent_instances),
            'learning_style_effectiveness': self._analyze_learning_style_effectiveness(learner, recent_instances),
            'recommendations': self.get_personalized_recommendations(user_id)
        }
        
        return analytics
    
    def _calculate_progress_trends(self, instances: List[LearningInstance]) -> Dict[str, Any]:
        """Calculate learning progress trends"""
        
        if not instances:
            return {'trend': 'insufficient_data'}
        
        # Sort by start date
        sorted_instances = sorted(instances, key=lambda x: x.started_at or datetime.datetime.min)
        
        completion_times = []
        engagement_scores = []
        
        for instance in sorted_instances:
            if instance.status == ProjectStatus.COMPLETED:
                completion_times.append(instance.time_spent_minutes)
                engagement_scores.append(instance.engagement_score)
        
        trends = {
            'completion_trend': 'improving' if len(completion_times) > 1 and completion_times[-1] < completion_times[0] else 'stable',
            'engagement_trend': 'improving' if len(engagement_scores) > 1 and engagement_scores[-1] > engagement_scores[0] else 'stable',
            'project_completion_rate': len([i for i in instances if i.status == ProjectStatus.COMPLETED]) / len(instances) * 100,
            'average_time_per_project': sum(completion_times) / len(completion_times) if completion_times else 0
        }
        
        return trends
    
    def export_learning_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Export comprehensive learning portfolio for the user"""
        
        if user_id not in self.learners:
            raise ValueError(f"Learner {user_id} not found")
        
        learner = self.learners[user_id]
        learner_instances = [i for i in self.instances.values() if i.user_id == user_id]
        completed_instances = [i for i in learner_instances if i.status == ProjectStatus.COMPLETED]
        
        portfolio = {
            'learner_profile': asdict(learner),
            'learning_journey': {
                'total_projects_completed': len(completed_instances),
                'total_learning_hours': sum(i.time_spent_minutes for i in completed_instances) / 60,
                'average_engagement_score': sum(i.engagement_score for i in completed_instances) / len(completed_instances) if completed_instances else 0,
                'frameworks_experienced': list(set(
                    framework.value for instance in completed_instances
                    for framework in self.projects[instance.project_id].frameworks
                )),
                'steam_competencies': self._extract_steam_competencies(user_id, completed_instances),
                'skill_progression': self._analyze_skill_progression(user_id, completed_instances)
            },
            'project_showcase': [
                {
                    'project_title': self.projects[instance.project_id].title,
                    'theme': self.projects[instance.project_id].theme,
                    'completion_date': instance.completed_at.strftime('%B %Y') if instance.completed_at else 'In Progress',
                    'artifacts_created': instance.artifacts_created,
                    'learning_outcomes_achieved': len([o for o in self.projects[instance.project_id].learning_outcomes if o.is_achieved]),
                    'time_invested_hours': instance.time_spent_minutes / 60,
                    'engagement_score': instance.engagement_score
                }
                for instance in completed_instances
            ],
            'certifications': self._generate_certifications(user_id, completed_instances),
            'recommendations_for_growth': self.get_personalized_recommendations(user_id)
        }
        
        return portfolio

    def _extract_steam_competencies(self, user_id: str, instances: List[LearningInstance]) -> Dict[str, List[str]]:
        """Extract demonstrated STEAM competencies from completed projects"""
        
        competencies = {
            'Science': set(),
            'Technology': set(), 
            'Engineering': set(),
            'Arts': set(),
            'Mathematics': set()
        }
        
        for instance in instances:
            project = self.projects[instance.project_id]
            for steam_area, skills in project.steam_components.items():
                if steam_area in competencies:
                    competencies[steam_area].update(skills)
        
        return {area: list(skills) for area, skills in competencies.items()}

# Example usage and testing
if __name__ == "__main__":
    # Initialize the learning instance manager
    manager = LearningInstanceManager()
    
    # Create a sample learner
    user_id = manager.create_learner_profile(
        name="Alex Student",
        age=14,
        learning_style=LearningStyle.VISUAL,
        multiple_intelligences=[MultipleIntelligence.LOGICAL_MATHEMATICAL, MultipleIntelligence.SPATIAL],
        interests=["robotics", "environmental science", "programming"]
    )
    
    # Generate a personalized project
    project_id = manager.generate_personalized_project(
        user_id=user_id,
        theme="Environmental Sustainability",
        frameworks=[EducationalFramework.NGSS, EducationalFramework.ISTE, EducationalFramework.PBL]
    )
    
    # Create and start a learning instance
    instance_id = manager.create_learning_instance(user_id, project_id)
    start_result = manager.start_learning_instance(instance_id)
    
    print(f"Created learning instance: {instance_id}")
    print(f"First activity: {start_result['first_activity']['title']}")
    print(f"Applied {len(start_result['adaptations'])} personalized adaptations")
    
    # Simulate some progress
    progress_result = manager.update_learning_progress(
        instance_id=instance_id,
        activity_completed=start_result['first_activity']['activity_id'],
        time_spent=25,
        engagement_score=4.2,
        artifacts=["initial_research_notes.pdf"]
    )
    
    print(f"Progress updated: {progress_result['progress_percentage']}% complete")
    
    # Get recommendations
    recommendations = manager.get_personalized_recommendations(user_id)
    print(f"Recommended themes: {[r['theme'] for r in recommendations['suggested_themes'][:3]]}")
    
    # Get analytics
    analytics = manager.get_learning_analytics(user_id)
    print(f"Learning analytics generated for {analytics['learning_summary']['total_projects']} projects")