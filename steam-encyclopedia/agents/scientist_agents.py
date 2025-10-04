"""
Scientist Agents for STEAM Encyclopedia Editorial Board
Specialized in research validation, scientific accuracy, and cutting-edge discoveries
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import re

from .base_agent import BaseAgent, AgentRole, ContentItem, ContentType, AgeGroup, ReviewFeedback


class BiologyAgent(BaseAgent):
    """Specialist in life sciences, ecology, genetics, and health."""
    
    def __init__(self):
        super().__init__(
            agent_id="bio_scientist_001",
            role=AgentRole.SCIENTIST,
            domains=["biology", "life_sciences", "ecology", "genetics", "health", "medicine"],
            specializations=["molecular_biology", "evolution", "microbiology", "biotechnology"]
        )
        
        # Biology-specific knowledge patterns
        self.taxonomy_patterns = [
            r'\b[A-Z][a-z]+ [a-z]+\b',  # Binomial nomenclature
            r'\b(?:species|genus|family|order|class|phylum|kingdom)\b'
        ]
        
        self.biological_processes = [
            "photosynthesis", "cellular_respiration", "mitosis", "meiosis", "transcription",
            "translation", "metabolism", "homeostasis", "evolution", "natural_selection"
        ]
    
    async def analyze_content(self, source_data: Dict[str, Any]) -> ContentItem:
        """Analyze biological content and create structured encyclopedia entry."""
        title = source_data.get("title", "Untitled Biological Concept")
        content = source_data.get("content", "")
        
        # Extract biological concepts
        identified_processes = [p for p in self.biological_processes if p.lower() in content.lower()]
        
        # Determine content type
        content_type = ContentType.THEORY
        if any(word in content.lower() for word in ["experiment", "study", "research"]):
            content_type = ContentType.DISCOVERY
        elif any(word in content.lower() for word in ["application", "treatment", "therapy"]):
            content_type = ContentType.APPLICATION
        
        # Generate age-appropriate versions
        age_groups = [AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED]
        
        # Create structured content
        structured_content = await self._structure_biological_content(content, identified_processes)
        
        return ContentItem(
            id=self.generate_content_id(title, "biology"),
            title=title,
            content=structured_content,
            content_type=content_type,
            domain="biology",
            age_groups=age_groups,
            sources=source_data.get("sources", []),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1,
            tags=identified_processes + ["biology", "life_sciences"],
            prerequisites=self._identify_prerequisites(content),
            related_concepts=self._find_related_concepts(content)
        )
    
    async def _structure_biological_content(self, content: str, processes: List[str]) -> str:
        """Structure biological content with proper scientific formatting."""
        sections = {
            "overview": "",
            "mechanism": "",
            "significance": "",
            "examples": "",
            "current_research": ""
        }
        
        # Basic content structuring (would be more sophisticated in real implementation)
        sections["overview"] = content[:200] + "..." if len(content) > 200 else content
        sections["significance"] = f"This biological concept involves: {', '.join(processes)}"
        
        structured = f"""
## Overview
{sections['overview']}

## Biological Significance
{sections['significance']}

## Key Processes
{chr(10).join(f'- {process.title()}' for process in processes)}

