"""
Engineer Agents for STEAM Encyclopedia Editorial Board
Specialized in practical applications, innovation, and real-world problem solving
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from .base_agent import BaseAgent, AgentRole, ContentItem, ContentType, AgeGroup, ReviewFeedback


class MechanicalEngineeringAgent(BaseAgent):
    """Specialist in machines, robotics, manufacturing, and mechanical systems."""
    
    def __init__(self):
        super().__init__(
            agent_id="mech_engineer_001",
            role=AgentRole.ENGINEER,
            domains=["mechanical_engineering", "robotics", "manufacturing", "materials"],
            specializations=["automation", "thermodynamics", "fluid_mechanics", "design"]
        )
        
        self.mechanical_concepts = [
            "gear", "lever", "pulley", "wheel", "axle", "screw", "inclined_plane",
            "force", "torque", "friction", "stress", "strain", "fatigue",
            "kinematics", "dynamics", "thermodynamics"
        ]
        
        self.engineering_processes = [
            "design", "prototype", "testing", "manufacturing", "quality_control",
            "optimization", "maintenance", "troubleshooting"
        ]
    
    async def analyze_content(self, source_data: Dict[str, Any]) -> ContentItem:
        """Analyze engineering content focusing on practical applications."""
        title = source_data.get("title", "Untitled Engineering Concept")
        content = source_data.get("content", "")
        
        # Identify mechanical concepts and processes
        identified_concepts = [c for c in self.mechanical_concepts if c.lower() in content.lower()]
        identified_processes = [p for p in self.engineering_processes if p.lower() in content.lower()]
        
        # Determine content type based on engineering context
        content_type = ContentType.APPLICATION
        if any(word in content.lower() for word in ["theory", "principle", "law"]):
            content_type = ContentType.THEORY
        elif any(word in content.lower() for word in ["invention", "innovation", "breakthrough"]):
            content_type = ContentType.INNOVATION
        
        # Structure engineering content with practical focus
        structured_content = await self._structure_engineering_content(
            content, identified_concepts, identified_processes
        )
        
        return ContentItem(
            id=self.generate_content_id(title, "mechanical_engineering"),
            title=title,
            content=structured_content,
            content_type=content_type,
            domain="mechanical_engineering",
            age_groups=[AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
            sources=source_data.get("sources", []),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1,
            tags=identified_concepts + identified_processes + ["engineering", "mechanical"],
            prerequisites=self._identify_engineering_prerequisites(content),
            related_concepts=self._find_engineering_related_concepts(content),
            multimedia_assets=["diagrams", "animations", "3d_models"]  # Engineering benefits from visuals
        )
    
    async def _structure_engineering_content(self, content: str, concepts: List[str], 
                                           processes: List[str]) -> str:
        """Structure engineering content with emphasis on practical applications."""
        return f"""
## Engineering Overview
{content[:250]}...

## Key Mechanical Concepts
{chr(10).join(f'- **{concept.title()}**: Fundamental principle in mechanical systems' for concept in concepts[:5])}

## Engineering Process
{chr(10).join(f'- {process.title()}' for process in processes)}

## Real-World Applications
This engineering concept is used in:
- Industrial machinery and equipment
- Consumer products and devices
- Transportation systems
- Manufacturing processes

## Design Considerations
- Safety requirements and standards
- Cost-effectiveness and efficiency
- Environmental impact
- Maintenance and reliability

