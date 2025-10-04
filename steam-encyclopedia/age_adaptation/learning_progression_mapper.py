"""
Learning Progression Mapper
Maps learning progressions and prerequisite relationships across age groups
"""

from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime
import networkx as nx
import asyncio

from agents.base_agent import ContentItem, AgeGroup


class ProgressionType(Enum):
    """Types of learning progressions."""
    SEQUENTIAL = "sequential"        # Must learn A before B
    HIERARCHICAL = "hierarchical"    # Lower level concepts support higher level
    SPIRAL = "spiral"               # Concepts revisited at deeper levels
    BRANCHING = "branching"         # Multiple paths to same concept
    PARALLEL = "parallel"           # Can be learned simultaneously


class MasteryLevel(Enum):
    """Levels of concept mastery."""
    AWARENESS = "awareness"          # Basic recognition
    UNDERSTANDING = "understanding"  # Comprehends relationships
    APPLICATION = "application"      # Can use in new contexts
    ANALYSIS = "analysis"           # Can break down and examine
    SYNTHESIS = "synthesis"         # Can combine with other concepts
    EVALUATION = "evaluation"       # Can judge and critique


@dataclass
class ConceptNode:
    """Represents a learning concept in the progression map."""
    concept_id: str
    name: str
    description: str
    domain: str
    
    # Age group mappings
    age_introductions: Dict[AgeGroup, MasteryLevel] = field(default_factory=dict)
    age_prerequisites: Dict[AgeGroup, List[str]] = field(default_factory=dict)
    
    # Learning characteristics
    difficulty_level: float = 0.0  # 0-100 scale
    abstract_level: float = 0.0    # 0-100 scale
    time_to_master: int = 0        # Hours of instruction
    
    # Content associations
    related_content: List[str] = field(default_factory=list)
    example_activities: Dict[AgeGroup, List[str]] = field(default_factory=dict)
    
    # Assessment information
    assessment_methods: Dict[AgeGroup, List[str]] = field(default_factory=dict)
    common_misconceptions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept_id": self.concept_id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "age_introductions": {age.value: level.value for age, level in self.age_introductions.items()},
            "age_prerequisites": {age.value: prereqs for age, prereqs in self.age_prerequisites.items()},
            "difficulty_level": self.difficulty_level,
            "abstract_level": self.abstract_level,
            "time_to_master": self.time_to_master,
            "related_content": self.related_content,
            "example_activities": {age.value: activities for age, activities in self.example_activities.items()},
            "assessment_methods": {age.value: methods for age, methods in self.assessment_methods.items()},
            "common_misconceptions": self.common_misconceptions
        }


@dataclass
class LearningProgression:
    """Represents a learning progression pathway."""
    progression_id: str
    name: str
    description: str
    domain: str
    progression_type: ProgressionType
    
    # Concept sequence
    concept_sequence: List[str] = field(default_factory=list)
    concept_relationships: Dict[str, List[str]] = field(default_factory=dict)  # concept_id -> prerequisites
    
    # Age group mappings
    age_pathways: Dict[AgeGroup, List[str]] = field(default_factory=dict)
    milestone_concepts: Dict[AgeGroup, List[str]] = field(default_factory=dict)
    
    # Progression characteristics
    total_duration: Dict[AgeGroup, int] = field(default_factory=dict)  # Hours
    complexity_curve: List[float] = field(default_factory=list)  # Difficulty progression
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "progression_id": self.progression_id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "progression_type": self.progression_type.value,
            "concept_sequence": self.concept_sequence,
            "concept_relationships": self.concept_relationships,
            "age_pathways": {age.value: pathway for age, pathway in self.age_pathways.items()},
            "milestone_concepts": {age.value: milestones for age, milestones in self.milestone_concepts.items()},
            "total_duration": {age.value: duration for age, duration in self.total_duration.items()},
            "complexity_curve": self.complexity_curve
        }