## Related Research
{sections['current_research'] or 'Current research is ongoing in this area.'}
        """.strip()
        
        return structured
    
    async def review_content(self, content: ContentItem) -> ReviewFeedback:
        """Review content for biological accuracy and completeness."""
        accuracy_score = 0.9  # Would use sophisticated fact-checking
        clarity_score = 0.85
        age_appropriateness_score = self._assess_age_appropriateness(content)
        completeness_score = self._assess_biological_completeness(content)
        
        suggestions = []
        if "DNA" in content.content and "chromosome" not in content.content:
            suggestions.append("Consider adding information about chromosomes for context")
        if "evolution" in content.content.lower() and "natural selection" not in content.content.lower():
            suggestions.append("Include natural selection mechanism for evolutionary concepts")
        
        return ReviewFeedback(
            agent_id=self.agent_id,
            agent_role=self.role,
            content_id=content.id,
            accuracy_score=accuracy_score,
            clarity_score=clarity_score,
            age_appropriateness_score=age_appropriateness_score,
            completeness_score=completeness_score,
            suggestions=suggestions,
            approved=accuracy_score > 0.8 and completeness_score > 0.7,
            timestamp=datetime.now()
        )
    
    async def adapt_for_age_group(self, content: ContentItem, target_age: AgeGroup) -> ContentItem:
        """Adapt biological content for specific age group."""
        adapted_content = content.content
        
        if target_age == AgeGroup.EARLY_YEARS:
            adapted_content = self._simplify_for_early_years(content.content)
        elif target_age == AgeGroup.ELEMENTARY:
            adapted_content = self._adapt_for_elementary(content.content)
        elif target_age == AgeGroup.MIDDLE_SCHOOL:
            adapted_content = self._adapt_for_middle_school(content.content)
        elif target_age == AgeGroup.HIGH_SCHOOL:
            adapted_content = self._adapt_for_high_school(content.content)
        # HIGHER_ED keeps original content
        
        adapted = ContentItem(
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
            prerequisites=self._adapt_prerequisites_for_age(content.prerequisites, target_age),
            related_concepts=content.related_concepts
        )
        
        return adapted
    
    def _identify_prerequisites(self, content: str) -> List[str]:
        """Identify prerequisite concepts for biological content."""
        prerequisites = []
        
        if "DNA" in content:
            prerequisites.extend(["cell", "nucleus", "chromosome"])
        if "photosynthesis" in content.lower():
            prerequisites.extend(["plant", "chloroplast", "sunlight", "carbon_dioxide"])
        if "evolution" in content.lower():
            prerequisites.extend(["species", "adaptation", "heredity"])
        
        return list(set(prerequisites))
    
    def _find_related_concepts(self, content: str) -> List[str]:
        """Find related biological concepts."""
        related = []
        
        if "cell" in content.lower():
            related.extend(["tissue", "organ", "organism"])
        if "genetics" in content.lower():
            related.extend(["heredity", "mutation", "gene_expression"])
        if "ecology" in content.lower():
            related.extend(["ecosystem", "biodiversity", "food_chain"])
        
        return list(set(related))
    
    def _assess_age_appropriateness(self, content: ContentItem) -> float:
        """Assess if content is appropriate for target age groups."""
        # Check for complex terminology
        complex_terms = ["transcription", "translation", "cytoplasm", "mitochondria"]
        complex_count = sum(1 for term in complex_terms if term in content.content.lower())
        
        if AgeGroup.EARLY_YEARS in content.age_groups and complex_count > 0:
            return 0.3
        elif AgeGroup.ELEMENTARY in content.age_groups and complex_count > 3:
            return 0.6
        
        return 0.9
    
    def _assess_biological_completeness(self, content: ContentItem) -> float:
        """Assess completeness of biological content."""
        required_sections = ["overview", "significance", "mechanism"]
        present_sections = sum(1 for section in required_sections 
                             if section in content.content.lower())
        
        return present_sections / len(required_sections)
    
    def _simplify_for_early_years(self, content: str) -> str:
        """Simplify content for ages 1-5."""
        return """
## What is this?
This is about living things! Living things grow, eat, and move.

## Fun Facts
- All living things need food and water
- Plants make their own food from sunlight
- Animals need to eat other living things

## Let's Explore!
Look around you - what living things can you see?
        """.strip()
    
    def _adapt_for_elementary(self, content: str) -> str:
        """Adapt content for ages 6-11."""
        return f"""
## Introduction
{content[:150]}...

## Key Ideas
- Living things are made of tiny parts called cells
- Plants and animals are different types of living things
- All living things need energy to survive