## Hands-On Activities
- Build simple machines using everyday materials
- Design challenges and problem-solving exercises
- Computer simulations and modeling
        """.strip()
    
    async def review_content(self, content: ContentItem) -> ReviewFeedback:
        """Review engineering content for practical accuracy and safety."""
        # Engineering content must be practically applicable and safe
        accuracy_score = self._assess_technical_accuracy(content)
        safety_score = self._assess_safety_considerations(content)
        practicality_score = self._assess_practical_applicability(content)
        
        suggestions = []
        if safety_score < 0.7:
            suggestions.append("Include more comprehensive safety guidelines")
        if "design" in content.content.lower() and "constraint" not in content.content.lower():
            suggestions.append("Add information about design constraints and limitations")
        if practicality_score < 0.6:
            suggestions.append("Include more real-world examples and applications")
        
        overall_score = (accuracy_score + safety_score + practicality_score) / 3
        
        return ReviewFeedback(
            agent_id=self.agent_id,
            agent_role=self.role,
            content_id=content.id,
            accuracy_score=accuracy_score,
            clarity_score=0.85,
            age_appropriateness_score=self._assess_age_appropriateness_engineering(content),
            completeness_score=practicality_score,
            suggestions=suggestions,
            approved=overall_score > 0.75 and safety_score > 0.6,
            timestamp=datetime.now()
        )
    
    async def adapt_for_age_group(self, content: ContentItem, target_age: AgeGroup) -> ContentItem:
        """Adapt engineering content with age-appropriate complexity and safety."""
        if target_age == AgeGroup.EARLY_YEARS:
            adapted_content = self._create_early_years_engineering(content)
        elif target_age == AgeGroup.ELEMENTARY:
            adapted_content = self._create_elementary_engineering(content)
        elif target_age == AgeGroup.MIDDLE_SCHOOL:
            adapted_content = self._create_middle_school_engineering(content)
        elif target_age == AgeGroup.HIGH_SCHOOL:
            adapted_content = self._create_high_school_engineering(content)
        else:  # HIGHER_ED
            adapted_content = content.content
        
        return ContentItem(
            id=f"{content.id}_{target_age.value}",
            title=content.title,
            content=adapted_content,
            content_type=content.content_type,
            domain=content.domain,
            age_groups=[target_age],
            sources=content.sources,
            created_at=content.created_at,
            updated_at=datetime.now(),
            version=content.version,
            tags=content.tags,
            prerequisites=self._adapt_engineering_prerequisites(content.prerequisites, target_age),
            related_concepts=content.related_concepts,
            multimedia_assets=self._adapt_multimedia_for_age(content.multimedia_assets, target_age)
        )
    
    def _create_early_years_engineering(self, content: ContentItem) -> str:
        """Create engineering content for ages 1-5."""
        return """
## Simple Machines Around Us!

### What are Simple Machines?
Simple machines help us do work easier! They are everywhere around us.

### Types of Simple Machines:
- **Lever**: Like a seesaw that helps lift heavy things
- **Wheel**: Round things that roll to make moving easier
- **Ramp**: A slope that helps us go up high places

### Fun Activities:
- Find wheels in your house (toys, chairs, bikes)
- Use a spoon as a lever to open a container
- Roll a ball up a ramp (books stacked up)

### Safety First:
- Always ask an adult to help
- Be gentle with tools and toys
- Keep fingers away from moving parts

Remember: Engineers build things to help people!
        """.strip()
    
    def _create_elementary_engineering(self, content: ContentItem) -> str:
        """Create engineering content for ages 6-11."""
        return """
## Engineering and Simple Machines

### What is Engineering?
Engineering is using science and math to solve problems and build useful things!

### The Six Simple Machines:
1. **Lever** - A bar that turns on a point (fulcrum)
2. **Wheel and Axle** - A round part that turns on a center rod
3. **Pulley** - A wheel with a rope to lift things
4. **Inclined Plane** - A ramp or slope
5. **Wedge** - Like a triangle that splits or cuts
6. **Screw** - An inclined plane wrapped around a rod

### Engineering Design Process:
1. Ask: What problem needs solving?
2. Imagine: Think of solutions
3. Plan: Draw your idea
4. Create: Build a prototype
5. Test: See if it works
6. Improve: Make it better

### Build Your Own:
- Make a lever with a ruler and a block
- Build a ramp with books and cardboard
- Create a pulley with string and a wheel