class LearningProgressionMapper:
    """Maps learning progressions and manages prerequisite relationships."""
    
    def __init__(self):
        self.concept_graph = nx.DiGraph()  # Directed graph for prerequisites
        self.concepts: Dict[str, ConceptNode] = {}
        self.progressions: Dict[str, LearningProgression] = {}
        
        # Initialize with core STEAM concepts
        self._initialize_core_concepts()
        self._initialize_core_progressions()
    
    def _initialize_core_concepts(self):
        """Initialize core STEAM concepts with age-appropriate progressions."""
        
        # Science concepts
        science_concepts = [
            ConceptNode(
                concept_id="observation",
                name="Scientific Observation",
                description="Using senses to gather information about the world",
                domain="science",
                age_introductions={
                    AgeGroup.EARLY_YEARS: MasteryLevel.AWARENESS,
                    AgeGroup.ELEMENTARY: MasteryLevel.UNDERSTANDING,
                    AgeGroup.MIDDLE_SCHOOL: MasteryLevel.APPLICATION,
                    AgeGroup.HIGH_SCHOOL: MasteryLevel.ANALYSIS,
                    AgeGroup.HIGHER_ED: MasteryLevel.SYNTHESIS
                },
                difficulty_level=10.0,
                abstract_level=5.0,
                time_to_master=5,
                example_activities={
                    AgeGroup.EARLY_YEARS: ["Look at flowers", "Touch different textures"],
                    AgeGroup.ELEMENTARY: ["Record weather daily", "Compare plant growth"],
                    AgeGroup.MIDDLE_SCHOOL: ["Systematic observation protocols", "Data collection methods"]
                },
                common_misconceptions=["Observation is just looking", "Personal opinions are observations"]
            ),
            
            ConceptNode(
                concept_id="hypothesis",
                name="Hypothesis Formation",
                description="Making educated guesses based on observations",
                domain="science",
                age_introductions={
                    AgeGroup.ELEMENTARY: MasteryLevel.AWARENESS,
                    AgeGroup.MIDDLE_SCHOOL: MasteryLevel.UNDERSTANDING,
                    AgeGroup.HIGH_SCHOOL: MasteryLevel.APPLICATION,
                    AgeGroup.HIGHER_ED: MasteryLevel.ANALYSIS
                },
                age_prerequisites={
                    AgeGroup.ELEMENTARY: ["observation"],
                    AgeGroup.MIDDLE_SCHOOL: ["observation", "patterns"],
                    AgeGroup.HIGH_SCHOOL: ["observation", "patterns", "variables"]
                },
                difficulty_level=30.0,
                abstract_level=40.0,
                time_to_master=10,
                common_misconceptions=["Hypothesis must be proven right", "Guessing is the same as hypothesizing"]
            ),
            
            ConceptNode(
                concept_id="experimentation",
                name="Scientific Experimentation",
                description="Testing hypotheses through controlled procedures",
                domain="science",
                age_introductions={
                    AgeGroup.ELEMENTARY: MasteryLevel.AWARENESS,
                    AgeGroup.MIDDLE_SCHOOL: MasteryLevel.UNDERSTANDING,
                    AgeGroup.HIGH_SCHOOL: MasteryLevel.APPLICATION,
                    AgeGroup.HIGHER_ED: MasteryLevel.SYNTHESIS
                },
                age_prerequisites={
                    AgeGroup.ELEMENTARY: ["observation"],
                    AgeGroup.MIDDLE_SCHOOL: ["observation", "hypothesis"],
                    AgeGroup.HIGH_SCHOOL: ["observation", "hypothesis", "variables", "controls"]
                },
                difficulty_level=50.0,
                abstract_level=30.0,
                time_to_master=20
            ),
            
            ConceptNode(
                concept_id="matter_states",
                name="States of Matter",
                description="Different forms matter can take: solid, liquid, gas",
                domain="science",
                age_introductions={
                    AgeGroup.EARLY_YEARS: MasteryLevel.AWARENESS,
                    AgeGroup.ELEMENTARY: MasteryLevel.UNDERSTANDING,
                    AgeGroup.MIDDLE_SCHOOL: MasteryLevel.APPLICATION,
                    AgeGroup.HIGH_SCHOOL: MasteryLevel.ANALYSIS
                },
                difficulty_level=20.0,
                abstract_level=15.0,
                time_to_master=8,
                example_activities={
                    AgeGroup.EARLY_YEARS: ["Ice melting", "Water freezing"],
                    AgeGroup.ELEMENTARY: ["States of water cycle", "Classify materials"],
                    AgeGroup.MIDDLE_SCHOOL: ["Particle models", "Phase transitions"]
                }
            )
        ]
        
        # Technology concepts
        technology_concepts = [
            ConceptNode(
                concept_id="algorithm_basics",
                name="Basic Algorithms",
                description="Step-by-step instructions to solve problems",
                domain="technology",
                age_introductions={
                    AgeGroup.ELEMENTARY: MasteryLevel.AWARENESS,
                    AgeGroup.MIDDLE_SCHOOL: MasteryLevel.UNDERSTANDING,
                    AgeGroup.HIGH_SCHOOL: MasteryLevel.APPLICATION,
                    AgeGroup.HIGHER_ED: MasteryLevel.ANALYSIS
                },
                difficulty_level=25.0,
                abstract_level=35.0,
                time_to_master=15,
                example_activities={
                    AgeGroup.ELEMENTARY: ["Recipe following", "Game rules"],
                    AgeGroup.MIDDLE_SCHOOL: ["Flowcharts", "Pseudocode"],
                    AgeGroup.HIGH_SCHOOL: ["Programming basics", "Algorithm design"]
                }
            ),
            
            ConceptNode(
                concept_id="data_representation",
                name="Data Representation",
                description="How information is stored and represented digitally",
                domain="technology",
                age_introductions={
                    AgeGroup.MIDDLE_SCHOOL: MasteryLevel.AWARENESS,
                    AgeGroup.HIGH_SCHOOL: MasteryLevel.UNDERSTANDING,
                    AgeGroup.HIGHER_ED: MasteryLevel.APPLICATION
                },
                age_prerequisites={
                    AgeGroup.MIDDLE_SCHOOL: ["number_systems"],
                    AgeGroup.HIGH_SCHOOL: ["number_systems", "algorithm_basics"],
                    AgeGroup.HIGHER_ED: ["number_systems", "algorithm_basics", "data_structures"]
                },
                difficulty_level=45.0,
                abstract_level=60.0,
                time_to_master=25
            )
        ]
        
        # Engineering concepts
        engineering_concepts = [
            ConceptNode(
                concept_id="design_process",
                name="Engineering Design Process",
                description="Systematic approach to solving engineering problems",
                domain="engineering",
                age_introductions={
                    AgeGroup.ELEMENTARY: MasteryLevel.AWARENESS,
                    AgeGroup.MIDDLE_SCHOOL: MasteryLevel.UNDERSTANDING,
                    AgeGroup.HIGH_SCHOOL: MasteryLevel.APPLICATION,
                    AgeGroup.HIGHER_ED: MasteryLevel.SYNTHESIS
                },
                difficulty_level=30.0,
                abstract_level=25.0,
                time_to_master=20,
                example_activities={
                    AgeGroup.ELEMENTARY: ["Build a bridge with blocks", "Design a paper airplane"],
                    AgeGroup.MIDDLE_SCHOOL: ["Prototype testing", "Iterative design"],
                    AgeGroup.HIGH_SCHOOL: ["CAD modeling", "Systems analysis"]
                }
            ),
            
            ConceptNode(
                concept_id="structures_forces",
                name="Structures and Forces",
                description="How forces affect structures and materials",
                domain="engineering",
                age_introductions={
                    AgeGroup.ELEMENTARY: MasteryLevel.AWARENESS,
                    AgeGroup.MIDDLE_SCHOOL: MasteryLevel.UNDERSTANDING,
                    AgeGroup.HIGH_SCHOOL: MasteryLevel.APPLICATION,
                    AgeGroup.HIGHER_ED: MasteryLevel.ANALYSIS
                },
                age_prerequisites={
                    AgeGroup.MIDDLE_SCHOOL: ["forces"],
                    AgeGroup.HIGH_SCHOOL: ["forces", "materials"],
                    AgeGroup.HIGHER_ED: ["forces", "materials", "statics"]
                },
                difficulty_level=40.0,
                abstract_level=30.0,
                time_to_master=30
            )
        ]
        
        # Mathematics concepts
        math_concepts = [
            ConceptNode(
                concept_id="number_sense",
                name="Number Sense",
                description="Understanding numbers and their relationships",
                domain="mathematics",
                age_introductions={
                    AgeGroup.EARLY_YEARS: MasteryLevel.AWARENESS,
                    AgeGroup.ELEMENTARY: MasteryLevel.UNDERSTANDING,
                    AgeGroup.MIDDLE_SCHOOL: MasteryLevel.APPLICATION
                },
                difficulty_level=15.0,
                abstract_level=10.0,
                time_to_master=40,
                example_activities={
                    AgeGroup.EARLY_YEARS: ["Counting objects", "More/less comparisons"],
                    AgeGroup.ELEMENTARY: ["Place value", "Number patterns"],
                    AgeGroup.MIDDLE_SCHOOL: ["Rational numbers", "Number theory"]
                }
            ),
            
            ConceptNode(
                concept_id="algebraic_thinking",
                name="Algebraic Thinking",
                description="Using symbols and relationships to represent mathematical ideas",
                domain="mathematics",
                age_introductions={
                    AgeGroup.ELEMENTARY: MasteryLevel.AWARENESS,
                    AgeGroup.MIDDLE_SCHOOL: MasteryLevel.UNDERSTANDING,
                    AgeGroup.HIGH_SCHOOL: MasteryLevel.APPLICATION,
                    AgeGroup.HIGHER_ED: MasteryLevel.ANALYSIS
                },
                age_prerequisites={
                    AgeGroup.ELEMENTARY: ["number_sense", "patterns"],
                    AgeGroup.MIDDLE_SCHOOL: ["number_sense", "patterns", "operations"],
                    AgeGroup.HIGH_SCHOOL: ["number_sense", "patterns", "operations", "equations"]
                },
                difficulty_level=50.0,
                abstract_level=70.0,
                time_to_master=60
            )
        ]
        
        # Arts concepts
        arts_concepts = [
            ConceptNode(
                concept_id="visual_elements",
                name="Visual Elements",
                description="Basic elements of visual art: line, shape, color, texture",
                domain="arts",
                age_introductions={
                    AgeGroup.EARLY_YEARS: MasteryLevel.AWARENESS,
                    AgeGroup.ELEMENTARY: MasteryLevel.UNDERSTANDING,
                    AgeGroup.MIDDLE_SCHOOL: MasteryLevel.APPLICATION,
                    AgeGroup.HIGH_SCHOOL: MasteryLevel.ANALYSIS
                },
                difficulty_level=10.0,
                abstract_level=20.0,
                time_to_master=15,
                example_activities={
                    AgeGroup.EARLY_YEARS: ["Finger painting", "Shape recognition"],
                    AgeGroup.ELEMENTARY: ["Color mixing", "Texture exploration"],
                    AgeGroup.MIDDLE_SCHOOL: ["Composition principles", "Visual analysis"]
                }
            ),
            
            ConceptNode(
                concept_id="creative_expression",
                name="Creative Expression",
                description="Using artistic mediums to communicate ideas and emotions",
                domain="arts",
                age_introductions={
                    AgeGroup.EARLY_YEARS: MasteryLevel.AWARENESS,
                    AgeGroup.ELEMENTARY: MasteryLevel.UNDERSTANDING,
                    AgeGroup.MIDDLE_SCHOOL: MasteryLevel.APPLICATION,
                    AgeGroup.HIGH_SCHOOL: MasteryLevel.SYNTHESIS,
                    AgeGroup.HIGHER_ED: MasteryLevel.EVALUATION
                },
                age_prerequisites={
                    AgeGroup.ELEMENTARY: ["visual_elements"],
                    AgeGroup.MIDDLE_SCHOOL: ["visual_elements", "techniques"],
                    AgeGroup.HIGH_SCHOOL: ["visual_elements", "techniques", "art_history"]
                },
                difficulty_level=35.0,
                abstract_level=80.0,
                time_to_master=50
            )
        ]
        
        # Add all concepts to the mapper
        all_concepts = science_concepts + technology_concepts + engineering_concepts + math_concepts + arts_concepts
        
        for concept in all_concepts:
            self.add_concept(concept)
    
    def _initialize_core_progressions(self):
        """Initialize core learning progressions."""
        
        # Scientific Method Progression
        scientific_method = LearningProgression(
            progression_id="scientific_method",
            name="Scientific Method",
            description="Progressive development of scientific thinking and methodology",
            domain="science",
            progression_type=ProgressionType.SEQUENTIAL,
            concept_sequence=["observation", "patterns", "hypothesis", "experimentation", "analysis", "conclusion"],
            age_pathways={
                AgeGroup.EARLY_YEARS: ["observation"],
                AgeGroup.ELEMENTARY: ["observation", "patterns", "hypothesis"],
                AgeGroup.MIDDLE_SCHOOL: ["observation", "patterns", "hypothesis", "experimentation"],
                AgeGroup.HIGH_SCHOOL: ["observation", "patterns", "hypothesis", "experimentation", "analysis"],
                AgeGroup.HIGHER_ED: ["observation", "patterns", "hypothesis", "experimentation", "analysis", "conclusion"]
            },
            milestone_concepts={
                AgeGroup.EARLY_YEARS: ["observation"],
                AgeGroup.ELEMENTARY: ["hypothesis"],
                AgeGroup.MIDDLE_SCHOOL: ["experimentation"],
                AgeGroup.HIGH_SCHOOL: ["analysis"],
                AgeGroup.HIGHER_ED: ["conclusion"]
            },
            total_duration={
                AgeGroup.EARLY_YEARS: 10,
                AgeGroup.ELEMENTARY: 30,
                AgeGroup.MIDDLE_SCHOOL: 60,
                AgeGroup.HIGH_SCHOOL: 100,
                AgeGroup.HIGHER_ED: 150
            },
            complexity_curve=[10, 20, 35, 50, 70, 85]
        )
        
        # Mathematical Reasoning Progression
        math_reasoning = LearningProgression(
            progression_id="mathematical_reasoning",
            name="Mathematical Reasoning",
            description="Development of mathematical thinking from concrete to abstract",
            domain="mathematics",
            progression_type=ProgressionType.SPIRAL,
            concept_sequence=["number_sense", "patterns", "operations", "algebraic_thinking", "functions", "calculus"],
            age_pathways={
                AgeGroup.EARLY_YEARS: ["number_sense"],
                AgeGroup.ELEMENTARY: ["number_sense", "patterns", "operations"],
                AgeGroup.MIDDLE_SCHOOL: ["number_sense", "patterns", "operations", "algebraic_thinking"],
                AgeGroup.HIGH_SCHOOL: ["algebraic_thinking", "functions", "geometry", "statistics"],
                AgeGroup.HIGHER_ED: ["functions", "calculus", "linear_algebra", "differential_equations"]
            },
            milestone_concepts={
                AgeGroup.EARLY_YEARS: ["number_sense"],
                AgeGroup.ELEMENTARY: ["operations"],
                AgeGroup.MIDDLE_SCHOOL: ["algebraic_thinking"],
                AgeGroup.HIGH_SCHOOL: ["functions"],
                AgeGroup.HIGHER_ED: ["calculus"]
            }
        )
        
        # Design Thinking Progression
        design_thinking = LearningProgression(
            progression_id="design_thinking",
            name="Design Thinking",
            description="Progressive development of design and problem-solving skills",
            domain="engineering",
            progression_type=ProgressionType.HIERARCHICAL,
            concept_sequence=["problem_identification", "ideation", "prototyping", "testing", "iteration", "optimization"],
            age_pathways={
                AgeGroup.ELEMENTARY: ["problem_identification", "ideation"],
                AgeGroup.MIDDLE_SCHOOL: ["problem_identification", "ideation", "prototyping"],
                AgeGroup.HIGH_SCHOOL: ["ideation", "prototyping", "testing", "iteration"],
                AgeGroup.HIGHER_ED: ["prototyping", "testing", "iteration", "optimization"]
            }
        )
        
        # Add progressions
        self.add_progression(scientific_method)
        self.add_progression(math_reasoning)
        self.add_progression(design_thinking)
    
    def add_concept(self, concept: ConceptNode):
        """Add a concept to the progression mapper."""
        self.concepts[concept.concept_id] = concept
        self.concept_graph.add_node(concept.concept_id, **concept.to_dict())
        
        # Add prerequisite edges
        for age_group, prerequisites in concept.age_prerequisites.items():
            for prereq in prerequisites:
                if prereq in self.concepts:
                    self.concept_graph.add_edge(prereq, concept.concept_id, age_group=age_group.value)
    
    def add_progression(self, progression: LearningProgression):
        """Add a learning progression."""
        self.progressions[progression.progression_id] = progression
        
        # Add concept relationships to graph
        for concept_id, prerequisites in progression.concept_relationships.items():
            for prereq in prerequisites:
                if concept_id in self.concepts and prereq in self.concepts:
                    self.concept_graph.add_edge(prereq, concept_id, progression=progression.progression_id)
    
    def get_prerequisites(self, concept_id: str, age_group: AgeGroup) -> List[str]:
        """Get prerequisites for a concept at a specific age group."""
        if concept_id not in self.concepts:
            return []
        
        concept = self.concepts[concept_id]
        age_prerequisites = concept.age_prerequisites.get(age_group, [])
        
        # Also get graph-based prerequisites
        graph_prerequisites = list(self.concept_graph.predecessors(concept_id))
        
        # Combine and deduplicate
        all_prerequisites = list(set(age_prerequisites + graph_prerequisites))
        
        return all_prerequisites
    
    def get_learning_path(self, target_concept: str, age_group: AgeGroup) -> List[str]:
        """Get an optimal learning path to reach a target concept."""
        if target_concept not in self.concepts:
            return []
        
        # Find all paths from concepts with no prerequisites to target
        source_concepts = [node for node in self.concept_graph.nodes() 
                          if self.concept_graph.in_degree(node) == 0]
        
        paths = []
        for source in source_concepts:
            try:
                if nx.has_path(self.concept_graph, source, target_concept):
                    path = nx.shortest_path(self.concept_graph, source, target_concept)
                    paths.append(path)
            except nx.NetworkXNoPath:
                continue
        
        if not paths:
            return [target_concept]
        
        # Choose the path with concepts most appropriate for age group
        best_path = min(paths, key=lambda p: self._calculate_path_difficulty(p, age_group))
        
        return best_path
    
    def _calculate_path_difficulty(self, path: List[str], age_group: AgeGroup) -> float:
        """Calculate the difficulty of a learning path for an age group."""
        total_difficulty = 0.0
        
        for concept_id in path:
            if concept_id in self.concepts:
                concept = self.concepts[concept_id]
                
                # Check if concept is introduced at this age group
                if age_group in concept.age_introductions:
                    mastery_level = concept.age_introductions[age_group]
                    
                    # Weight by mastery level complexity
                    mastery_weights = {
                        MasteryLevel.AWARENESS: 1.0,
                        MasteryLevel.UNDERSTANDING: 2.0,
                        MasteryLevel.APPLICATION: 3.0,
                        MasteryLevel.ANALYSIS: 4.0,
                        MasteryLevel.SYNTHESIS: 5.0,
                        MasteryLevel.EVALUATION: 6.0
                    }
                    
                    difficulty = concept.difficulty_level * mastery_weights.get(mastery_level, 1.0)
                    total_difficulty += difficulty
                else:
                    # Penalize concepts not appropriate for age group
                    total_difficulty += 1000
        
        return total_difficulty
    
    def suggest_next_concepts(self, mastered_concepts: List[str], age_group: AgeGroup) -> List[str]:
        """Suggest next concepts to learn based on mastered concepts."""
        suggestions = []
        
        for concept_id, concept in self.concepts.items():
            if concept_id in mastered_concepts:
                continue
            
            # Check if prerequisites are met
            prerequisites = self.get_prerequisites(concept_id, age_group)
            if all(prereq in mastered_concepts for prereq in prerequisites):
                # Check if concept is appropriate for age group
                if age_group in concept.age_introductions:
                    suggestions.append(concept_id)
        
        # Sort by difficulty and appropriateness
        suggestions.sort(key=lambda cid: (
            self.concepts[cid].difficulty_level,
            self.concepts[cid].abstract_level
        ))
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def assess_readiness(self, concept_id: str, mastered_concepts: List[str], age_group: AgeGroup) -> Dict[str, Any]:
        """Assess readiness to learn a specific concept."""
        if concept_id not in self.concepts:
            return {"ready": False, "reason": "Concept not found"}
        
        concept = self.concepts[concept_id]
        
        # Check age appropriateness
        if age_group not in concept.age_introductions:
            return {
                "ready": False,
                "reason": "Concept not age-appropriate",
                "suggested_age": min(concept.age_introductions.keys(), key=lambda x: x.value)
            }
        
        # Check prerequisites
        prerequisites = self.get_prerequisites(concept_id, age_group)
        missing_prerequisites = [p for p in prerequisites if p not in mastered_concepts]
        
        if missing_prerequisites:
            return {
                "ready": False,
                "reason": "Missing prerequisites",
                "missing_prerequisites": missing_prerequisites,
                "suggested_path": self.get_learning_path(concept_id, age_group)
            }
        
        # Calculate readiness score
        readiness_score = self._calculate_readiness_score(concept, mastered_concepts, age_group)
        
        return {
            "ready": True,
            "readiness_score": readiness_score,
            "mastery_level": concept.age_introductions[age_group],
            "estimated_time": concept.time_to_master,
            "recommended_activities": concept.example_activities.get(age_group, [])
        }
    
    def _calculate_readiness_score(self, concept: ConceptNode, mastered_concepts: List[str], age_group: AgeGroup) -> float:
        """Calculate a readiness score (0-100) for learning a concept."""
        score = 50.0  # Base score
        
        # Bonus for having more related concepts mastered
        related_mastered = len([c for c in concept.related_content if c in mastered_concepts])
        if concept.related_content:
            score += 30 * (related_mastered / len(concept.related_content))
        
        # Adjust for age appropriateness
        if age_group in concept.age_introductions:
            mastery_level = concept.age_introductions[age_group]
            if mastery_level == MasteryLevel.AWARENESS:
                score += 20  # Easy to start
            elif mastery_level in [MasteryLevel.UNDERSTANDING, MasteryLevel.APPLICATION]:
                score += 10  # Moderate difficulty
            # No penalty for higher levels - they're appropriately challenging
        
        # Adjust for concept characteristics
        if concept.abstract_level > 60:
            score -= 10  # More challenging for younger learners
        
        return max(0.0, min(100.0, score))
    
    def get_progression_status(self, progression_id: str, mastered_concepts: List[str], age_group: AgeGroup) -> Dict[str, Any]:
        """Get status of progress through a learning progression."""
        if progression_id not in self.progressions:
            return {"error": "Progression not found"}
        
        progression = self.progressions[progression_id]
        age_pathway = progression.age_pathways.get(age_group, progression.concept_sequence)
        
        # Calculate completion
        completed_concepts = [c for c in age_pathway if c in mastered_concepts]
        completion_ratio = len(completed_concepts) / len(age_pathway) if age_pathway else 0
        
        # Find current position
        current_position = 0
        for i, concept in enumerate(age_pathway):
            if concept in mastered_concepts:
                current_position = i + 1
            else:
                break
        
        # Identify next milestone
        milestones = progression.milestone_concepts.get(age_group, [])
        next_milestone = None
        for milestone in milestones:
            if milestone not in mastered_concepts:
                next_milestone = milestone
                break
        
        return {
            "progression_name": progression.name,
            "completion_ratio": completion_ratio,
            "completed_concepts": completed_concepts,
            "current_position": current_position,
            "total_concepts": len(age_pathway),
            "next_concept": age_pathway[current_position] if current_position < len(age_pathway) else None,
            "next_milestone": next_milestone,
            "estimated_remaining_time": self._estimate_remaining_time(progression, current_position, age_group)
        }
    
    def _estimate_remaining_time(self, progression: LearningProgression, current_position: int, age_group: AgeGroup) -> int:
        """Estimate remaining time to complete progression."""
        total_duration = progression.total_duration.get(age_group, 0)
        if not total_duration:
            return 0
        
        age_pathway = progression.age_pathways.get(age_group, progression.concept_sequence)
        if not age_pathway:
            return 0
        
        completion_ratio = current_position / len(age_pathway)
        remaining_ratio = 1.0 - completion_ratio
        
        return int(total_duration * remaining_ratio)
    
    def export_concept_map(self, format_type: str = "json") -> str:
        """Export the concept map in various formats."""
        if format_type == "json":
            data = {
                "concepts": {cid: concept.to_dict() for cid, concept in self.concepts.items()},
                "progressions": {pid: progression.to_dict() for pid, progression in self.progressions.items()},
                "graph_edges": list(self.concept_graph.edges(data=True))
            }
            return json.dumps(data, indent=2, default=str)
        
        elif format_type == "graphml":
            # Export as GraphML for visualization
            return "\n".join(nx.generate_graphml(self.concept_graph))
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def import_concept_map(self, data: str, format_type: str = "json"):
        """Import concept map from various formats."""
        if format_type == "json":
            imported_data = json.loads(data)
            
            # Import concepts
            for concept_data in imported_data.get("concepts", {}).values():
                concept = ConceptNode(**concept_data)
                self.add_concept(concept)
            
            # Import progressions
            for progression_data in imported_data.get("progressions", {}).values():
                progression = LearningProgression(**progression_data)
                self.add_progression(progression)
    
    async def analyze_learning_gaps(self, mastered_concepts: List[str], target_concepts: List[str], age_group: AgeGroup) -> Dict[str, Any]:
        """Analyze learning gaps between current knowledge and targets."""
        gaps = {}
        
        for target in target_concepts:
            if target not in mastered_concepts:
                path = self.get_learning_path(target, age_group)
                missing_in_path = [c for c in path if c not in mastered_concepts]
                
                gaps[target] = {
                    "learning_path": path,
                    "missing_concepts": missing_in_path,
                    "estimated_time": sum(
                        self.concepts[c].time_to_master for c in missing_in_path 
                        if c in self.concepts
                    ),
                    "difficulty_level": max(
                        self.concepts[c].difficulty_level for c in missing_in_path 
                        if c in self.concepts
                    ) if missing_in_path else 0
                }
        
        return {
            "gaps": gaps,
            "total_missing_concepts": sum(len(gap["missing_concepts"]) for gap in gaps.values()),
            "total_estimated_time": sum(gap["estimated_time"] for gap in gaps.values()),
            "recommended_order": sorted(gaps.keys(), key=lambda t: gaps[t]["difficulty_level"])
        }


# Example usage and testing
def main():
    """Example usage of the learning progression mapper."""
    mapper = LearningProgressionMapper()
    
    # Example: Student has mastered basic concepts
    mastered = ["observation", "number_sense", "visual_elements"]
    age = AgeGroup.ELEMENTARY
    
    print("=== Learning Progression Mapper Demo ===")
    
    # Get suggestions for next concepts
    suggestions = mapper.suggest_next_concepts(mastered, age)
    print(f"\nSuggested next concepts for {age.value}:")
    for suggestion in suggestions:
        concept = mapper.concepts[suggestion]
        print(f"- {concept.name}: {concept.description}")
    
    # Check readiness for a specific concept
    readiness = mapper.assess_readiness("hypothesis", mastered, age)
    print(f"\nReadiness for 'hypothesis': {readiness}")
    
    # Get learning path
    path = mapper.get_learning_path("experimentation", age)
    print(f"\nLearning path to 'experimentation': {path}")
    
    # Check progression status
    status = mapper.get_progression_status("scientific_method", mastered, age)
    print(f"\nScientific method progression status: {status}")


if __name__ == "__main__":
    main()