## Simple Experiment
Try growing a plant from a seed and watch how it changes!
        """.strip()
    
    def _adapt_for_middle_school(self, content: str) -> str:
        """Adapt content for ages 12-14."""
        return content  # Keep most original content but add age-appropriate examples
    
    def _adapt_for_high_school(self, content: str) -> str:
        """Adapt content for ages 15-17."""
        return content  # Keep original content, maybe add more detail
    
    def _adapt_prerequisites_for_age(self, prerequisites: List[str], age: AgeGroup) -> List[str]:
        """Adapt prerequisites based on age group."""
        if age == AgeGroup.EARLY_YEARS:
            return ["basic_observation"]
        elif age == AgeGroup.ELEMENTARY:
            return ["living_vs_nonliving", "basic_needs_of_life"]
        else:
            return prerequisites


class ChemistryAgent(BaseAgent):
    """Specialist in molecular science, reactions, and materials."""
    
    def __init__(self):
        super().__init__(
            agent_id="chem_scientist_001",
            role=AgentRole.SCIENTIST,
            domains=["chemistry", "materials_science", "biochemistry", "physical_chemistry"],
            specializations=["organic_chemistry", "inorganic_chemistry", "analytical_chemistry"]
        )
        
        self.chemical_formulas = re.compile(r'[A-Z][a-z]?[0-9]*(?:[A-Z][a-z]?[0-9]*)*')
        self.chemical_processes = [
            "oxidation", "reduction", "synthesis", "decomposition", "precipitation",
            "crystallization", "catalysis", "polymerization", "fermentation"
        ]
    
    async def analyze_content(self, source_data: Dict[str, Any]) -> ContentItem:
        """Analyze chemistry content and create structured encyclopedia entry."""
        title = source_data.get("title", "Untitled Chemistry Concept")
        content = source_data.get("content", "")
        
        # Extract chemical formulas and processes
        formulas = self.chemical_formulas.findall(content)
        processes = [p for p in self.chemical_processes if p.lower() in content.lower()]
        
        # Structure chemical content
        structured_content = await self._structure_chemical_content(content, formulas, processes)
        
        return ContentItem(
            id=self.generate_content_id(title, "chemistry"),
            title=title,
            content=structured_content,
            content_type=ContentType.THEORY,
            domain="chemistry",
            age_groups=[AgeGroup.ELEMENTARY, AgeGroup.MIDDLE_SCHOOL, AgeGroup.HIGH_SCHOOL, AgeGroup.HIGHER_ED],
            sources=source_data.get("sources", []),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1,
            tags=processes + formulas + ["chemistry", "molecules"],
            prerequisites=self._identify_chemistry_prerequisites(content),
            related_concepts=self._find_chemistry_related_concepts(content)
        )
    
    async def _structure_chemical_content(self, content: str, formulas: List[str], processes: List[str]) -> str:
        """Structure chemistry content with proper scientific formatting."""
        return f"""
## Chemical Overview
{content[:200]}...

## Key Chemical Formulas
{chr(10).join(f'- {formula}' for formula in formulas[:5])}

## Important Processes
{chr(10).join(f'- {process.title()}' for process in processes)}

## Safety Considerations
Always follow proper safety procedures when working with chemicals.

## Real-World Applications
This chemistry concept has applications in industry, medicine, and daily life.
        """.strip()
    
    async def review_content(self, content: ContentItem) -> ReviewFeedback:
        """Review chemistry content for accuracy and safety."""
        # Chemistry requires high accuracy for safety reasons
        accuracy_score = 0.95
        safety_mentions = content.content.lower().count("safety")
        safety_score = min(1.0, safety_mentions * 0.3)
        
        suggestions = []
        if safety_score < 0.5:
            suggestions.append("Add safety warnings for chemical procedures")
        if "reaction" in content.content.lower() and "equation" not in content.content.lower():
            suggestions.append("Include balanced chemical equations for reactions")
        
        return ReviewFeedback(
            agent_id=self.agent_id,
            agent_role=self.role,
            content_id=content.id,
            accuracy_score=accuracy_score,
            clarity_score=0.88,
            age_appropriateness_score=0.85,
            completeness_score=0.90,
            suggestions=suggestions,
            approved=accuracy_score > 0.9 and safety_score > 0.3,
            timestamp=datetime.now()
        )
    
    async def adapt_for_age_group(self, content: ContentItem, target_age: AgeGroup) -> ContentItem:
        """Adapt chemistry content with age-appropriate safety considerations."""
        # Similar structure to BiologyAgent but with chemistry-specific adaptations
        # Implementation would include safety-first approach for younger ages
        adapted_content = content.content
        
        if target_age in [AgeGroup.EARLY_YEARS, AgeGroup.ELEMENTARY]:
            adapted_content = """