### Real Engineers:
Engineers design cars, bridges, robots, and even toys!
        """.strip()
    
    def _create_middle_school_engineering(self, content: ContentItem) -> str:
        """Create engineering content for ages 12-14."""
        return f"""
## Mechanical Engineering Principles

### Engineering Fundamentals:
Mechanical engineering applies physics principles to design and build machines and systems.

### Key Concepts:
- **Force and Motion**: Understanding how forces create movement
- **Energy Transfer**: How energy moves through mechanical systems
- **Materials Science**: Choosing the right materials for the job
- **Design Optimization**: Making systems efficient and reliable

### Engineering Design Challenge:
Design a machine that can:
- Solve a specific problem
- Be built with available materials
- Meet safety and performance requirements
- Be cost-effective to manufacture

### Career Connections:
Mechanical engineers work in:
- Automotive industry (cars, trucks)
- Aerospace (planes, rockets)
- Manufacturing (factories, production)
- Robotics and automation

### Next Steps:
- Learn basic programming for robotics
- Study physics and mathematics
- Practice problem-solving skills
- Explore engineering competitions
        """.strip()
    
    def _create_high_school_engineering(self, content: ContentItem) -> str:
        """Create engineering content for ages 15-17."""
        return content.content  # Keep detailed technical content
    
    def _assess_technical_accuracy(self, content: ContentItem) -> float:
        """Assess technical accuracy of engineering content."""
        # Check for engineering terminology and concepts
        technical_terms = sum(1 for term in self.mechanical_concepts if term in content.content.lower())
        return min(1.0, technical_terms * 0.1 + 0.5)
    
    def _assess_safety_considerations(self, content: ContentItem) -> float:
        """Assess safety considerations in engineering content."""
        safety_keywords = ["safety", "caution", "warning", "protection", "secure"]
        safety_mentions = sum(content.content.lower().count(keyword) for keyword in safety_keywords)
        return min(1.0, safety_mentions * 0.2)
    
    def _assess_practical_applicability(self, content: ContentItem) -> float:
        """Assess practical applicability of engineering content."""
        practical_keywords = ["application", "use", "example", "real-world", "industry"]
        practical_mentions = sum(content.content.lower().count(keyword) for keyword in practical_keywords)
        return min(1.0, practical_mentions * 0.15 + 0.3)
    
    def _assess_age_appropriateness_engineering(self, content: ContentItem) -> float:
        """Assess age appropriateness for engineering content."""
        complex_terms = ["thermodynamics", "finite_element", "computational", "differential"]
        complex_count = sum(1 for term in complex_terms if term in content.content.lower())
        
        if AgeGroup.EARLY_YEARS in content.age_groups and complex_count > 0:
            return 0.2
        elif AgeGroup.ELEMENTARY in content.age_groups and complex_count > 2:
            return 0.5
        
        return 0.9
    
    def _identify_engineering_prerequisites(self, content: str) -> List[str]:
        """Identify prerequisites for engineering content."""
        prerequisites = []
        
        if "force" in content.lower():
            prerequisites.extend(["physics_basics", "newton_laws"])
        if "material" in content.lower():
            prerequisites.extend(["properties_of_matter", "strength_concepts"])
        if "design" in content.lower():
            prerequisites.extend(["problem_solving", "measurement", "geometry"])
        
        return list(set(prerequisites))
    
    def _find_engineering_related_concepts(self, content: str) -> List[str]:
        """Find related engineering concepts."""
        related = []
        
        if "machine" in content.lower():
            related.extend(["automation", "manufacturing", "maintenance"])
        if "design" in content.lower():
            related.extend(["innovation", "optimization", "prototyping"])
        if "robot" in content.lower():
            related.extend(["programming", "sensors", "artificial_intelligence"])
        
        return list(set(related))
    
    def _adapt_engineering_prerequisites(self, prerequisites: List[str], age: AgeGroup) -> List[str]:
        """Adapt prerequisites for age group."""
        if age == AgeGroup.EARLY_YEARS:
            return ["basic_shapes", "cause_and_effect"]
        elif age == AgeGroup.ELEMENTARY:
            return ["simple_machines", "measurement", "safety_rules"]
        else:
            return prerequisites
    
    def _adapt_multimedia_for_age(self, assets: List[str], age: AgeGroup) -> List[str]:
        """Adapt multimedia assets for age group."""
        if age == AgeGroup.EARLY_YEARS:
            return ["simple_pictures", "videos", "interactive_games"]
        elif age == AgeGroup.ELEMENTARY:
            return ["diagrams", "animations", "hands_on_activities"]
        else:
            return assets


class SoftwareEngineeringAgent(BaseAgent):
    """Specialist in programming, algorithms, and software systems."""
    
    def __init__(self):
        super().__init__(
            agent_id="software_engineer_001",
            role=AgentRole.ENGINEER,
            domains=["software_engineering", "computer_science", "programming", "algorithms"],
            specializations=["web_development", "mobile_apps", "artificial_intelligence", "cybersecurity"]
        )
        
        self.programming_concepts = [
            "algorithm", "data_structure", "function", "variable", "loop", "condition",
            "object", "class", "inheritance", "recursion", "database", "api"
        ]
        
        self.programming_languages = [
            "python", "javascript", "java", "c++", "html", "css", "sql", "scratch"
        ]
    
    async def analyze_content(self, source_data: Dict[str, Any]) -> ContentItem:
        """Analyze software engineering content with focus on practical coding."""
        title = source_data.get("title", "Untitled Software Concept")
        content = source_data.get("content", "")
        
        # Identify programming concepts and languages
        identified_concepts = [c for c in self.programming_concepts if c.lower() in content.lower()]
        identified_languages = [l for l in self.programming_languages if l.lower() in content.lower()]
        
        # Structure software content
        structured_content = await self._structure_software_content(
            content, identified_concepts, identified_languages
        )
        
        return ContentItem(
            id=self.generate_content_id(title, "software_engineering"),
            title=title,
            content=structured_content,
            content_type=ContentType.APPLICATION,
            domain="software_engineering",
            age_groups=[AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
            sources=source_data.get("sources", []),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1,
            tags=identified_concepts + identified_languages + ["programming", "software"],
            prerequisites=self._identify_software_prerequisites(content),
            related_concepts=self._find_software_related_concepts(content),
            multimedia_assets=["code_examples", "interactive_demos", "video_tutorials"]
        )
    
    async def _structure_software_content(self, content: str, concepts: List[str], 
                                        languages: List[str]) -> str:
        """Structure software content with code examples and practical applications."""
        return f"""
## Software Engineering Overview
{content[:250]}...

## Key Programming Concepts
{chr(10).join(f'- **{concept.title()}**: Essential building block of programming' for concept in concepts[:5])}

## Programming Languages
{chr(10).join(f'- {lang.title()}' for lang in languages)}

## Practical Applications
Software engineering creates:
- Mobile apps and websites
- Video games and entertainment
- Business and productivity tools
- Scientific and research software

## Problem-Solving Process
1. **Understand** the problem
2. **Plan** the solution (algorithm)
3. **Code** the implementation
4. **Test** and debug
5. **Deploy** and maintain

## Getting Started
- Start with visual programming (Scratch)
- Learn fundamental concepts
- Practice with small projects
- Join coding communities

## Career Opportunities
- Software Developer
- Web Designer
- Game Developer
- Data Scientist
- Cybersecurity Specialist
        """.strip()
    
    async def review_content(self, content: ContentItem) -> ReviewFeedback:
        """Review software content for technical accuracy and age appropriateness."""
        code_accuracy = self._assess_code_accuracy(content)
        concept_clarity = self._assess_concept_clarity(content)
        practical_relevance = self._assess_practical_relevance(content)
        
        suggestions = []
        if "algorithm" in content.content.lower() and "example" not in content.content.lower():
            suggestions.append("Include concrete examples of algorithms")
        if "programming" in content.content.lower() and "debugging" not in content.content.lower():
            suggestions.append("Mention debugging as an essential programming skill")
        
        return ReviewFeedback(
            agent_id=self.agent_id,
            agent_role=self.role,
            content_id=content.id,
            accuracy_score=code_accuracy,
            clarity_score=concept_clarity,
            age_appropriateness_score=self._assess_software_age_appropriateness(content),
            completeness_score=practical_relevance,
            suggestions=suggestions,
            approved=code_accuracy > 0.8 and concept_clarity > 0.7,
            timestamp=datetime.now()
        )
    
    async def adapt_for_age_group(self, content: ContentItem, target_age: AgeGroup) -> ContentItem:
        """Adapt software content for different age groups with appropriate complexity."""
        if target_age == AgeGroup.EARLY_YEARS:
            adapted_content = self._create_early_years_software(content)
        elif target_age == AgeGroup.ELEMENTARY:
            adapted_content = self._create_elementary_software(content)
        elif target_age == AgeGroup.MIDDLE_SCHOOL:
            adapted_content = self._create_middle_school_software(content)
        elif target_age == AgeGroup.HIGH_SCHOOL:
            adapted_content = self._create_high_school_software(content)
        else:
            adapted_content = content.content
        
        return ContentItem(
            id=f"{content.id}_{target_age.value}",
            title=content.title,
            content=adapted_content,
            content_type=content.content_type,
            domain=content.domain,
            age_groups=[target_age],
            sources=content.sources,
            created_at=content.created_at,
            updated_at=datetime.now(),
            version=content.version,
            tags=content.tags,
            prerequisites=self._adapt_software_prerequisites(content.prerequisites, target_age),
            related_concepts=content.related_concepts
        )
    
    def _create_early_years_software(self, content: ContentItem) -> str:
        """Create software content for ages 1-5."""
        return """