## Safe Chemistry Fun!
Chemistry is all around us! It's how we cook food, clean things, and even how our bodies work.

## Safe Experiments
- Mix baking soda and vinegar (with an adult)
- Watch how ice melts into water
- See how salt dissolves in water

## Important Rule
NEVER touch or taste chemicals without an adult helping you!
            """.strip()
        
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
            tags=content.tags + ["safety"],
            prerequisites=self._adapt_chemistry_prerequisites_for_age(content.prerequisites, target_age),
            related_concepts=content.related_concepts
        )
    
    def _identify_chemistry_prerequisites(self, content: str) -> List[str]:
        """Identify chemistry prerequisites."""
        prerequisites = []
        
        if "molecule" in content.lower():
            prerequisites.extend(["atom", "element", "periodic_table"])
        if "reaction" in content.lower():
            prerequisites.extend(["reactant", "product", "chemical_equation"])
        if "pH" in content:
            prerequisites.extend(["acid", "base", "neutral"])
        
        return list(set(prerequisites))
    
    def _find_chemistry_related_concepts(self, content: str) -> List[str]:
        """Find related chemistry concepts."""
        related = []
        
        if "organic" in content.lower():
            related.extend(["carbon", "hydrocarbon", "functional_group"])
        if "metal" in content.lower():
            related.extend(["periodic_table", "electron", "ionic_bond"])
        if "solution" in content.lower():
            related.extend(["solvent", "solute", "concentration"])
        
        return list(set(related))
    
    def _adapt_chemistry_prerequisites_for_age(self, prerequisites: List[str], age: AgeGroup) -> List[str]:
        """Adapt chemistry prerequisites for age group."""
        if age == AgeGroup.EARLY_YEARS:
            return ["adult_supervision", "safety_first"]
        elif age == AgeGroup.ELEMENTARY:
            return ["basic_matter_states", "safety_rules"]
        else:
            return prerequisites


# Additional scientist agents would follow similar patterns
class PhysicsAgent(BaseAgent):
    """Specialist in mechanics, quantum physics, energy, and space."""
    
    def __init__(self):
        super().__init__(
            agent_id="physics_scientist_001",
            role=AgentRole.SCIENTIST,
            domains=["physics", "mechanics", "thermodynamics", "electromagnetism", "quantum_physics"],
            specializations=["theoretical_physics", "astrophysics", "particle_physics"]
        )
    
    # Implementation similar to other scientist agents...
    async def analyze_content(self, source_data: Dict[str, Any]) -> ContentItem:
        # Physics-specific analysis
        pass
    
    async def review_content(self, content: ContentItem) -> ReviewFeedback:
        # Physics accuracy review
        pass
    
    async def adapt_for_age_group(self, content: ContentItem, target_age: AgeGroup) -> ContentItem:
        # Physics age adaptation
        pass


class EarthSciencesAgent(BaseAgent):
    """Specialist in geology, climate, and environmental science."""
    
    def __init__(self):
        super().__init__(
            agent_id="earth_scientist_001",
            role=AgentRole.SCIENTIST,
            domains=["geology", "meteorology", "oceanography", "environmental_science"],
            specializations=["climate_science", "seismology", "ecology"]
        )
    
    # Implementation similar to other scientist agents...
    async def analyze_content(self, source_data: Dict[str, Any]) -> ContentItem:
        pass
    
    async def review_content(self, content: ContentItem) -> ReviewFeedback:
        pass
    
    async def adapt_for_age_group(self, content: ContentItem, target_age: AgeGroup) -> ContentItem:
        pass