## Computers Help Us!

### What do Computers Do?
Computers are special machines that follow instructions to help us!

### Computer Games:
- Educational apps that teach letters and numbers
- Drawing programs to make colorful pictures
- Simple puzzle games

### How Computers Think:
- They follow step-by-step instructions (like a recipe!)
- They remember things we tell them
- They can show us pictures and play sounds

### Fun with Technology:
- Take pictures with a tablet
- Listen to music and stories
- Video call with family far away

### Being Safe:
- Always use computers with grown-ups
- Be kind to others online
- Take breaks to play outside too!

Computers are tools that help us learn and have fun!
        """.strip()
    
    def _create_elementary_software(self, content: ContentItem) -> str:
        """Create software content for ages 6-11."""
        return """
## Introduction to Programming

### What is Programming?
Programming is giving instructions to computers to make them do useful things!

### Basic Programming Concepts:
- **Algorithm**: Step-by-step instructions (like a recipe)
- **Input**: Information we give to the computer
- **Output**: What the computer shows or does
- **Loop**: Repeating the same steps many times

### Visual Programming with Scratch:
- Drag and drop blocks to create programs
- Make characters move, talk, and interact
- Create simple games and animations
- No typing needed - just connect blocks!

### Real Programming Examples:
- Apps on phones and tablets
- Video games you play
- Websites you visit
- Smart home devices

### Programming Projects:
- Make a digital greeting card
- Create an interactive story
- Build a simple quiz game
- Animate your favorite character

### Why Learn Programming?
- Solve problems creatively
- Build things that help others
- Express your ideas through technology
- Prepare for future careers

Programming is like learning a new language to talk to computers!
        """.strip()
    
    def _create_middle_school_software(self, content: ContentItem) -> str:
        """Create software content for ages 12-14."""
        return content.content  # Keep most content but add more interactive elements
    
    def _create_high_school_software(self, content: ContentItem) -> str:
        """Create software content for ages 15-17."""
        return content.content  # Keep technical content with career focus
    
    def _assess_code_accuracy(self, content: ContentItem) -> float:
        """Assess accuracy of code-related content."""
        programming_terms = sum(1 for term in self.programming_concepts if term in content.content.lower())
        return min(1.0, programming_terms * 0.08 + 0.6)
    
    def _assess_concept_clarity(self, content: ContentItem) -> float:
        """Assess clarity of programming concepts."""
        explanation_keywords = ["example", "step", "instruction", "process"]
        clarity_score = sum(content.content.lower().count(keyword) for keyword in explanation_keywords)
        return min(1.0, clarity_score * 0.1 + 0.5)
    
    def _assess_practical_relevance(self, content: ContentItem) -> float:
        """Assess practical relevance of software content."""
        practical_keywords = ["project", "build", "create", "develop", "app"]
        relevance_score = sum(content.content.lower().count(keyword) for keyword in practical_keywords)
        return min(1.0, relevance_score * 0.12 + 0.4)
    
    def _assess_software_age_appropriateness(self, content: ContentItem) -> float:
        """Assess age appropriateness for software content."""
        advanced_terms = ["compiler", "runtime", "polymorphism", "encapsulation"]
        advanced_count = sum(1 for term in advanced_terms if term in content.content.lower())
        
        if AgeGroup.EARLY_YEARS in content.age_groups and advanced_count > 0:
            return 0.1
        elif AgeGroup.ELEMENTARY in content.age_groups and advanced_count > 1:
            return 0.4
        
        return 0.9
    
    def _identify_software_prerequisites(self, content: str) -> List[str]:
        """Identify prerequisites for software content."""
        prerequisites = []
        
        if "programming" in content.lower():
            prerequisites.extend(["basic_computer_skills", "logical_thinking"])
        if "algorithm" in content.lower():
            prerequisites.extend(["problem_solving", "sequential_thinking"])
        if "data" in content.lower():
            prerequisites.extend(["organization_concepts", "categorization"])
        
        return list(set(prerequisites))
    
    def _find_software_related_concepts(self, content: str) -> List[str]:
        """Find related software concepts."""
        related = []
        
        if "web" in content.lower():
            related.extend(["html", "css", "javascript", "internet"])
        if "app" in content.lower():
            related.extend(["mobile_development", "user_interface", "user_experience"])
        if "game" in content.lower():
            related.extend(["graphics", "animation", "sound", "interaction"])
        
        return list(set(related))
    
    def _adapt_software_prerequisites(self, prerequisites: List[str], age: AgeGroup) -> List[str]:
        """Adapt software prerequisites for age group."""
        if age == AgeGroup.EARLY_YEARS:
            return ["basic_interaction", "following_instructions"]
        elif age == AgeGroup.ELEMENTARY:
            return ["computer_basics", "reading_skills", "logical_thinking"]
        else:
            return prerequisites


# Additional engineering agents (Electrical, Civil) would follow similar patterns
class ElectricalEngineeringAgent(BaseAgent):
    """Specialist in electronics, circuits, and power systems."""
    
    def __init__(self):
        super().__init__(
            agent_id="elec_engineer_001",
            role=AgentRole.ENGINEER,
            domains=["electrical_engineering", "electronics", "circuits", "power_systems"],
            specializations=["renewable_energy", "embedded_systems", "signal_processing"]
        )
    
    # Implementation similar to other engineering agents...


class CivilEngineeringAgent(BaseAgent):
    """Specialist in construction, infrastructure, and structural design."""
    
    def __init__(self):
        super().__init__(
            agent_id="civil_engineer_001",
            role=AgentRole.ENGINEER,
            domains=["civil_engineering", "construction", "infrastructure", "structural_design"],
            specializations=["transportation", "environmental_engineering", "urban_planning"]
        )
    
    # Implementation similar to other engineering agents...